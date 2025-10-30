"""
Memory Manager - 基于Mem0的记忆管理系统
支持：添加、查询、勾选、删除记忆，以及来源溯源
"""
from typing import List, Dict, Optional, Any
from datetime import datetime
from mem0 import Memory
import json


class MemoryItem:
    """记忆项数据模型"""

    def __init__(
        self,
        id: str,
        content: str,
        memory_type: str,  # "global" | "scenario" | "interaction"
        enabled: bool = True,
        metadata: Optional[Dict] = None,
        created_at: Optional[str] = None
    ):
        self.id = id
        self.content = content
        self.memory_type = memory_type
        self.enabled = enabled
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.now().isoformat()

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "id": self.id,
            "content": self.content,
            "memory_type": self.memory_type,
            "enabled": self.enabled,
            "metadata": self.metadata,
            "created_at": self.created_at
        }

    @classmethod
    def from_mem0_result(cls, result: Dict) -> "MemoryItem":
        """从Mem0查询结果创建"""
        return cls(
            id=result.get("id", ""),
            content=result.get("memory", ""),
            memory_type=result.get("metadata", {}).get("type", "global"),
            enabled=result.get("metadata", {}).get("enabled", True),
            metadata=result.get("metadata", {}),
            created_at=result.get("created_at", datetime.now().isoformat())
        )


