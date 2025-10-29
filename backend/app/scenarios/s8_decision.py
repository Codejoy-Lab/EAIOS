"""
S8 Decision Agent - CEO决策军师
主打：企业大脑，兼顾主动式
"""
from typing import Dict, List, Any, Optional
import json
from datetime import datetime
from app.core.agent import ScenarioOrchestrator, AgentState, register_scenario
from app.core.memory import MemoryManager
from app.core.llm import LLMClient
from app.core.mcp import get_tool_registry
from app.core.event_bus import get_event_bus, EventNames


@register_scenario("S8")
class S8DecisionAgent(ScenarioOrchestrator):
    """S8 CEO决策军师Agent"""

    _instance = None  # 单例实例
    _is_processing_update = False  # 防止重复处理

    def __new__(cls, scenario_id: str, memory_manager: MemoryManager, llm_client: LLMClient):
        """单例模式：确保只有一个Agent实例"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, scenario_id: str, memory_manager: MemoryManager, llm_client: LLMClient):
        # 只初始化一次
        if self._initialized:
            return

        super().__init__(scenario_id, memory_manager, llm_client)
        self.event_bus = get_event_bus()
        self.current_report = None  # 保存当前报告（用于修正）
        self.report_version = "v1.0"

        # 订阅记忆更新事件（只订阅一次）
        self.event_bus.subscribe(EventNames.MEMORY_UPDATED, self.on_memory_updated)
        print(f"✅ S8 Agent已初始化并订阅事件")

        self._initialized = True

    async def generate_report(self, input_data: Dict = None) -> Dict:
        """
        生成CEO晨报

        Args:
            input_data: 输入数据（可选）

        Returns:
            完整报告
        """
        print(f"📊 开始生成CEO决策军师晨报 ({self.report_version})...")

        # 节点1: 汇总助手
        summary = await self._node_summary(input_data)

        # 节点2: 异常/风险助手
        risks = await self._node_risk_detection(summary)

        # 节点3: 策略建议助手
        recommendations = await self._node_recommendations(summary, risks)

        # 构建完整报告
        report = {
            "version": self.report_version,
            "generated_at": datetime.now().isoformat(),
            "summary": summary,
            "risks": risks,
            "recommendations": recommendations,
            "status": "pending_confirmation"  # 等待节点4确认
        }

        # 保存当前报告
        self.current_report = report

        # 触发事件
        await self.event_bus.emit(
            event_name=EventNames.REPORT_GENERATED,
            data={
                "version": self.report_version,
                "report": report
            },
            source="s8_decision_agent"
        )

        return report

    async def _node_summary(self, input_data: Dict = None) -> Dict:
        """节点1: 汇总助手"""
        print("  [节点1] 汇总助手...")

        # 推送节点开始状态
        await self.event_bus.emit(
            event_name="node_status",
            data={
                "node": "summary",
                "status": "working",
                "message": "正在汇总经营数据和关键指标..."
            },
            source="s8_decision_agent"
        )

        # 1. 从MCP工具获取经营数据
        analytics_tool = get_tool_registry().get_tool("query_analytics")
        if analytics_tool:
            metrics_result = await analytics_tool.execute(metric="all")
            metrics_data = metrics_result.get("data", {})
        else:
            # 兜底：从模拟数据加载
            import os
            import json
            data_path = "data/analytics.json"
            if os.path.exists(data_path):
                with open(data_path, 'r', encoding='utf-8') as f:
                    metrics_data = json.load(f).get("metrics", {})
            else:
                metrics_data = {}

        # 2. 从记忆管理器召回会议共识
        memories = self.memory_manager.search_memories(
            query="Q4战略 经营目标 核心指标 产品线",
            memory_type="global",
            enabled_only=True,
            limit=5
        )

        memory_context = "\n".join([
            f"{i+1}. {m.content}\n   来源: {m.metadata.get('source', '未知')}"
            for i, m in enumerate(memories)
        ])

        # 3. 构建LLM提示词
        prompt = f"""
你是CEO的战略助手，正在生成每日晨报的"经营摘要"部分。

