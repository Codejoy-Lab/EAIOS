"""
Memory Management API
记忆管理接口
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.core.state import get_app_state

router = APIRouter()


class AddMemoryRequest(BaseModel):
    """添加记忆请求"""
    content: str
    memory_type: str = "global"  # global/scenario/interaction
    source: str = "手动输入"
    metadata: Optional[dict] = None


class ToggleMemoryRequest(BaseModel):
    """勾选记忆请求"""
    memory_id: str
    enabled: bool


class SearchMemoryRequest(BaseModel):
    """搜索记忆请求"""
    query: str
    memory_type: Optional[str] = None
    enabled_only: bool = True
    limit: int = 5


@router.post("/add")
async def add_memory(request: AddMemoryRequest):
    """
    添加记忆

    用于在记忆管理页面手动添加新的全局记忆或规定
    """
    memory_mgr = get_app_state().memory_manager

    if not memory_mgr:
        raise HTTPException(status_code=500, detail="记忆管理器未初始化")

    result = memory_mgr.add_memory(
        content=request.content,
        memory_type=request.memory_type,
        source=request.source,
        metadata=request.metadata
    )

    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error"))

    return result


@router.post("/toggle")
async def toggle_memory(request: ToggleMemoryRequest):
    """
    勾选/取消勾选记忆

    用于启用或禁用某条记忆，被禁用的记忆不会被Agent召回
    """
    memory_mgr = get_app_state().memory_manager

    if not memory_mgr:
        raise HTTPException(status_code=500, detail="记忆管理器未初始化")

    result = memory_mgr.toggle_memory(
        memory_id=request.memory_id,
        enabled=request.enabled
    )

    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error"))

    return result


@router.get("/list")
async def list_memories(memory_type: Optional[str] = None):
    """
    获取所有记忆

    用于记忆管理页面展示记忆列表
    """
    memory_mgr = get_app_state().memory_manager

    if not memory_mgr:
        raise HTTPException(status_code=500, detail="记忆管理器未初始化")

    memories = memory_mgr.get_all_memories(memory_type=memory_type)

    return {
        "success": True,
        "memories": [mem.to_dict() for mem in memories],
        "count": len(memories)
    }


@router.post("/search")
async def search_memories(request: SearchMemoryRequest):
    """
    搜索记忆（语义搜索）

    用于根据查询内容找到相关记忆
    """
    memory_mgr = get_app_state().memory_manager

    if not memory_mgr:
        raise HTTPException(status_code=500, detail="记忆管理器未初始化")

    memories = memory_mgr.search_memories(
        query=request.query,
        memory_type=request.memory_type,
        enabled_only=request.enabled_only,
        limit=request.limit
    )

    return {
        "success": True,
        "memories": [mem.to_dict() for mem in memories],
        "count": len(memories)
    }


@router.delete("/{memory_id}")
async def delete_memory(memory_id: str):
    """
    删除记忆

    用于删除不需要的记忆
    """
    memory_mgr = get_app_state().memory_manager

    if not memory_mgr:
        raise HTTPException(status_code=500, detail="记忆管理器未初始化")

    result = memory_mgr.delete_memory(memory_id=memory_id)

    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error"))

    return result
