"""
Business Item Model
业务事项数据模型
用于管理企业中的重要事项、待办、跟进任务等
"""
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class ItemType(str, Enum):
    """事项类型"""
    DECISION = "decision"  # 决策事项
    TODO = "todo"  # 待办事项
    FOLLOW_UP = "follow_up"  # 跟进事项
    METRIC = "metric"  # 指标跟踪
    ALERT = "alert"  # 异常告警


class ItemPriority(str, Enum):
    """优先级"""
    LOW = "low"  # 低
    MEDIUM = "medium"  # 中
    HIGH = "high"  # 高
    URGENT = "urgent"  # 紧急


class ItemStatus(str, Enum):
    """状态"""
    PENDING = "pending"  # 待处理
    IN_PROGRESS = "in_progress"  # 进行中
    COMPLETED = "completed"  # 已完成
    CANCELLED = "cancelled"  # 已取消


class BusinessItem(BaseModel):
    """业务事项"""
    id: str
    title: str  # 标题
    description: Optional[str] = None  # 描述
    type: ItemType  # 类型
    priority: ItemPriority  # 优先级
    status: ItemStatus  # 状态

    # 关联信息
    source: Optional[str] = None  # 来源（如：S3客服、S8决策、会议助手）
    source_id: Optional[str] = None  # 来源ID

    # 时间信息
    created_at: str  # 创建时间
    updated_at: str  # 更新时间
    due_date: Optional[str] = None  # 截止日期
    completed_at: Optional[str] = None  # 完成时间

    # 责任人
    assignee: Optional[str] = None  # 负责人

    # 扩展字段
    metadata: Optional[dict] = None  # 额外元数据
    tags: List[str] = []  # 标签


class CreateBusinessItemRequest(BaseModel):
    """创建业务事项请求"""
    title: str
    description: Optional[str] = None
    type: ItemType
    priority: ItemPriority = ItemPriority.MEDIUM
    source: Optional[str] = None
    source_id: Optional[str] = None
    due_date: Optional[str] = None
    assignee: Optional[str] = None
    tags: List[str] = []
    metadata: Optional[dict] = None


class UpdateBusinessItemRequest(BaseModel):
    """更新业务事项请求"""
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[ItemPriority] = None
    status: Optional[ItemStatus] = None
    due_date: Optional[str] = None
    assignee: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[dict] = None


class BusinessItemStats(BaseModel):
    """业务事项统计"""
    total: int
    by_type: dict  # 各类型数量
    by_status: dict  # 各状态数量
    by_priority: dict  # 各优先级数量
    high_priority_pending: int  # 高优先级待处理数量
    overdue: int  # 逾期数量