## 企业记忆与共识
{memory_context if memory_context else "暂无相关记忆"}

## 经营数据（近7天）
{json.dumps(metrics_data, ensure_ascii=False, indent=2)}

## 任务
生成一份简洁的经营摘要（3-5句话），包括：
1. 核心指标表现（营收、转化率、获客成本等）
2. 与公司战略目标的对齐情况（如果有记忆的话）
3. 需要CEO关注的点

## 输出格式（JSON）
{{
  "summary_text": "经营摘要文本（3-5句话）",
  "key_metrics": [
    {{"name": "指标名", "value": "值", "status": "正常/异常", "change": "变化"}},
    ...
  ],
  "evidence_ids": ["引用的记忆ID"]
}}
"""

        try:
            response = await self.llm_client.async_chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5
            )

            # 检查错误
            if "error" in response:
                print(f"    ✗ LLM调用失败: {response['error']}")
                return {
                    "summary_text": "LLM服务暂时不可用",
                    "key_metrics": [],
                    "evidence_ids": []
                }

            content = response.get("content") or ""
            content = content.strip()

            if not content:
                print(f"    ✗ LLM返回空内容")
                return {
                    "summary_text": "LLM返回空内容",
                    "key_metrics": [],
                    "evidence_ids": []
                }

            # 提取JSON内容
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

            # 再次检查是否为空
            if not content:
                print(f"    ✗ 提取JSON后内容为空")
                return {
                    "summary_text": "JSON提取失败",
                    "key_metrics": [],
                    "evidence_ids": []
                }

            result = json.loads(content)
            result["evidence_ids"] = [m.id for m in memories]
            result["data_source"] = "analytics.json"

            print(f"    ✓ 汇总完成: {len(result.get('key_metrics', []))} 个关键指标")

            # 推送节点完成状态
            await self.event_bus.emit(
                event_name="node_status",
                data={
                    "node": "summary",
                    "status": "completed",
                    "message": f"汇总完成：{len(result.get('key_metrics', []))} 个关键指标"
                },
                source="s8_decision_agent"
            )

            return result

        except Exception as e:
            print(f"    ✗ 汇总失败: {e}")
            return {
                "summary_text": "经营数据加载失败",
                "key_metrics": [],
                "evidence_ids": []
            }

    async def _node_risk_detection(self, summary: Dict) -> Dict:
        """节点2: 异常/风险助手"""
        print("  [节点2] 异常/风险助手...")

        # 推送节点开始状态
        await self.event_bus.emit(
            event_name="node_status",
            data={
                "node": "risk",
                "status": "working",
                "message": "正在识别异常和风险..."
            },
            source="s8_decision_agent"
        )

        # 召回相关会议共识
        memories = self.memory_manager.search_memories(
            query="转化率 营销策略 渠道 风险",
            memory_type="global",
            enabled_only=True,
            limit=5
        )

        memory_context = "\n".join([
            f"{i+1}. {m.content} (来源: {m.metadata.get('source', '未知')})"
            for i, m in enumerate(memories)
        ])

        prompt = f"""
你是风险识别专家，正在为CEO识别需要关注的异常和风险。

## 企业记忆（会议共识）
{memory_context if memory_context else "暂无相关记忆"}

## 当前经营情况
{summary.get('summary_text', '')}

指标详情：
{json.dumps(summary.get('key_metrics', []), ensure_ascii=False, indent=2)}

## 任务
识别2-3个需要CEO关注的异常或风险，每个包括：
- 异常描述
- 可能原因（**必须结合"企业记忆"中的会议共识来分析**）
- 严重程度

**关键约束**：
1. 你的分析必须基于公司已达成的共识
2. 如果某个异常与会议决议的重点方向相关，务必指出
3. 不要提出与会议决议相悖的观点

