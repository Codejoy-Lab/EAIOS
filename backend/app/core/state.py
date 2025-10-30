"""
应用全局状态管理
"""
from app.core.memory import MemoryManager
from app.core.llm import LLMClient
from app.core.mcp_client import MCPClient
from typing import Optional


class AppState:
    """应用全局状态"""
    memory_manager: Optional[MemoryManager] = None
    llm_client: Optional[LLMClient] = None
    mcp_client: Optional[MCPClient] = None  # 飞书任务MCP客户端


# 全局状态实例
app_state = AppState()


def get_app_state() -> AppState:
    """获取应用全局状态"""
    return app_state
