"""
MCP HTTP Client
用于调用 Streamable HTTP 模式的 MCP Server
"""
import httpx
import json
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class MCPTool(BaseModel):
    """MCP 工具定义"""
    name: str
    description: str
    inputSchema: Dict[str, Any]


class MCPClient:
    """MCP HTTP 客户端"""

    def __init__(self, endpoint_url: str):
        """
        初始化 MCP 客户端

        Args:
            endpoint_url: MCP Server 的 HTTP 端点 URL
        """
        self.endpoint_url = endpoint_url
        self.client = httpx.Client(timeout=30.0)
        self._tools_cache: Optional[List[MCPTool]] = None

    def _make_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        发送 JSON-RPC 请求到 MCP Server

        Args:
            method: JSON-RPC 方法名
            params: 方法参数

        Returns:
            响应结果
        """
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": 1
        }

        try:
            response = self.client.post(
                self.endpoint_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            result = response.json()

            if "error" in result:
                raise Exception(f"MCP Error: {result['error']}")

            return result.get("result", {})
        except httpx.HTTPError as e:
            raise Exception(f"MCP HTTP Error: {str(e)}")

    def list_tools(self, use_cache: bool = True) -> List[MCPTool]:
        """
        获取 MCP Server 提供的所有工具

        Args:
            use_cache: 是否使用缓存

        Returns:
            工具列表
        """
        if use_cache and self._tools_cache:
            return self._tools_cache

        result = self._make_request("tools/list")
        tools = [MCPTool(**tool) for tool in result.get("tools", [])]
        self._tools_cache = tools
        return tools

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        调用 MCP 工具

        Args:
            tool_name: 工具名称
            arguments: 工具参数

        Returns:
            工具执行结果
        """
        params = {
            "name": tool_name,
            "arguments": arguments
        }

        result = self._make_request("tools/call", params)
        return result

    def get_tools_for_openai(self) -> List[Dict[str, Any]]:
        """
        将 MCP 工具转换为 OpenAI Function Calling 格式

        Returns:
            OpenAI tools 格式的工具列表
        """
        mcp_tools = self.list_tools()
        openai_tools = []

        for tool in mcp_tools:
            openai_tool = {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema
                }
            }
            openai_tools.append(openai_tool)

        return openai_tools

    def close(self):
        """关闭 HTTP 客户端"""
        self.client.close()