## 输出格式（JSON）
{{
  "risks": [
    {{
      "title": "异常标题",
      "description": "异常描述",
      "reason": "可能原因（必须结合企业记忆分析）",
      "severity": "high/medium/low",
      "evidence_ids": ["相关的记忆ID或数据ID"]
    }}
  ]
}}
"""

        try:
            response = await self.llm_client.async_chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6
            )

            # 检查错误
            if "error" in response:
                print(f"    ✗ LLM调用失败: {response['error']}")
                return {"risks": []}

            content = response.get("content") or ""
            content = content.strip()

            if not content:
                print(f"    ✗ LLM返回空内容")
                return {"risks": []}

            # 提取JSON内容
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

            # 再次检查是否为空
            if not content:
                print(f"    ✗ 提取JSON后内容为空")
                return {"risks": []}

            result = json.loads(content)

            # 补充evidence_ids
            for risk in result.get("risks", []):
                if not risk.get("evidence_ids"):
                    risk["evidence_ids"] = [m.id for m in memories[:2]]

            print(f"    ✓ 识别到 {len(result.get('risks', []))} 个风险")

            # 推送节点完成状态
            await self.event_bus.emit(
                event_name="node_status",
                data={
                    "node": "risk",
                    "status": "completed",
                    "message": f"识别到 {len(result.get('risks', []))} 个风险"
                },
                source="s8_decision_agent"
            )

            return result

        except Exception as e:
            print(f"    ✗ 风险识别失败: {e}")
            return {"risks": []}

    async def _node_recommendations(self, summary: Dict, risks: Dict) -> Dict:
        """节点3: 策略建议助手（核心节点）"""
        print("  [节点3] 策略建议助手...")

        # 推送节点开始状态
        await self.event_bus.emit(
            event_name="node_status",
            data={
                "node": "recommendation",
                "status": "working",
                "message": "正在生成策略建议..."
            },
            source="s8_decision_agent"
        )

        # 召回会议共识（必须！）
        memories = self.memory_manager.search_memories(
            query="Q4战略 营销策略 产品线 渠道 预算",
            memory_type="global",
            enabled_only=True,
            limit=5
        )

        memory_context = "\n".join([
            f"{i+1}. {m.content}\n   来源: {m.metadata.get('source', '未知')}\n   ID: {m.id}"
            for i, m in enumerate(memories)
        ])

        prompt = f"""
你是资深战略顾问，正在为CEO准备每日简报的"三项优先行动"。

## 企业记忆与共识（必须严格遵守！）
{memory_context if memory_context else "暂无相关记忆"}

## 当前情况
{summary.get('summary_text', '')}

## 异常与风险
{json.dumps(risks.get('risks', []), ensure_ascii=False, indent=2)}

## 任务
根据上述信息，给出**三项优先行动建议**，每项包括：
- 行动标题（具体、可执行）
- 详细描述
- 为什么（必须引用"企业记忆"或"经营数据"）
- 预期效果（量化）
- 建议责任人
- 建议截止期

## 关键约束（非常重要！）
1. 所有建议必须与"企业记忆"中的会议共识方向**完全一致**
2. 禁止提出与会议决议相悖的建议
   - 例如：会议说"重点小红书"，就不能建议"放弃小红书"
3. 如果经营数据与会议共识冲突，优先按会议共识方向调整策略
4. 每个建议必须明确引用依据（哪次会议、哪条数据）
5. 如果没有相关的企业记忆，可以给通用建议，但要说明"未找到相关共识"

