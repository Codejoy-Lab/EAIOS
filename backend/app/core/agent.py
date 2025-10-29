"""
Agent Orchestrator - Agent编排引擎基础框架
基于LangGraph实现多Agent协同
"""
from typing import TypedDict, List, Dict, Optional, Callable
from datetime import datetime
from langgraph.graph import StateGraph, END
from app.core.memory import MemoryManager
from app.core.llm import LLMClient


class AgentState(TypedDict):
    """Agent状态定义"""
    scenario_id: str  # S1-S8
    current_node: str  # 当前节点
    input_data: Dict  # 输入数据
    memories: List[Dict]  # 召回的记忆
    node_outputs: Dict  # 各节点输出
    sources: List[Dict]  # 来源证明链
    needs_confirmation: bool  # 是否需要人工确认
    error: Optional[str]  # 错误信息


class BaseAgentNode:
    """Agent节点基类"""

    def __init__(
        self,
        node_name: str,
        memory_manager: MemoryManager,
        llm_client: LLMClient,
        is_critical: bool = False
    ):
        """
        初始化节点

        Args:
            node_name: 节点名称
            memory_manager: 记忆管理器
            llm_client: LLM客户端
            is_critical: 是否为关键节点（需要人工确认）
        """
        self.node_name = node_name
        self.memory_manager = memory_manager
        self.llm_client = llm_client
        self.is_critical = is_critical

    async def execute(self, state: AgentState) -> AgentState:
        """
        执行节点逻辑

        Args:
            state: 当前状态

        Returns:
            更新后的状态
        """
        raise NotImplementedError("子类必须实现execute方法")

    def _recall_memories(self, query: str, memory_type: Optional[str] = None) -> List[Dict]:
        """
        召回相关记忆

        Args:
            query: 查询内容
            memory_type: 记忆类型

        Returns:
            记忆列表
        """
        memories = self.memory_manager.search_memories(
            query=query,
            memory_type=memory_type,
            enabled_only=True
        )
        return [mem.to_dict() for mem in memories]

    def _add_source(self, state: AgentState, memory_ids: List[str], additional_info: Dict = None):
        """
        添加来源证明

        Args:
            state: 状态
            memory_ids: 记忆ID列表
            additional_info: 额外信息
        """
        source_entry = {
            "node": self.node_name,
            "memory_ids": memory_ids,
            "timestamp": datetime.now().isoformat(),
            **(additional_info or {})
        }
        state["sources"].append(source_entry)


class ScenarioOrchestrator:
    """场景编排器基类"""

    def __init__(
        self,
        scenario_id: str,
        memory_manager: MemoryManager,
        llm_client: LLMClient
    ):
        """
        初始化编排器

        Args:
            scenario_id: 场景ID (S1-S8)
            memory_manager: 记忆管理器
            llm_client: LLM客户端
        """
        self.scenario_id = scenario_id
        self.memory_manager = memory_manager
        self.llm_client = llm_client
        self.graph = None

    def build_graph(self) -> StateGraph:
        """
        构建场景的状态图

        Returns:
            状态图
        """
        raise NotImplementedError("子类必须实现build_graph方法")

    async def run(self, input_data: Dict, callback: Optional[Callable] = None) -> Dict:
        """
        运行场景

        Args:
            input_data: 输入数据
            callback: 回调函数（用于推送状态）

        Returns:
            最终结果
        """
        if not self.graph:
            self.graph = self.build_graph()

        # 初始化状态
        initial_state: AgentState = {
            "scenario_id": self.scenario_id,
            "current_node": "",
            "input_data": input_data,
            "memories": [],
            "node_outputs": {},
            "sources": [],
            "needs_confirmation": False,
            "error": None
        }

        # 执行状态图
        try:
            final_state = await self.graph.ainvoke(initial_state)
            return {
                "success": True,
                "outputs": final_state["node_outputs"],
                "sources": final_state["sources"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# 场景注册表
SCENARIO_REGISTRY: Dict[str, type] = {}


def register_scenario(scenario_id: str):
    """
    场景注册装饰器

    Usage:
        @register_scenario("S1")
        class S1Orchestrator(ScenarioOrchestrator):
            ...
    """
    def decorator(cls):
        SCENARIO_REGISTRY[scenario_id] = cls
        return cls
    return decorator


def get_orchestrator(
    scenario_id: str,
    memory_manager: MemoryManager,
    llm_client: LLMClient
) -> Optional[ScenarioOrchestrator]:
    """
    获取场景编排器

    Args:
        scenario_id: 场景ID
        memory_manager: 记忆管理器
        llm_client: LLM客户端

    Returns:
        编排器实例
    """
    orchestrator_class = SCENARIO_REGISTRY.get(scenario_id)
    if orchestrator_class:
        return orchestrator_class(scenario_id, memory_manager, llm_client)
    return None
