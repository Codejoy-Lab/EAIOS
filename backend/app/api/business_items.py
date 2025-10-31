"""
Business Items API
业务事项管理API
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime
import json
import os
from app.models.business_item import (
    BusinessItem,
    CreateBusinessItemRequest,
    UpdateBusinessItemRequest,
    BusinessItemStats,
    ItemType,
    ItemStatus,
    ItemPriority
)

router = APIRouter()

# 数据存储路径
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
ITEMS_FILE = os.path.join(DATA_DIR, "business_items.json")


def _load_items() -> List[dict]:
    """加载业务事项"""
    if not os.path.exists(ITEMS_FILE):
        return []

    try:
        with open(ITEMS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️  加载业务事项失败: {e}")
        return []


def _save_items(items: List[dict]):
    """保存业务事项"""
    os.makedirs(DATA_DIR, exist_ok=True)

    try:
        with open(ITEMS_FILE, "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️  保存业务事项失败: {e}")
        raise HTTPException(status_code=500, detail=f"保存失败: {str(e)}")


@router.post("/create", response_model=BusinessItem)
async def create_item(req: CreateBusinessItemRequest):
    """创建业务事项"""
    items = _load_items()

    # 生成ID
    item_id = f"item_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(items)}"

    # 创建事项
    item = {
        "id": item_id,
        "title": req.title,
        "description": req.description,
        "type": req.type,
        "priority": req.priority,
        "status": ItemStatus.PENDING,
        "source": req.source,
        "source_id": req.source_id,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "due_date": req.due_date,
        "completed_at": None,
        "assignee": req.assignee,
        "metadata": req.metadata or {},
        "tags": req.tags or []
    }

    items.append(item)
    _save_items(items)

    print(f"✅ 创建业务事项: {item['title']} ({item['type']})")

    return BusinessItem(**item)


@router.get("/list", response_model=List[BusinessItem])
async def list_items(
    type: Optional[ItemType] = None,
    status: Optional[ItemStatus] = None,
    priority: Optional[ItemPriority] = None,
    source: Optional[str] = None,
    limit: int = 100
):
    """获取业务事项列表"""
    items = _load_items()

    # 过滤
    if type:
        items = [item for item in items if item.get("type") == type]

    if status:
        items = [item for item in items if item.get("status") == status]

    if priority:
        items = [item for item in items if item.get("priority") == priority]

    if source:
        items = [item for item in items if item.get("source") == source]

    # 按更新时间倒序
    items.sort(key=lambda x: x.get("updated_at", ""), reverse=True)

    # 限制数量
    items = items[:limit]

    return [BusinessItem(**item) for item in items]


@router.get("/{item_id}", response_model=BusinessItem)
async def get_item(item_id: str):
    """获取单个业务事项"""
    items = _load_items()

    for item in items:
        if item.get("id") == item_id:
            return BusinessItem(**item)

    raise HTTPException(status_code=404, detail="业务事项不存在")


@router.put("/{item_id}", response_model=BusinessItem)
async def update_item(item_id: str, req: UpdateBusinessItemRequest):
    """更新业务事项"""
    items = _load_items()

    # 查找事项
    found = False
    for i, item in enumerate(items):
        if item.get("id") == item_id:
            found = True

            # 更新字段
            if req.title is not None:
                item["title"] = req.title
            if req.description is not None:
                item["description"] = req.description
            if req.priority is not None:
                item["priority"] = req.priority
            if req.status is not None:
                item["status"] = req.status
                # 如果状态变为已完成，记录完成时间
                if req.status == ItemStatus.COMPLETED and not item.get("completed_at"):
                    item["completed_at"] = datetime.now().isoformat()
            if req.due_date is not None:
                item["due_date"] = req.due_date
            if req.assignee is not None:
                item["assignee"] = req.assignee
            if req.tags is not None:
                item["tags"] = req.tags
            if req.metadata is not None:
                item["metadata"] = {**item.get("metadata", {}), **req.metadata}

            item["updated_at"] = datetime.now().isoformat()

            items[i] = item
            break

    if not found:
        raise HTTPException(status_code=404, detail="业务事项不存在")

    _save_items(items)

    print(f"✅ 更新业务事项: {item['title']}")

    return BusinessItem(**item)


@router.delete("/{item_id}")
async def delete_item(item_id: str):
    """删除业务事项"""
    items = _load_items()

    # 查找并删除
    found = False
    new_items = []
    for item in items:
        if item.get("id") == item_id:
            found = True
            print(f"🗑️  删除业务事项: {item['title']}")
        else:
            new_items.append(item)

    if not found:
        raise HTTPException(status_code=404, detail="业务事项不存在")

    _save_items(new_items)

    return {"success": True, "message": "业务事项已删除"}


@router.get("/stats/summary", response_model=BusinessItemStats)
async def get_stats():
    """获取业务事项统计"""
    items = _load_items()

    if not items:
        return BusinessItemStats(
            total=0,
            by_type={},
            by_status={},
            by_priority={},
            high_priority_pending=0,
            overdue=0
        )

    # 统计各类型数量
    by_type = {}
    for item in items:
        item_type = item.get("type", "other")
        by_type[item_type] = by_type.get(item_type, 0) + 1

    # 统计各状态数量
    by_status = {}
    for item in items:
        status = item.get("status", "pending")
        by_status[status] = by_status.get(status, 0) + 1

    # 统计各优先级数量
    by_priority = {}
    for item in items:
        priority = item.get("priority", "medium")
        by_priority[priority] = by_priority.get(priority, 0) + 1

    # 高优先级待处理
    high_priority_pending = len([
        item for item in items
        if item.get("priority") in ["high", "urgent"]
        and item.get("status") == "pending"
    ])

    # 逾期事项
    now = datetime.now()
    overdue = 0
    for item in items:
        if item.get("due_date") and item.get("status") != "completed":
            try:
                due_date = datetime.fromisoformat(item["due_date"])
                if due_date < now:
                    overdue += 1
            except:
                pass

    return BusinessItemStats(
        total=len(items),
        by_type=by_type,
        by_status=by_status,
        by_priority=by_priority,
        high_priority_pending=high_priority_pending,
        overdue=overdue
    )