## 输出格式（JSON）
{{
  "actions": [
    {{
      "title": "行动标题",
      "description": "详细描述（2-3句话）",
      "reason": "依据（必须引用具体的记忆或数据）",
      "evidence_ids": ["memory_id_1", "data_id"],
      "expected_impact": "预期提升转化率0.5个百分点",
      "suggested_owner": "市场部李经理",
      "suggested_deadline": "2025-11-05",
      "priority": 1
    }},
    ...
  ]
}}
"""

        try:
            response = await self.llm_client.async_chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )

            # 检查错误
            if "error" in response:
                print(f"    ✗ LLM调用失败: {response['error']}")
                return {"actions": []}

            content = response.get("content") or ""
            content = content.strip()

            if not content:
                print(f"    ✗ LLM返回空内容")
                return {"actions": []}

            # 提取JSON内容
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

            # 再次检查是否为空
            if not content:
                print(f"    ✗ 提取JSON后内容为空")
                return {"actions": []}

            result = json.loads(content)

            # 补充evidence_ids
            for action in result.get("actions", []):
                if not action.get("evidence_ids"):
                    action["evidence_ids"] = [m.id for m in memories[:2]]

            print(f"    ✓ 生成 {len(result.get('actions', []))} 项建议")

            # 推送节点完成状态
            await self.event_bus.emit(
                event_name="node_status",
                data={
                    "node": "recommendation",
                    "status": "completed",
                    "message": f"生成 {len(result.get('actions', []))} 项建议"
                },
                source="s8_decision_agent"
            )

            return result

        except Exception as e:
            print(f"    ✗ 建议生成失败: {e}")
            return {"actions": []}

    async def confirm_actions(self, actions_with_assignment: List[Dict], sync_to_board: bool = False) -> Dict:
        """
        节点4: 行动清单/指派助手（关键节点）

        Args:
            actions_with_assignment: 确认后的行动（含责任人和截止期）
            sync_to_board: 是否同步到看板

        Returns:
            任务列表和同步日志
        """
        print("  [节点4] 行动清单/指派助手...")

        tasks = []
        for action in actions_with_assignment:
            task_id = f"TASK_{datetime.now().strftime('%Y%m%d')}_{datetime.now().strftime('%H%M%S')}"

            task = {
                "task_id": task_id,
                "title": action["title"],
                "description": action.get("description", ""),
                "owner": action["owner"],
                "deadline": action["deadline"],
                "status": "待开始",
                "created_at": datetime.now().isoformat(),
                "created_by": "CEO",
                "evidence_ids": action.get("evidence_ids", []),
                "expected_impact": action.get("expected_impact", "")
            }

            tasks.append(task)

        # 同步到看板（模拟）
        sync_log = ""
        if sync_to_board:
            sync_log = f"已生成 {len(tasks)} 个任务，模拟同步到飞书看板"
            print(f"    ✓ {sync_log}")
        else:
            sync_log = f"已生成 {len(tasks)} 个任务，未同步到看板"

        # 更新报告状态
        if self.current_report:
            self.current_report["status"] = "confirmed"
            self.current_report["tasks"] = tasks
            self.current_report["sync_log"] = sync_log

        # 触发事件
        await self.event_bus.emit(
            event_name=EventNames.ACTION_CONFIRMED,
            data={
                "tasks": tasks,
                "sync_to_board": sync_to_board,
                "count": len(tasks)
            },
            source="s8_decision_agent"
        )

        return {
            "success": True,
            "tasks": tasks,
            "sync_log": sync_log
        }

    async def on_memory_updated(self, event_data: Dict):
        """
        监听记忆更新事件，主动修正报告（方案核心！）

        Args:
            event_data: 事件数据
        """
        # 防抖：如果正在处理，跳过
        if S8DecisionAgent._is_processing_update:
            print(f"⏭️  正在处理中，跳过此次事件")
            return

        S8DecisionAgent._is_processing_update = True
        try:
            print(f"🔔 检测到记忆更新事件，正在分析是否需要修正报告...")

            # 检查是否有当前报告
            if not self.current_report:
                print("  → 暂无当前报告，跳过")
                return

            # 检查报告是否已确认（已确认的不再修正）
            if self.current_report.get("status") == "confirmed":
                print("  → 报告已确认，不再修正")
                return

            # 获取新记忆
            new_memory_ids = event_data.get("memory_ids", [])
            if not new_memory_ids:
                return

            new_memories = []
            for mid in new_memory_ids:
                memories = self.memory_manager.get_all_memories()
                for m in memories:
                    if m.id == mid:
                        new_memories.append(m)
                        break

            if not new_memories:
                return

            print(f"  → 检测到 {len(new_memories)} 条新记忆")

            # 判断是否需要修正
            should_update = await self._should_update_report(new_memories)

            if should_update["should_update"]:
                print(f"  → 需要修正报告: {should_update['reason']}")

                # 生成修正版本
                self.report_version = "v2.0"
                new_report = await self.generate_report()

                # 生成对比
                comparison = await self._generate_comparison(
                    old_report=self.current_report,
                    new_report=new_report,
                    trigger_memories=new_memories
                )

                # 触发报告更新事件
                await self.event_bus.emit(
                    event_name=EventNames.REPORT_UPDATED,
                    data={
                        "old_version": "v1.0",
                        "new_version": "v2.0",
                        "comparison": comparison,
                        "trigger_source": "memory_updated",
                        "new_memories": [m.to_dict() for m in new_memories]
                    },
                    source="s8_decision_agent"
                )

                print("  ✓ 报告已更新并推送通知")
            else:
                print(f"  → 无需修正: {should_update.get('reason', '不影响当前建议')}")

        finally:
            # 重置处理标志
            S8DecisionAgent._is_processing_update = False

    async def _should_update_report(self, new_memories: List) -> Dict:
        """判断是否需要修正报告"""
        current_recommendations = self.current_report.get("recommendations", {}).get("actions", [])

        memory_contents = "\n".join([f"- {m.content}" for m in new_memories])
        current_actions = "\n".join([f"- {a['title']}" for a in current_recommendations])

        prompt = f"""
