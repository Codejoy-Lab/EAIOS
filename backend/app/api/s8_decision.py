"""
S8 Decision API
S8决策军师场景的API接口
"""
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
import json
import asyncio
from app.core.state import get_app_state
from app.scenarios.s8_decision import S8DecisionAgent
from app.core.meeting_assistant import get_meeting_assistant

router = APIRouter()


async def _should_save_to_memory_llm(user_message: str, ai_reply: str, llm_client) -> tuple[bool, str, str]:
    """
    使用 LLM 智能判断对话是否值得保存到长期记忆
    参考 ChatGPT 的记忆管理机制

    返回：(是否保存, 提取的关键信息摘要, 记忆类型)
    """
    prompt = f"""你是企业记忆管理助手，负责从CEO与决策助手的对话中提取**企业和业务相关**的关键信息。

**重要原则：这是企业大脑，只记录企业经营相关的信息，不记录CEO的个人信息。**

**对话内容：**
CEO问：{user_message}
S8答：{ai_reply}

**应该保存的信息类型：**

1. **工作偏好** (work_preference)
   - CEO的决策风格、管理风格（作为工作方式）
   - 会议习惯、汇报偏好
   - 回答格式偏好（如"我希望看数据驱动的分析"）
   - 注意：只记录**工作相关**的偏好

2. **公司背景** (company_background)
   - 公司名称、业务类型、商业模式
   - 团队规模、组织架构
   - 行业背景、市场定位
   - **不包括CEO个人信息**（姓名、年龄、学历等）

3. **业务决策和计划** (business_decision)
   - 重要的战略决策
   - 具体的行动计划
   - 任务分配和责任人
   - 明确的业务目标和截止时间

4. **业务洞察** (business_insight)
   - 关键业务指标和趋势
   - 风险识别和分析
   - 市场洞察、竞品分析
   - 客户反馈和需求

**明确排除的内容：**
- ❌ CEO的个人信息：姓名、年龄、个人背景、家庭情况
- ❌ 个人兴趣爱好：食物偏好、娱乐方式等
- ❌ 简单问候和闲聊
- ❌ 技术操作问题
- ❌ 临时性、重复性内容

**示例对比：**
- ✅ "公司是50人的跨境电商团队" → 应该保存（company_background）
- ❌ "我叫张三，今年30岁" → 不应该保存（个人信息）
- ✅ "我偏好数据驱动的决策方式" → 应该保存（work_preference）
- ❌ "我喜欢喝咖啡" → 不应该保存（个人喜好）

**请输出JSON格式：**
{{
  "should_save": true/false,
  "memory_type": "work_preference/company_background/business_decision/business_insight/none",
  "reason": "判断理由（简短）",
  "summary": "如果需要保存，提取核心信息（1-2句话，客观陈述）。例如：'公司主营跨境电商业务，团队50人' 或 '计划Q2重点优化转化率'"
}}

只输出JSON，不要其他内容。"""

    try:
        response = await llm_client.async_chat_completion([
            {"role": "user", "content": prompt}
        ])

        if response.get("error"):
            print(f"  ⚠️ LLM判断失败，使用关键词备用方案: {response['error']}")
            return _should_save_to_memory_keyword(user_message, ai_reply), None

        # 解析 LLM 返回
        import json
        content = response.get("content", "{}")

        # 处理 markdown 代码块
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        result = json.loads(content)
        should_save = result.get("should_save", False)
        memory_type = result.get("memory_type", "none")
        reason = result.get("reason", "")
        summary = result.get("summary", "")

        if should_save:
            print(f"  ✓ [LLM判断] 值得保存的信息")
            print(f"    类型: {memory_type}")
            print(f"    理由: {reason}")
            print(f"    摘要: {summary}")
        else:
            print(f"  ✗ [LLM判断] 无需保存")
            print(f"    理由: {reason}")

        return should_save, summary if should_save else None, memory_type

    except Exception as e:
        print(f"  ⚠️ LLM判断异常，使用关键词备用方案: {e}")
        return _should_save_to_memory_keyword(user_message, ai_reply), None, "decision"


