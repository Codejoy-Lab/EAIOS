"""
Event Bus - 事件总线
用于Agent之间的事件驱动通信
"""
from typing import Callable, Dict, List, Any
import asyncio
from datetime import datetime
import json


class Event:
    """事件对象"""
    def __init__(self, name: str, data: Dict[str, Any], source: str):
        self.name = name
        self.data = data
        self.source = source
        self.timestamp = datetime.now().isoformat()
        self.id = f"EVT_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "data": self.data,
            "source": self.source,
            "timestamp": self.timestamp
        }


class EventBus:
    """事件总线 - 支持异步事件分发"""

    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.event_history: List[Event] = []
        self.max_history = 100

    def subscribe(self, event_name: str, callback: Callable):
        """
        订阅事件

        Args:
            event_name: 事件名称
            callback: 回调函数（支持异步）
        """
        if event_name not in self.subscribers:
            self.subscribers[event_name] = []

        self.subscribers[event_name].append(callback)
        print(f"✅ 订阅事件: {event_name} -> {callback.__name__}")

    def unsubscribe(self, event_name: str, callback: Callable):
        """取消订阅"""
        if event_name in self.subscribers:
            self.subscribers[event_name].remove(callback)

    async def emit(self, event_name: str, data: Dict[str, Any], source: str = "unknown"):
        """
        触发事件（异步）

        Args:
            event_name: 事件名称
            data: 事件数据
            source: 事件来源
        """
        event = Event(name=event_name, data=data, source=source)

        # 记录历史
        self.event_history.append(event)
        if len(self.event_history) > self.max_history:
            self.event_history.pop(0)

        print(f"📡 触发事件: {event_name} | 来源: {source}")

        # 分发给订阅者
        if event_name in self.subscribers:
            tasks = []
            for callback in self.subscribers[event_name]:
                # 支持同步和异步回调
                if asyncio.iscoroutinefunction(callback):
                    tasks.append(callback(event.data))
                else:
                    # 同步函数包装为异步
                    tasks.append(asyncio.to_thread(callback, event.data))

            # 并发执行所有订阅者
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)

        return event.id

    def get_event_history(self, event_name: str = None, limit: int = 10) -> List[Dict]:
        """获取事件历史"""
        history = self.event_history

        if event_name:
            history = [e for e in history if e.name == event_name]

        return [e.to_dict() for e in history[-limit:]]

    def clear_history(self):
        """清空历史"""
        self.event_history.clear()


# 全局单例
_event_bus_instance = None


def get_event_bus() -> EventBus:
    """获取事件总线单例"""
    global _event_bus_instance
    if _event_bus_instance is None:
        _event_bus_instance = EventBus()
    return _event_bus_instance


# 事件名称常量
class EventNames:
    """事件名称定义"""
    MEMORY_UPDATED = "memory_updated"  # 记忆更新
    MEMORY_CONFLICT = "memory_conflict"  # 记忆冲突
    MEETING_RECORDED = "meeting_recorded"  # 会议记录录入
    REPORT_GENERATED = "report_generated"  # 报告生成
    REPORT_UPDATED = "report_updated"  # 报告更新
    ACTION_CONFIRMED = "action_confirmed"  # 行动确认
