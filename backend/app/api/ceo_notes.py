"""
CEO Quick Notes API
CEO快记功能的API接口
提供快速记录、AI自动分类、查询功能
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
import json
import os
from app.core.state import get_app_state

router = APIRouter()

# 数据存储路径
NOTES_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
NOTES_FILE = os.path.join(NOTES_DATA_DIR, "ceo_notes.json")


class CreateNoteRequest(BaseModel):
    """创建快记请求"""
    content: str
    user_id: str = "ceo_default"


class NoteResponse(BaseModel):
    """快记响应"""
    id: str
    content: str
    category: str  # 分类：work_preference, company_background, business_decision, daily_thought, other
    created_at: str
    user_id: str
    ai_summary: Optional[str] = None  # AI生成的摘要


def _load_notes() -> List[Dict]:
    """加载快记数据"""
    if not os.path.exists(NOTES_FILE):
        return []

    try:
        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️  加载快记失败: {e}")
        return []


def _save_notes(notes: List[Dict]):
    """保存快记数据"""
    os.makedirs(NOTES_DATA_DIR, exist_ok=True)

    try:
        with open(NOTES_FILE, "w", encoding="utf-8") as f:
            json.dump(notes, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️  保存快记失败: {e}")
        raise HTTPException(status_code=500, detail=f"保存快记失败: {str(e)}")


async def _classify_note_with_ai(content: str) -> tuple[str, str]:
    """
    使用AI自动分类快记内容

    返回：(分类, AI摘要)
    """
    app_state = get_app_state()

    if not app_state.llm_client:
        # 如果LLM不可用，返回默认分类
        return "other", content[:50] + "..." if len(content) > 50 else content

    # 构建分类提示词
    prompt = f"""你是CEO快记智能分类助手，需要将CEO的快速记录分类并生成简洁摘要。

**快记内容：**
{content}

**分类规则：**
1. work_preference - 工作偏好、决策风格、管理习惯
2. company_background - 公司信息、团队情况、业务模式
3. business_decision - 战略决策、业务计划、重要事项
4. daily_thought - 日常想法、灵感、临时备忘
5. other - 其他无法分类的内容

**输出格式（JSON）：**
{{
    "category": "分类名称（必须是上述5种之一）",
    "summary": "10-20字的简洁摘要"
}}

请直接输出JSON，不要有其他内容。"""

    try:
        # 调用LLM
        messages = [{"role": "user", "content": prompt}]
        response = await app_state.llm_client.async_chat_completion(
            messages=messages,
            temperature=0.3,
            max_tokens=150
        )

        if response.get("error"):
            print(f"⚠️  AI分类失败: {response['error']}")
            return "other", content[:50] + "..." if len(content) > 50 else content

        # 解析LLM响应
        content_text = response.get("content", "")

        # 提取JSON（处理可能的markdown代码块）
        if "```json" in content_text:
            content_text = content_text.split("```json")[1].split("```")[0].strip()
        elif "```" in content_text:
            content_text = content_text.split("```")[1].split("```")[0].strip()

        result = json.loads(content_text)
        category = result.get("category", "other")
        summary = result.get("summary", content[:50] + "...")

        # 验证分类有效性
        valid_categories = ["work_preference", "company_background", "business_decision", "daily_thought", "other"]
        if category not in valid_categories:
            category = "other"

        return category, summary

    except Exception as e:
        print(f"⚠️  AI分类异常: {e}")
        return "other", content[:50] + "..." if len(content) > 50 else content


@router.post("/create", response_model=NoteResponse)
async def create_note(req: CreateNoteRequest):
    """
    创建CEO快记

    - 使用AI自动分类
    - 保存到JSON文件
    - 保存到企业级记忆（Mem0）
    """
    app_state = get_app_state()

    # 1. 使用AI分类
    print(f"📝 创建快记: {req.content[:50]}...")
    category, summary = await _classify_note_with_ai(req.content)
    print(f"   分类: {category}, 摘要: {summary}")

    # 2. 生成快记ID
    note_id = f"note_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{req.user_id}"

    # 3. 创建快记对象
    note = {
        "id": note_id,
        "content": req.content,
        "category": category,
        "ai_summary": summary,
        "created_at": datetime.now().isoformat(),
        "user_id": req.user_id
    }

    # 4. 保存到JSON文件
    notes = _load_notes()
    notes.append(note)
    _save_notes(notes)

    # 5. 保存到企业级记忆（Mem0）
    if app_state.memory_manager:
        try:
            memory_content = f"[CEO快记-{category}] {req.content}"
            app_state.memory_manager.add_memory(
                content=memory_content,
                memory_type="global",
                source="ceo_notes",
                metadata={
                    "level": "enterprise",
                    "domain": "enterprise",
                    "category": f"ceo_note_{category}",
                    "note_id": note_id,
                    "summary": summary,
                    "timestamp": note["created_at"],
                    "scope": {"userId": req.user_id}
                },
                user_id="system"
            )
            print(f"   ✅ 已保存到企业记忆")
        except Exception as e:
            print(f"   ⚠️  保存到Mem0失败: {e}")

    return NoteResponse(**note)


@router.get("/list", response_model=List[NoteResponse])
async def list_notes(
    category: Optional[str] = None,
    user_id: Optional[str] = None,
    limit: int = 50
):
    """
    获取快记列表

    - 支持按分类筛选
    - 支持按用户筛选
    - 默认返回最近50条
    """
    notes = _load_notes()

    # 过滤
    if category:
        notes = [n for n in notes if n.get("category") == category]

    if user_id:
        notes = [n for n in notes if n.get("user_id") == user_id]

    # 按时间倒序
    notes.sort(key=lambda x: x.get("created_at", ""), reverse=True)

    # 限制数量
    notes = notes[:limit]

    return [NoteResponse(**note) for note in notes]


@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(note_id: str):
    """获取单条快记"""
    notes = _load_notes()

    for note in notes:
        if note.get("id") == note_id:
            return NoteResponse(**note)

    raise HTTPException(status_code=404, detail="快记不存在")


@router.delete("/{note_id}")
async def delete_note(note_id: str):
    """删除快记"""
    notes = _load_notes()

    # 查找并删除
    found = False
    new_notes = []
    for note in notes:
        if note.get("id") == note_id:
            found = True
            print(f"🗑️  删除快记: {note_id}")
        else:
            new_notes.append(note)

    if not found:
        raise HTTPException(status_code=404, detail="快记不存在")

    _save_notes(new_notes)

    return {"success": True, "message": "快记已删除"}


@router.get("/stats/summary")
async def get_notes_stats():
    """
    获取快记统计信息

    - 总数
    - 各分类数量
    - 最近记录时间
    """
    notes = _load_notes()

    if not notes:
        return {
            "total": 0,
            "by_category": {},
            "last_note_time": None
        }

    # 统计各分类数量
    category_counts = {}
    for note in notes:
        category = note.get("category", "other")
        category_counts[category] = category_counts.get(category, 0) + 1

    # 最近记录时间
    notes.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    last_note_time = notes[0].get("created_at") if notes else None

    return {
        "total": len(notes),
        "by_category": category_counts,
        "last_note_time": last_note_time
    }
