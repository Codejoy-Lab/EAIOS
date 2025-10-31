"""
MCP Tools - Model Context Protocol工具层
用于连接各种数据源（CRM、文档、数据库等）
"""
from typing import Dict, List, Optional, Any
import json
import os


class MCPTool:
    """MCP工具基类"""

    def __init__(self, name: str, description: str):
        """
        初始化工具

        Args:
            name: 工具名称
            description: 工具描述
        """
        self.name = name
        self.description = description

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        执行工具

        Args:
            **kwargs: 工具参数

        Returns:
            执行结果，包含：
            - data: 数据
            - source: 来源信息
        """
        raise NotImplementedError("子类必须实现execute方法")

    def get_schema(self) -> Dict:
        """
        获取工具的JSON Schema

        Returns:
            工具schema
        """
        raise NotImplementedError("子类必须实现get_schema方法")


class CRMTool(MCPTool):
    """CRM查询工具"""

    def __init__(self, data_path: Optional[str] = None):
        super().__init__(
            name="query_crm",
            description="查询CRM客户信息、商机、线索等"
        )
        self.data_path = data_path or "backend/data/crm_data.json"

    async def execute(self, customer_id: Optional[str] = None, query_type: str = "customer") -> Dict:
        """
        查询CRM

        Args:
            customer_id: 客户ID
            query_type: 查询类型（customer/lead/opportunity）

        Returns:
            CRM数据
        """
        try:
            # 从模拟数据文件加载
            if os.path.exists(self.data_path):
                with open(self.data_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = self._get_mock_data()

            # 查询逻辑
            if customer_id:
                result = data.get("customers", {}).get(customer_id, {})
            else:
                result = data.get(query_type, {})

            return {
                "data": result,
                "source": {
                    "system": "CRM系统",
                    "table": f"{query_type}_table",
                    "timestamp": "2025-10-29T10:00:00",
                    "responsible": "销售团队"
                }
            }

        except Exception as e:
            return {
                "data": None,
                "error": str(e),
                "source": {"system": "CRM系统"}
            }

    def _get_mock_data(self) -> Dict:
        """获取模拟数据"""
        return {
            "customers": {
                "C001": {
                    "name": "张三",
                    "status": "意向客户",
                    "last_contact": "2025-10-20",
                    "stage": "需求确认"
                }
            }
        }

    def get_schema(self) -> Dict:
        return {
            "type": "object",
            "properties": {
                "customer_id": {"type": "string", "description": "客户ID"},
                "query_type": {"type": "string", "enum": ["customer", "lead", "opportunity"]}
            }
        }


class DocumentTool(MCPTool):
    """文档查询工具"""

    def __init__(self, data_path: Optional[str] = None):
        super().__init__(
            name="query_documents",
            description="查询企业文档、知识库、会议纪要等"
        )
        self.data_path = data_path or "backend/data/documents.json"

    async def execute(self, query: str, doc_type: str = "all") -> Dict:
        """
        查询文档

        Args:
            query: 查询内容
            doc_type: 文档类型（all/meeting/policy/report）

        Returns:
            文档数据
        """
        try:
            # 从模拟数据文件加载
            if os.path.exists(self.data_path):
                with open(self.data_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = self._get_mock_data()

            # 简单的关键词匹配
            results = []
            for doc in data.get("documents", []):
                if doc_type != "all" and doc.get("type") != doc_type:
                    continue
                if query.lower() in doc.get("content", "").lower():
                    results.append(doc)

            return {
                "data": results,
                "source": {
                    "system": "文档系统",
                    "database": "企业知识库",
                    "timestamp": "2025-10-29T10:00:00"
                }
            }

        except Exception as e:
            return {
                "data": [],
                "error": str(e),
                "source": {"system": "文档系统"}
            }

    def _get_mock_data(self) -> Dict:
        """获取模拟数据"""
        return {
            "documents": [
                {
                    "id": "DOC001",
                    "type": "meeting",
                    "title": "Q4营销策略会议",
                    "content": "会议决定Q4主推三大产品线...",
                    "date": "2025-10-15"
                }
            ]
        }

    def get_schema(self) -> Dict:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "查询关键词"},
                "doc_type": {"type": "string", "enum": ["all", "meeting", "policy", "report"]}
            },
            "required": ["query"]
        }


class DataAnalyticsTool(MCPTool):
    """数据分析工具"""

    def __init__(self, data_path: Optional[str] = None):
        super().__init__(
            name="query_analytics",
            description="查询业务指标、数据报表等"
        )
        self.data_path = data_path or "backend/data/analytics.json"

    async def execute(self, metric: str, time_range: str = "last_7_days") -> Dict:
        """
        查询数据指标

        Args:
            metric: 指标名称（revenue/users/conversion_rate等）
            time_range: 时间范围

        Returns:
            指标数据
        """
        try:
            # 从模拟数据文件加载
            if os.path.exists(self.data_path):
                with open(self.data_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = self._get_mock_data()

            result = data.get("metrics", {}).get(metric, {})

            return {
                "data": result,
                "source": {
                    "system": "数据分析平台",
                    "metric": metric,
                    "time_range": time_range,
                    "timestamp": "2025-10-29T10:00:00"
                }
            }

        except Exception as e:
            return {
                "data": None,
                "error": str(e),
                "source": {"system": "数据分析平台"}
            }

    def _get_mock_data(self) -> Dict:
        """获取模拟数据"""
        return {
            "metrics": {
                "conversion_rate": {
                    "current": 3.2,
                    "previous": 4.1,
                    "change": -0.9,
                    "trend": "下降"
                }
            }
        }

    def get_schema(self) -> Dict:
        return {
            "type": "object",
            "properties": {
                "metric": {"type": "string", "description": "指标名称"},
                "time_range": {"type": "string", "description": "时间范围"}
            },
            "required": ["metric"]
        }


class BusinessItemsTool(MCPTool):
    """业务事项查询工具"""

    def __init__(self):
        super().__init__(
            name="query_business_items",
            description="查询企业业务事项（决策事项、待办、跟进任务等），支持按状态、优先级、类型筛选"
        )

    async def execute(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        item_type: Optional[str] = None,
        limit: int = 10
    ) -> Dict:
        """
        查询业务事项

        Args:
            status: 状态筛选 (pending/in_progress/completed/cancelled)
            priority: 优先级筛选 (low/medium/high/urgent)
            item_type: 类型筛选 (decision/todo/follow_up/metric/alert)
            limit: 返回数量

        Returns:
            业务事项列表
        """
        try:
            import os
            data_file = os.path.join(os.path.dirname(__file__), "..", "..", "data", "business_items.json")

            if os.path.exists(data_file):
                with open(data_file, 'r', encoding='utf-8') as f:
                    items = json.load(f)
            else:
                items = []

            # 过滤
            filtered = items
            if status:
                filtered = [item for item in filtered if item.get("status") == status]
            if priority:
                filtered = [item for item in filtered if item.get("priority") == priority]
            if item_type:
                filtered = [item for item in filtered if item.get("type") == item_type]

            # 排序：按更新时间倒序
            filtered.sort(key=lambda x: x.get("updated_at", ""), reverse=True)

            # 限制数量
            filtered = filtered[:limit]

            # 统计
            stats = {
                "total": len(filtered),
                "by_status": {},
                "by_priority": {}
            }

            for item in filtered:
                s = item.get("status", "pending")
                p = item.get("priority", "medium")
                stats["by_status"][s] = stats["by_status"].get(s, 0) + 1
                stats["by_priority"][p] = stats["by_priority"].get(p, 0) + 1

            return {
                "data": {
                    "items": filtered,
                    "stats": stats
                },
                "source": {
                    "system": "业务事项管理系统",
                    "description": "企业重要事项、待办、跟进任务等",
                    "responsible": "各部门负责人"
                }
            }

        except Exception as e:
            return {
                "data": None,
                "error": str(e),
                "source": {"system": "业务事项管理系统"}
            }

    def get_schema(self) -> Dict:
        return {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "description": "状态筛选",
                    "enum": ["pending", "in_progress", "completed", "cancelled"]
                },
                "priority": {
                    "type": "string",
                    "description": "优先级筛选",
                    "enum": ["low", "medium", "high", "urgent"]
                },
                "item_type": {
                    "type": "string",
                    "description": "事项类型",
                    "enum": ["decision", "todo", "follow_up", "metric", "alert"]
                },
                "limit": {
                    "type": "integer",
                    "description": "返回数量",
                    "default": 10
                }
            }
        }


class S6AnalyticsReportTool(MCPTool):
    """S6数据分析报告工具"""

    def __init__(self):
        super().__init__(
            name="get_s6_report",
            description="获取S6数据分析中台的综合分析报告，包含各场景关键指标、异常告警、跨场景洞察"
        )

    async def execute(self, scenario: Optional[str] = None) -> Dict:
        """
        获取S6分析报告

        Args:
            scenario: 场景名称（如 s3_customer_service），留空则获取全局报告

        Returns:
            分析报告数据
        """
        try:
            from app.core.data_analyzer import get_data_analyzer

            analyzer = get_data_analyzer()

            if scenario:
                # 获取单个场景摘要
                result = analyzer.get_scenario_summary(scenario)
            else:
                # 获取完整报告
                result = analyzer.get_latest_report()

            return {
                "data": result,
                "source": {
                    "system": "S6数据分析中台",
                    "description": "汇总各场景metrics，进行智能分析",
                    "timestamp": result.get("generated_at"),
                    "responsible": "数据分析团队"
                }
            }

        except Exception as e:
            return {
                "data": None,
                "error": str(e),
                "source": {"system": "S6数据分析中台"}
            }

    def get_schema(self) -> Dict:
        return {
            "type": "object",
            "properties": {
                "scenario": {
                    "type": "string",
                    "description": "场景名称（可选），如 s3_customer_service、s1_marketing等。留空则获取全局报告",
                    "enum": ["s3_customer_service", "s1_marketing", "s2_sales", "s4_content", "s5_process", "s7_compliance", None]
                }
            }
        }


class MCPToolRegistry:
    """MCP工具注册表"""

    def __init__(self):
        self.tools: Dict[str, MCPTool] = {}

    def register(self, tool: MCPTool):
        """注册工具"""
        self.tools[tool.name] = tool

    def get_tool(self, name: str) -> Optional[MCPTool]:
        """获取工具"""
        return self.tools.get(name)

    def list_tools(self) -> List[Dict]:
        """列出所有工具"""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "schema": tool.get_schema()
            }
            for tool in self.tools.values()
        ]


# 全局工具注册表
_tool_registry = MCPToolRegistry()


def get_tool_registry() -> MCPToolRegistry:
    """获取工具注册表单例"""
    return _tool_registry


def init_default_tools():
    """初始化默认工具"""
    registry = get_tool_registry()
    registry.register(CRMTool())
    registry.register(DocumentTool())
    registry.register(DataAnalyticsTool())
    registry.register(BusinessItemsTool())
    registry.register(S6AnalyticsReportTool())
    print("✅ MCP工具初始化完成（含业务事项查询和S6报告）")