def _should_save_to_memory_keyword(user_message: str, ai_reply: str) -> bool:
    """
    关键词匹配备用方案（当LLM不可用时）
    """
    decision_keywords = ["决定", "决策", "计划", "策略", "方案", "建议", "应该", "需要", "必须"]
    data_keywords = ["数据", "指标", "百分比", "%", "增长", "下降", "风险", "目标"]
    action_keywords = ["执行", "安排", "负责", "完成", "截止", "任务", "行动"]

    combined_text = user_message + ai_reply
    has_keywords = any(kw in combined_text for kw in decision_keywords + data_keywords + action_keywords)
    has_substance = len(combined_text) > 20

    greetings = ["你好", "您好", "hi", "hello", "早上好", "晚上好"]
    is_greeting = any(g in user_message.lower() for g in greetings) and len(user_message) < 10

    return has_keywords and has_substance and not is_greeting


class GenerateReportRequest(BaseModel):
    """生成报告请求"""
    input_data: Optional[Dict] = None


class ProcessMeetingNotesRequest(BaseModel):
    """处理会议记录请求"""
    notes: str
    metadata: Optional[Dict] = None


class ConfirmActionsRequest(BaseModel):
    """确认行动请求"""
    actions: List[Dict]  # 包含owner和deadline
    sync_to_board: bool = False


class ChatRequest(BaseModel):
    """对话请求"""
    message: str
    conversation_history: Optional[List[Dict]] = None  # 对话历史
    session_id: Optional[str] = None  # 会话ID，用于Mem0隔离不同会话


@router.post("/generate")
async def generate_report(request: GenerateReportRequest):
    """
    生成CEO晨报

    这是v1.0版本的报告生成
    """
    app_state = get_app_state()

    if not app_state.memory_manager or not app_state.llm_client:
        raise HTTPException(status_code=500, detail="系统未初始化")

    # 创建S8 Agent
    agent = S8DecisionAgent("S8", app_state.memory_manager, app_state.llm_client)

    try:
        report = await agent.generate_report(request.input_data)
        return {
            "success": True,
            "report": report
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/meeting/process")
async def process_meeting_notes(request: ProcessMeetingNotesRequest):
    """
    处理会议记录

    会议助手会：
    1. 提取结构化信息
    2. 写入记忆库
    3. 检测冲突
    4. 触发事件（可能导致报告自动更新）
    """
    app_state = get_app_state()

    if not app_state.memory_manager or not app_state.llm_client:
        raise HTTPException(status_code=500, detail="系统未初始化")

    # 获取会议助手
    meeting_assistant = get_meeting_assistant(app_state.llm_client, app_state.memory_manager)

    try:
        result = await meeting_assistant.process_meeting_notes(
            notes=request.notes,
            metadata=request.metadata
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/actions/confirm")
async def confirm_actions(request: ConfirmActionsRequest):
    """
    确认行动指派（节点4）

    这是关键节点，需要CEO确认责任人和截止期
    """
    app_state = get_app_state()

    if not app_state.memory_manager or not app_state.llm_client:
        raise HTTPException(status_code=500, detail="系统未初始化")

    # 创建S8 Agent
    agent = S8DecisionAgent("S8", app_state.memory_manager, app_state.llm_client)

    try:
        result = await agent.confirm_actions(
            actions_with_assignment=request.actions,
            sync_to_board=request.sync_to_board
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/stream")
async def chat_with_s8_stream(request: ChatRequest):
    """
    与S8决策军师对话 - 流式版本

    使用Server-Sent Events (SSE)实时流式返回，提升用户体验
    """
    print(f"💬 [流式] 收到对话请求: {request.message}")

    app_state = get_app_state()

    if not app_state.memory_manager or not app_state.llm_client:
        print("❌ 系统未初始化")
        raise HTTPException(status_code=500, detail="系统未初始化")

    user_message = request.message
    if not user_message:
        print("❌ 消息为空")
        raise HTTPException(status_code=400, detail="消息不能为空")

    async def generate_stream():
        """生成流式响应"""
        full_reply = ""  # 收集完整回复用于后续记忆判断

        try:
            print("🔍 搜索相关记忆...")
            # 搜索相关记忆（使用 system 确保能搜到所有记忆）
            memories = app_state.memory_manager.search_memories(
                query=user_message,
                user_id="system",
                limit=5
            )
            print(f"✅ 找到 {len(memories)} 条相关记忆")

            # 构建上下文
            context = "\n".join([f"- {m.content}" for m in memories])

            # 构建消息
            messages = [
                {
                    "role": "system",
                    "content": f"""你是S8决策军师，一个帮助CEO做决策的AI助手。

相关企业信息：
{context if context else "暂无相关信息"}

请用自然对话的方式回答用户的问题。回答要简洁、专业，就像一个真实的顾问在跟CEO对话。不要使用过多的表情符号，保持专业但友好的语气。"""
                }
            ]

            # 添加对话历史
            if request.conversation_history:
                print(f"📚 包含 {len(request.conversation_history)} 条历史消息")
                messages.extend(request.conversation_history)

            # 添加当前用户消息
            messages.append({
                "role": "user",
                "content": user_message
            })

            print("🤖 开始流式调用LLM...")

            # 流式调用LLM
            async for chunk in app_state.llm_client.async_chat_completion_stream(messages):
                full_reply += chunk
                # 发送SSE格式数据
                yield f"data: {json.dumps({'type': 'content', 'content': chunk}, ensure_ascii=False)}\n\n"

            print(f"✅ 流式输出完成，总长度: {len(full_reply)}")

            # 发送完成标志
            yield f"data: {json.dumps({'type': 'done'}, ensure_ascii=False)}\n\n"

            # 🧠 异步处理记忆保存（不阻塞流式输出）
            asyncio.create_task(
                _save_memory_async(user_message, full_reply, request.session_id, app_state)
            )

        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"❌ 流式对话失败: {error_detail}")
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # 禁用Nginx缓冲
        }
    )


