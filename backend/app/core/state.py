"""
应用全局状态管理
"""
from app.core.memory import MemoryManager
from app.core.llm import LLMClient


class AppState:
    """应用全局状态"""
    memory_manager: MemoryManager = None
    llm_client: LLMClient = None


# 全局状态实例
app_state = AppState()


def get_app_state() -> AppState:
    """获取应用全局状态"""
    return app_state