你是战略分析专家。判断新录入的会议记录是否需要修正当前的CEO晨报建议。

## 当前建议（v1.0）
{current_actions}

## 刚刚录入的会议记录
{memory_contents}

## 任务
判断：新会议内容是否与当前建议存在**冲突**或**重要补充**？

需要修正的情况：
1. 新会议明确了战略方向，与当前建议不一致
2. 新会议披露了关键数据，改变了优先级
3. 新会议已有明确决议，当前建议未体现

输出JSON：
{{
  "should_update": true/false,
  "reason": "原因说明"
}}
"""

        try:
            response = await self.llm_client.async_chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )

            content = response.get("content", "")
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()

            return json.loads(content)

        except Exception as e:
            print(f"    ✗ 判断失败: {e}")
            return {"should_update": False, "reason": "判断失败"}

    async def _generate_comparison(self, old_report: Dict, new_report: Dict, trigger_memories: List) -> Dict:
        """生成报告对比"""
        old_actions = old_report.get("recommendations", {}).get("actions", [])
        new_actions = new_report.get("recommendations", {}).get("actions", [])

        # 使用LLM生成修正说明
        prompt = f"""
你是CEO决策助手。刚刚公司录入了新的会议记录，你重新分析后修正了建议。现在需要向CEO解释修正原因。

## 旧建议（v1.0）
{json.dumps([{"title": a["title"], "reason": a["reason"]} for a in old_actions], ensure_ascii=False, indent=2)}

## 新建议（v2.0）
{json.dumps([{"title": a["title"], "reason": a["reason"]} for a in new_actions], ensure_ascii=False, indent=2)}

## 触发修正的会议记录
{chr(10).join([f"- {m.content}" for m in trigger_memories])}

## 任务
生成修正说明，向CEO解释：
1. 为什么修改了每条建议？
2. 新会议记录中的哪些信息影响了决策？

输出JSON：
{{
  "revision_summary": "总体修正原因（2-3句话）",
  "revision_reasons": [
    {{
      "action_index": 0,
      "old_title": "旧建议标题",
      "new_title": "新建议标题",
      "why_changed": "修正原因（1-2句话）"
    }},
    ...
  ]
}}
"""

        try:
            response = await self.llm_client.async_chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6
            )

            content = response.get("content", "")
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()

            comparison = json.loads(content)
            comparison["old_version"] = "v1.0"
            comparison["new_version"] = "v2.0"
            comparison["trigger_source"] = [m.metadata.get("source", "未知") for m in trigger_memories]

            return comparison

        except Exception as e:
            print(f"    ✗ 对比生成失败: {e}")
            return {
                "revision_summary": "基于新的会议记录，已更新建议",
                "revision_reasons": []
            }