async def _save_memory_async(user_message: str, ai_reply: str, session_id: Optional[str], app_state):
    """
    异步保存记忆（不阻塞主流程）

    利用 Mem0 的原生能力：
    - Mem0 会自动判断是 Add/Update/Merge
    - 相似内容会自动合并，避免重复
    """
    try:
        print(f"🤔 [后台] 判断对话是否需要保存到长期记忆...")
        should_save, summary, memory_type = await _should_save_to_memory_llm(
            user_message, ai_reply, app_state.llm_client
        )

        if should_save:
            # 使用 "system" 作为 user_id，保证记忆全局可见
            # CEO 的偏好、背景、决策应该在所有场景下都能被召回
            user_id = "system"

            # 使用 LLM 提取的摘要（更精炼，易于去重）
            memory_text = summary if summary else f"CEO问: {user_message}\nS8答: {ai_reply}"

            print(f"💾 [后台] 保存到长期记忆")
            print(f"    类型: {memory_type}")

            # 🔑 关键：Mem0 会自动判断这条记忆是新增还是更新已有记忆
            # 它使用向量相似度来避免重复
            memory_result = app_state.memory_manager.add_memory(
                content=memory_text,
                user_id=user_id,
                metadata={
                    "memory_type": memory_type,  # work_preference/company_background/business_decision/business_insight
                    "timestamp": str(datetime.now()),
                    "source": "s8_chat",
                    "category": "business"  # 统一标记为业务相关
                }
            )
            print(f"✅ [后台] 记忆已保存: {memory_result}")
    except Exception as e:
        print(f"⚠️ [后台] 保存记忆失败: {e}")


