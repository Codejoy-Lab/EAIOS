"""
S3 Customer Service API
 - Chat (stream) with knowledge base and history points
 - Manage customer history points (customer_service domain)
 - Simple KB endpoints (optional minimal)
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, List, Optional
import json
from datetime import datetime

from app.core.state import get_app_state
from app.core.customer_service_kb import get_cs_kb


router = APIRouter()


class ChatRequest(BaseModel):
    customer_id: str
    message: str
    conversation_history: Optional[List[Dict]] = None


class KBAddRequest(BaseModel):
    category: str
    title: str
    content: str


def _s3_system_prompt(kb_snippets: List[Dict], recent_points: List[str]) -> str:
    kb_text = "\n".join([f"- {k.get('title')}: {k.get('content')[:200]}" for k in kb_snippets]) or "无"
    points_text = "\n".join([f"- {p}" for p in recent_points]) or "无"
    return (
        "你是企业的智能客服。目标：准确、简洁，先解决问题；缺信息时礼貌引导。\n"
        "规则：\n"
        "1) 回答需基于知识库（若命中）并在结尾附'依据：<条目名>'。\n"
        "2) 若识别到客户历史要点（未结项/到期项），先提醒并衔接上下文。\n"
        "3) 订单进度/投诉可调用工具，由系统处理；无法获取时要说明并引导补充信息。\n"
        f"知识库片段：\n{kb_text}\n"
        f"该客户最近要点：\n{points_text}\n"
        "回答使用中文，避免过长。"
    )


def _format_point(now: datetime, topic: str, key_info: str, resolved: bool) -> str:
    flag = "是" if resolved else "转人工/未结"
    return f"{now.strftime('%Y-%m-%d %H:%M')}｜{topic}｜{key_info}｜{flag}"


@router.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    app_state = get_app_state()
    if not app_state.llm_client or not app_state.memory_manager:
        raise HTTPException(status_code=500, detail="系统未初始化")

    if not req.customer_id or not req.message:
        raise HTTPException(status_code=400, detail="缺少customer_id或message")

    kb = get_cs_kb()
    # 简单检索：按用户问题找3条kb
    kb_hits = kb.search(req.message, top_k=3)

    # 读取最近3条客户要点（customer_service 域）
    recent = app_state.memory_manager.search_memories(
        query=req.customer_id,
        memory_type=None,
        enabled_only=True,
        user_id="system",
        limit=10
    )
    # 仅保留客服域：通过metadata.domain判断（兼容无字段的老数据）
    recent_points = []
    for m in recent:
        md = m.metadata or {}
        if md.get("domain") == "customer_service" and md.get("scope", {}).get("customerId") == req.customer_id:
            recent_points.append(m.content)
    recent_points = recent_points[:3]

    system_prompt = _s3_system_prompt(kb_hits, recent_points)

    messages: List[Dict] = [{"role": "system", "content": system_prompt}]
    if req.conversation_history:
        messages.extend(req.conversation_history)
    messages.append({"role": "user", "content": req.message})

    async def generate_stream():
        full_reply = ""
        try:
            async for chunk in app_state.llm_client.async_chat_completion_stream(messages):
                t = chunk.get("type")
                if t == "content":
                    c = chunk.get("content", "")
                    full_reply += c
                    yield f"data: {json.dumps({'type': 'content', 'content': c}, ensure_ascii=False)}\n\n"
                elif t == "done":
                    break

            yield f"data: {json.dumps({'type': 'done'}, ensure_ascii=False)}\n\n"

            # 简单规则：若回复中包含进度/产品/投诉等关键词，当作关键回合，沉淀一条要点
            topic = "产品" if "产品" in req.message else ("投诉" if "投诉" in req.message else ("进度" if "进度" in req.message else "咨询"))
            key_info = req.message[:40]
            point = _format_point(datetime.now(), topic, key_info, resolved=("已解决" in full_reply))
            app_state.memory_manager.add_memory(
                content=point,
                memory_type="interaction",
                source="s3_customer_service",
                metadata={
                    "domain": "customer_service",
                    "scope": {"customerId": req.customer_id},
                    "category": "customer_point"
                },
                user_id="system"
            )
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(generate_stream(), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"})


@router.post("/kb/add")
async def kb_add(req: KBAddRequest):
    kb = get_cs_kb()
    try:
        entry = kb.add_entry(req.category, req.title, req.content)
        return {"success": True, "entry": entry}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/kb/list")
async def kb_list(category: Optional[str] = None):
    kb = get_cs_kb()
    return {"success": True, "entries": kb.list_entries(category)}


@router.get("/customer/points")
async def get_customer_points(customer_id: str, limit: int = 3):
    app_state = get_app_state()
    if not app_state.memory_manager:
        raise HTTPException(status_code=500, detail="系统未初始化")

    results = app_state.memory_manager.search_memories(
        query=customer_id,
        memory_type=None,
        limit=20,
        enabled_only=True,
        user_id="system"
    )
    points = []
    for m in results:
        md = m.metadata or {}
        if md.get("domain") == "customer_service" and md.get("scope", {}).get("customerId") == customer_id:
            points.append({"id": m.id, "content": m.content, "created_at": m.created_at})
    points = sorted(points, key=lambda x: x["created_at"], reverse=True)[:limit]
    return {"success": True, "points": points}


@router.delete("/customer/{customer_id}/clear")
async def clear_customer_data(customer_id: str):
    """清除指定客户的所有智能客服记忆（初始化账号）"""
    app_state = get_app_state()
    if not app_state.memory_manager:
        raise HTTPException(status_code=500, detail="系统未初始化")
    
    # 查找该客户所有customer_service域的记忆并删除
    results = app_state.memory_manager.search_memories(
        query=customer_id,
        memory_type=None,
        limit=100,
        enabled_only=True,
        user_id="system"
    )
    deleted_count = 0
    for m in results:
        md = m.metadata or {}
        if md.get("domain") == "customer_service" and md.get("scope", {}).get("customerId") == customer_id:
            app_state.memory_manager.delete_memory(m.id, user_id="system")
            deleted_count += 1
    
    return {"success": True, "deleted_count": deleted_count}