class MemoryManager:
    """记忆管理器 - 企业大脑核心"""

    def __init__(self):
        """初始化Mem0"""
        try:
            # 初始化Mem0（本地模式，使用Qdrant作为向量数据库）
            self.memory = Memory()
            print("✅ Mem0初始化成功")
        except Exception as e:
            print(f"⚠️  Mem0初始化失败: {e}")
            print("   提示：如果首次使用，Mem0会自动下载嵌入模型")
            self.memory = None

    def add_memory(
        self,
        content: str,
        memory_type: str = "global",
        source: str = "手动输入",
        metadata: Optional[Dict] = None,
        user_id: str = "system"
    ) -> Dict:
        """
        添加记忆

        Args:
            content: 记忆内容
            memory_type: 记忆类型 (global/scenario/interaction)
            source: 来源
            metadata: 额外元数据
            user_id: 用户ID

        Returns:
            添加结果
        """
        if not self.memory:
            return {"success": False, "error": "Mem0未初始化"}

        try:
            # 准备元数据
            full_metadata = {
                "type": memory_type,
                "source": source,
                "enabled": True,
                "created_at": datetime.now().isoformat(),
                **(metadata or {})
            }

            # 添加到Mem0
            result = self.memory.add(
                messages=[{"role": "user", "content": content}],
                user_id=user_id,
                metadata=full_metadata
            )

            # 处理不同的返回格式 - Mem0 可能返回列表或字典
            memory_id = None
            if isinstance(result, list):
                # 列表格式：直接是结果列表
                if result and len(result) > 0:
                    memory_id = result[0].get("id") if isinstance(result[0], dict) else None
            elif isinstance(result, dict):
                # 字典格式：包含 "results" 键
                results = result.get("results", [])
                if results and len(results) > 0:
                    memory_id = results[0].get("id") if isinstance(results[0], dict) else None

            return {
                "success": True,
                "memory_id": memory_id,
                "message": "记忆添加成功"
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"添加记忆失败: {str(e)}"
            }

    def search_memories(
        self,
        query: str,
        memory_type: Optional[str] = None,
        enabled_only: bool = True,
        user_id: str = "system",
        limit: int = 5
    ) -> List[MemoryItem]:
        """
        搜索相关记忆（语义搜索）

        Args:
            query: 搜索查询
            memory_type: 记忆类型过滤
            enabled_only: 只返回已启用的记忆
            user_id: 用户ID
            limit: 返回数量

        Returns:
            记忆列表
        """
        if not self.memory:
            return []

        try:
            # 搜索记忆
            results = self.memory.search(
                query=query,
                user_id=user_id,
                limit=limit
            )

            # 解析结果 - Mem0 可能返回列表或字典
            memories = []

            # 处理不同的返回格式
            if isinstance(results, list):
                result_list = results
            elif isinstance(results, dict):
                result_list = results.get("results", [])
            else:
                result_list = []

            for result in result_list:
                memory_item = MemoryItem.from_mem0_result(result)

                # 过滤
                if memory_type and memory_item.memory_type != memory_type:
                    continue
                if enabled_only and not memory_item.enabled:
                    continue

                memories.append(memory_item)

            return memories

        except Exception as e:
            print(f"搜索记忆失败: {e}")
            return []

    def get_all_memories(
        self,
        user_id: str = "system",
        memory_type: Optional[str] = None
    ) -> List[MemoryItem]:
        """
        获取所有记忆

        Args:
            user_id: 用户ID
            memory_type: 记忆类型过滤

        Returns:
            记忆列表
        """
        if not self.memory:
            return []

        try:
            # 获取所有记忆
            results = self.memory.get_all(user_id=user_id)

            # 解析结果 - Mem0 可能返回列表或字典
            memories = []

            # 处理不同的返回格式
            if isinstance(results, list):
                result_list = results
            elif isinstance(results, dict):
                result_list = results.get("results", [])
            else:
                result_list = []

            for result in result_list:
                memory_item = MemoryItem.from_mem0_result(result)

                # 过滤
                if memory_type and memory_item.memory_type != memory_type:
                    continue

                memories.append(memory_item)

            return memories

        except Exception as e:
            print(f"获取记忆失败: {e}")
            return []

    def toggle_memory(
        self,
        memory_id: str,
        enabled: bool,
        user_id: str = "system"
    ) -> Dict:
        """
        勾选/取消勾选记忆

        Args:
            memory_id: 记忆ID
            enabled: 是否启用
            user_id: 用户ID

        Returns:
            操作结果
        """
        if not self.memory:
            return {"success": False, "error": "Mem0未初始化"}

        try:
            # 更新记忆的enabled状态
            # 注意：Mem0的update API可能有限制，这里使用metadata更新
            result = self.memory.update(
                memory_id=memory_id,
                data={"enabled": enabled}
            )

            return {
                "success": True,
                "message": f"记忆已{'启用' if enabled else '禁用'}"
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"更新记忆失败: {str(e)}"
            }

    def delete_memory(
        self,
        memory_id: str,
        user_id: str = "system"
    ) -> Dict:
        """
        删除记忆

        Args:
            memory_id: 记忆ID
            user_id: 用户ID

        Returns:
            操作结果
        """
        if not self.memory:
            return {"success": False, "error": "Mem0未初始化"}

        try:
            # 删除记忆
            self.memory.delete(memory_id=memory_id)

            return {
                "success": True,
                "message": "记忆已删除"
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"删除记忆失败: {str(e)}"
            }

    def build_memory_context(
        self,
        query: str,
        memory_type: Optional[str] = None,
        user_id: str = "system",
        max_memories: int = 5
    ) -> str:
        """
        为LLM构建记忆上下文

        Args:
            query: 查询内容
            memory_type: 记忆类型
            user_id: 用户ID
            max_memories: 最多包含的记忆数量

        Returns:
            格式化的记忆上下文字符串
        """
        memories = self.search_memories(
            query=query,
            memory_type=memory_type,
            enabled_only=True,
            user_id=user_id,
            limit=max_memories
        )

        if not memories:
            return "暂无相关记忆。"

        context_lines = ["## 企业记忆与规定\n"]
        for i, mem in enumerate(memories, 1):
            source_info = mem.metadata.get("source", "未知来源")
            context_lines.append(
                f"{i}. {mem.content}\n   来源: {source_info}"
            )

        return "\n".join(context_lines)


# 单例模式（可选）
_memory_manager_instance = None


def get_memory_manager() -> MemoryManager:
    """获取记忆管理器单例"""
    global _memory_manager_instance
    if _memory_manager_instance is None:
        _memory_manager_instance = MemoryManager()
    return _memory_manager_instance