@router.post("/chat")
async def chat_with_s8(request: ChatRequest):
    """
    与S8决策军师对话

    用户可以提问，S8会基于企业记忆和当前报告回答
    """
    print(f"💬 收到对话请求: {request.message}")

    app_state = get_app_state()

    if not app_state.memory_manager or not app_state.llm_client:
        print("❌ 系统未初始化")
        raise HTTPException(status_code=500, detail="系统未初始化")

    user_message = request.message
    if not user_message:
        print("❌ 消息为空")
        raise HTTPException(status_code=400, detail="消息不能为空")

    try:
        print("🔍 搜索相关记忆...")
        # 搜索相关记忆（使用 system 确保能搜到所有记忆）
        memories = app_state.memory_manager.search_memories(
            query=user_message,
            user_id="system",
            limit=5
        )
        print(f"✅ 找到 {len(memories)} 条相关记忆")

        # 构建上下文
        context = "\n".join([f"- {m.content}" for m in memories])

        # 构建消息
        messages = [
            {
                "role": "system",
                "content": f"""你是S8决策军师，一个帮助CEO做决策的AI助手。

相关企业信息：
{context if context else "暂无相关信息"}

请用自然对话的方式回答用户的问题。回答要简洁、专业，就像一个真实的顾问在跟CEO对话。不要使用过多的表情符号，保持专业但友好的语气。"""
            }
        ]

        # 添加对话历史
        if request.conversation_history:
            print(f"📚 包含 {len(request.conversation_history)} 条历史消息")
            messages.extend(request.conversation_history)

        # 添加当前用户消息
        messages.append({
            "role": "user",
            "content": user_message
        })

        print("🤖 调用LLM...")
        # 调用LLM
        response = await app_state.llm_client.async_chat_completion(messages)
        print(f"✅ LLM响应: {response}")

        if response.get("error"):
            print(f"❌ LLM错误: {response.get('error')}")
            raise HTTPException(status_code=500, detail=response["error"])

        reply = response.get("content", "抱歉，我现在无法回答。")
        print(f"💬 回复: {reply[:100]}...")

        # 🧠 智能判断：使用LLM分析对话是否值得保存到长期记忆
        print(f"🤔 正在判断对话是否需要保存到长期记忆...")
        should_save, summary, memory_type = await _should_save_to_memory_llm(
            user_message, reply, app_state.llm_client
        )

        if should_save:
            try:
                # 使用 "system" 作为 user_id，保证记忆全局可见
                user_id = "system"

                # 使用 LLM 提取的摘要（更精炼，易于去重）
                memory_text = summary if summary else f"CEO问: {user_message}\nS8答: {reply}"

                print(f"💾 保存到长期记忆")
                print(f"    类型: {memory_type}")

                # Mem0 会自动判断这条记忆是新增还是更新
                memory_result = app_state.memory_manager.add_memory(
                    content=memory_text,
                    user_id=user_id,
                    metadata={
                        "memory_type": memory_type,  # work_preference/company_background/business_decision/business_insight
                        "timestamp": str(datetime.now()),
                        "source": "s8_chat",
                        "category": "business"  # 统一标记为业务相关
                    }
                )
                print(f"✅ 记忆已保存: {memory_result}")
            except Exception as e:
                print(f"⚠️ 保存记忆失败（不影响对话）: {e}")

        return {
            "success": True,
            "reply": reply
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"❌ 对话失败: {error_detail}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/report/current")
async def get_current_report():
    """
    获取当前报告

    返回最新版本的报告（可能是v1.0或v2.0）
    """
    app_state = get_app_state()

    if not app_state.memory_manager or not app_state.llm_client:
        raise HTTPException(status_code=500, detail="系统未初始化")

    # 创建S8 Agent（会保持单例状态）
    agent = S8DecisionAgent("S8", app_state.memory_manager, app_state.llm_client)

    if not agent.current_report:
        return {
            "success": False,
            "message": "暂无报告，请先生成"
        }

    return {
        "success": True,
        "report": agent.current_report
    }


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket连接 - 用于实时推送报告更新通知

    监听事件：
    - REPORT_UPDATED: 报告已更新
    - MEMORY_CONFLICT: 检测到记忆冲突
    """
    await websocket.accept()

    from app.core.event_bus import get_event_bus, EventNames

    event_bus = get_event_bus()

    # 定义事件处理器
    async def on_report_updated(data: Dict):
        await websocket.send_json({
            "type": "report_updated",
            "data": data
        })

    async def on_conflict(data: Dict):
        await websocket.send_json({
            "type": "memory_conflict",
            "data": data
        })

    async def on_node_status(data: Dict):
        await websocket.send_json({
            "type": "node_status",
            "data": data
        })

    # 订阅事件
    event_bus.subscribe(EventNames.REPORT_UPDATED, on_report_updated)
    event_bus.subscribe(EventNames.MEMORY_CONFLICT, on_conflict)
    event_bus.subscribe("node_status", on_node_status)

    try:
        while True:
            # 接收客户端消息（保持连接）
            data = await websocket.receive_text()
            # 可以处理客户端的ping/pong等
            if data == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        print("WebSocket断开连接")
    except Exception as e:
        print(f"WebSocket错误: {e}")
    finally:
        # 取消订阅
        event_bus.unsubscribe(EventNames.REPORT_UPDATED, on_report_updated)
        event_bus.unsubscribe(EventNames.MEMORY_CONFLICT, on_conflict)
        event_bus.unsubscribe("node_status", on_node_status)
