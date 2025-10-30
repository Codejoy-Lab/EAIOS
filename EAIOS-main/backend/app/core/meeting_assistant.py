"""
Meeting Assistant Agent - 会议助手
负责处理会议记录，提取结构化信息并写入企业记忆
"""
from typing import Dict, List, Any
import json
from datetime import datetime
from app.core.llm import LLMClient
from app.core.memory import MemoryManager
from app.core.event_bus import get_event_bus, EventNames


class MeetingAssistant:
    """会议助手Agent"""

    def __init__(self, llm_client: LLMClient, memory_manager: MemoryManager):
        self.llm = llm_client
        self.memory = memory_manager
        self.event_bus = get_event_bus()

    async def process_meeting_notes(self, notes: str, metadata: Dict = None) -> Dict:
        """
        处理会议记录

        Args:
            notes: 会议记录文本
            metadata: 额外元数据（可选）

        Returns:
            处理结果
        """
        print(f"📝 会议助手开始处理会议记录...")

        # Step 1: 提取结构化信息
        structured = await self._extract_structured_info(notes)

        if not structured.get("success"):
            print(f"   ❌ 提取失败: {structured.get('error', '未知错误')}")
            return {
                "success": False,
                "error": structured.get("error", "提取失败")
            }

        # Step 2: 写入记忆库
        memory_ids = await self._write_to_memory(structured, notes, metadata)

        # Step 3: 冲突检测
        conflicts = await self._detect_conflicts(structured, memory_ids)

        # Step 4: 触发事件
        await self.event_bus.emit(
            event_name=EventNames.MEETING_RECORDED,
            data={
                "memory_ids": memory_ids,
                "structured_info": structured,
                "has_conflicts": len(conflicts) > 0,
                "conflicts": conflicts,
                "timestamp": datetime.now().isoformat()
            },
            source="meeting_assistant"
        )

        # 如果有新的战略决策或数据异常，触发记忆更新事件
        if structured.get("strategic_decisions") or structured.get("data_insights"):
            await self.event_bus.emit(
                event_name=EventNames.MEMORY_UPDATED,
                data={
                    "memory_ids": memory_ids,
                    "categories": ["strategic_decision", "data_insight"],
                    "source": "meeting_assistant",
                    "requires_update": True
                },
                source="meeting_assistant"
            )

        return {
            "success": True,
            "extracted": structured,
            "memory_ids": memory_ids,
            "conflicts": conflicts,
            "message": f"成功提取 {len(memory_ids)} 条关键信息"
        }

    async def _extract_structured_info(self, notes: str) -> Dict:
        """提取结构化信息"""
        prompt = f"""
你是会议记录分析专家。请从以下会议记录中提取关键信息。

## 会议记录
{notes}

## 任务
提取以下类型的信息（如果存在）：

1. **战略决策** (strategic_decisions)
   - 公司方向、产品策略、市场策略等重大决策
   - 每条包括：内容、类别、参与人、决议日期

2. **数据洞察** (data_insights)
   - 披露的关键数据、异常情况、趋势变化
   - 每条包括：指标名称、当前值、变化情况、严重性

3. **行动决议** (action_items)
   - 明确的待办事项、责任人、截止期
   - 每条包括：行动内容、责任人、截止日期

4. **会议元信息** (meta)
   - 会议标题、日期、参与人

## 输出格式（严格JSON）
{{
  "success": true,
  "meta": {{
    "title": "会议标题",
    "date": "2025-10-29",
    "participants": ["张总", "李经理"]
  }},
  "strategic_decisions": [
    {{
      "content": "决策内容",
      "category": "marketing/product/operation",
      "participants": ["参与人"],
      "importance": "high/medium/low"
    }}
  ],
  "data_insights": [
    {{
      "metric": "指标名称",
      "current_value": "当前值",
      "change": "变化描述",
      "severity": "high/medium/low"
    }}
  ],
  "action_items": [
    {{
      "content": "行动内容",
      "owner": "责任人",
      "deadline": "截止日期"
    }}
  ]
}}

**注意**：
- 只提取明确提到的信息，不要推测
- 如果某类信息不存在，返回空数组
- 战略决策要明确、具体，避免模糊表述
"""

        try:
            response = await self.llm.async_chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )

            # 检查错误
            if "error" in response:
                print(f"❌ LLM调用失败: {response['error']}")
                return {
                    "success": False,
                    "error": response['error']
                }

            # 解析JSON
            content = response.get("content") or ""
            content = content.strip()

            if not content:
                print(f"❌ LLM返回空内容")
                return {
                    "success": False,
                    "error": "LLM返回空内容"
                }

            # 提取JSON（可能被markdown包裹）
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            else:
                # 尝试找到JSON对象（从第一个 { 到最后一个 }）
                start_idx = content.find('{')
                end_idx = content.rfind('}')
                if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                    content = content[start_idx:end_idx+1]

            if not content:
                print(f"❌ 提取JSON后内容为空")
                return {
                    "success": False,
                    "error": "JSON提取失败"
                }

            structured = json.loads(content)
            return structured

        except Exception as e:
            print(f"❌ 提取结构化信息失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _write_to_memory(
        self,
        structured: Dict,
        raw_notes: str,
        metadata: Dict = None
    ) -> List[str]:
        """写入记忆库"""
        memory_ids = []
        base_metadata = metadata or {}

        # 获取会议元信息（带默认值）
        meta = structured.get("meta", {})
        meeting_title = meta.get("title", "会议记录")
        meeting_date = meta.get("date", datetime.now().strftime("%Y-%m-%d"))

        num_decisions = len(structured.get('strategic_decisions', []))
        num_insights = len(structured.get('data_insights', []))
        print(f"   提取: {num_decisions}条战略决策, {num_insights}条数据洞察")

        # 写入战略决策
        for i, decision in enumerate(structured.get("strategic_decisions", []), 1):
            result = self.memory.add_memory(
                content=decision.get("content", ""),
                memory_type="global",
                source=f"{meeting_title} ({meeting_date})",
                metadata={
                    **base_metadata,
                    "category": "strategic_decision",
                    "subcategory": decision.get("category", "general"),
                    "participants": decision.get("participants", []),
                    "importance": decision.get("importance", "medium"),
                    "meeting_date": meeting_date,
                    "raw_notes": raw_notes  # 保存原始记录，用于"点回原文"
                }
            )
            if result.get("success") and result.get("memory_id"):
                memory_ids.append(result["memory_id"])
            else:
                print(f"   ❌ 战略决策写入失败: {result.get('error', '未知错误')}")

        # 写入数据洞察
        for i, insight in enumerate(structured.get("data_insights", []), 1):
            metric = insight.get("metric", "未知指标")
            current_value = insight.get("current_value", "")
            change = insight.get("change", "")
            content = f"{metric}: {current_value} ({change})"
            result = self.memory.add_memory(
                content=content,
                memory_type="global",
                source=f"{meeting_title} - 数据披露",
                metadata={
                    **base_metadata,
                    "category": "data_insight",
                    "metric": metric,
                    "severity": insight.get("severity", "medium"),
                    "meeting_date": meeting_date
                }
            )
            if result.get("success") and result.get("memory_id"):
                memory_ids.append(result["memory_id"])
            else:
                print(f"   ❌ 数据洞察写入失败: {result.get('error', '未知错误')}")

        print(f"✅ 已写入 {len(memory_ids)} 条记忆")
        return memory_ids

    async def _detect_conflicts(self, structured: Dict, new_memory_ids: List[str]) -> List[Dict]:
        """
        检测记忆冲突

        检查新记录的战略决策是否与历史记忆冲突
        """
        conflicts = []

        for decision in structured.get("strategic_decisions", []):
            # 搜索相关的历史决策
            related_memories = self.memory.search_memories(
                query=decision["content"],
                memory_type="global",
                enabled_only=True,
                limit=3
            )

            # 使用LLM判断是否冲突
            for mem in related_memories:
                if mem.id in new_memory_ids:
                    continue  # 跳过刚写入的记忆

                is_conflict = await self._check_if_conflict(
                    new_decision=decision["content"],
                    old_decision=mem.content,
                    new_date=structured["meta"]["date"],
                    old_date=mem.metadata.get("meeting_date", "未知")
                )

                if is_conflict["conflict"]:
                    conflicts.append({
                        "new_memory_id": new_memory_ids[0],  # 简化：取第一个
                        "old_memory_id": mem.id,
                        "new_decision": decision["content"],
                        "old_decision": mem.content,
                        "new_date": structured["meta"]["date"],
                        "old_date": mem.metadata.get("meeting_date", "未知"),
                        "reason": is_conflict["reason"]
                    })

        if conflicts:
            print(f"⚠️  检测到 {len(conflicts)} 个冲突")
            # 触发冲突事件
            await self.event_bus.emit(
                event_name=EventNames.MEMORY_CONFLICT,
                data={
                    "conflicts": conflicts,
                    "count": len(conflicts)
                },
                source="meeting_assistant"
            )

        return conflicts

    async def _check_if_conflict(
        self,
        new_decision: str,
        old_decision: str,
        new_date: str,
        old_date: str
    ) -> Dict:
        """使用LLM判断两条决策是否冲突"""
        prompt = f"""
你是企业战略分析专家。判断两条决策是否存在冲突。

## 旧决策 ({old_date})
{old_decision}

## 新决策 ({new_date})
{new_decision}

## 任务
判断这两条决策是否矛盾或冲突。

冲突定义：
- 方向相反（如"重点A渠道" vs "收缩A渠道"）
- 策略矛盾（如"主推产品X" vs "放弃产品X"）
- 预算/资源分配冲突

输出JSON格式：
{{
  "conflict": true/false,
  "reason": "冲突原因（如果conflict=true）"
}}
"""

        try:
            response = await self.llm.async_chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )

            # 检查错误
            if "error" in response:
                return {"conflict": False, "reason": ""}

            content = response.get("content") or ""
            content = content.strip()

            if not content:
                return {"conflict": False, "reason": ""}

            # 提取JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            else:
                # 尝试找到JSON对象
                start_idx = content.find('{')
                end_idx = content.rfind('}')
                if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                    content = content[start_idx:end_idx+1]

            if not content:
                return {"conflict": False, "reason": ""}

            result = json.loads(content)
            return result

        except Exception as e:
            print(f"❌ 冲突检测失败: {e}")
            return {"conflict": False, "reason": ""}


# 单例
_meeting_assistant_instance = None


def get_meeting_assistant(llm_client: LLMClient, memory_manager: MemoryManager) -> MeetingAssistant:
    """获取会议助手单例"""
    global _meeting_assistant_instance
    if _meeting_assistant_instance is None:
        _meeting_assistant_instance = MeetingAssistant(llm_client, memory_manager)
    return _meeting_assistant_instance
