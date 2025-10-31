"""
LLM Client - OpenAI封装
支持流式和非流式调用
"""
from typing import List, Dict, Optional, AsyncGenerator
import openai
from openai import OpenAI, AsyncOpenAI
import os


class LLMClient:
    """LLM客户端封装（支持OpenAI/DeepSeek多模式切换）"""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        """
        初始化LLM客户端

        Args:
            api_key: API Key（可选，会自动根据模式选择）
            model: 模型名称（可选，会自动根据模式选择）
        """
        # 🔧 读取LLM模式（openai | deepseek）
        self.llm_mode = os.getenv("LLM_MODE", "openai").lower()

        # 根据模式选择配置
        if self.llm_mode == "deepseek":
            self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
            self.model = model or os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
            self.base_url = "https://api.deepseek.com/v1"
            print(f"🌐 LLM模式: DeepSeek ({self.model}) - 国内直连")
        else:  # openai（默认）
            self.api_key = api_key or os.getenv("OPENAI_API_KEY")
            self.model = model or os.getenv("OPENAI_MODEL", "gpt-4")
            self.base_url = None  # OpenAI默认地址
            print(f"🌐 LLM模式: OpenAI ({self.model})")

        if not self.api_key:
            print(f"⚠️  警告: {self.llm_mode.upper()} API Key未设置")

        # 初始化同步客户端
        if self.api_key:
            client_kwargs = {"api_key": self.api_key}
            if self.base_url:
                client_kwargs["base_url"] = self.base_url
            self.client = OpenAI(**client_kwargs)
        else:
            self.client = None

        # 初始化异步客户端
        if self.api_key:
            async_kwargs = {"api_key": self.api_key}
            if self.base_url:
                async_kwargs["base_url"] = self.base_url
            self.async_client = AsyncOpenAI(**async_kwargs)
        else:
            self.async_client = None

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Dict:
        """
        调用OpenAI Chat Completion

        Args:
            messages: 消息列表
            model: 模型名称（可选）
            temperature: 温度
            max_tokens: 最大token数
            stream: 是否流式输出

        Returns:
            响应结果
        """
        if not self.client:
            return {
                "error": "OpenAI客户端未初始化",
                "content": None
            }

        try:
            response = self.client.chat.completions.create(
                model=model or self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream
            )

            if stream:
                return {"stream": response}
            else:
                return {
                    "content": response.choices[0].message.content,
                    "finish_reason": response.choices[0].finish_reason,
                    "usage": response.usage.model_dump() if response.usage else None
                }

        except Exception as e:
            return {
                "error": f"LLM调用失败: {str(e)}",
                "content": None
            }

    async def async_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Dict:
        """
        异步调用OpenAI Chat Completion

        Args:
            messages: 消息列表
            model: 模型名称（可选）
            temperature: 温度
            max_tokens: 最大token数

        Returns:
            响应结果
        """
        if not self.async_client:
            return {
                "error": "OpenAI异步客户端未初始化",
                "content": None
            }

        try:
            response = await self.async_client.chat.completions.create(
                model=model or self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )

            return {
                "content": response.choices[0].message.content,
                "finish_reason": response.choices[0].finish_reason,
                "usage": response.usage.model_dump() if response.usage else None
            }

        except Exception as e:
            return {
                "error": f"LLM调用失败: {str(e)}",
                "content": None
            }

    async def async_chat_completion_stream(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        tools: Optional[List[Dict]] = None
    ) -> AsyncGenerator[Dict, None]:
        """
        异步流式调用（支持 Function Calling）

        Args:
            messages: 消息列表
            model: 模型名称（可选）
            temperature: 温度
            tools: OpenAI tools 定义（可选）

        Yields:
            流式数据包：
            - {"type": "content", "content": "..."}  # 文本内容
            - {"type": "tool_call", "tool_call": {...}}  # 工具调用
            - {"type": "done", "finish_reason": "..."}  # 完成
        """
        if not self.async_client:
            yield {"type": "error", "error": "OpenAI异步客户端未初始化"}
            return

        try:
            kwargs = {
                "model": model or self.model,
                "messages": messages,
                "temperature": temperature,
                "stream": True
            }

            # 如果提供了 tools，添加到请求中
            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"

            stream = await self.async_client.chat.completions.create(**kwargs)

            tool_calls_buffer = []  # 累积工具调用

            async for chunk in stream:
                delta = chunk.choices[0].delta
                finish_reason = chunk.choices[0].finish_reason

                # 文本内容
                if delta.content:
                    yield {"type": "content", "content": delta.content}

                # 工具调用
                if delta.tool_calls:
                    for tool_call in delta.tool_calls:
                        index = tool_call.index

                        # 确保buffer有足够的空间
                        while len(tool_calls_buffer) <= index:
                            tool_calls_buffer.append({
                                "id": "",
                                "type": "function",
                                "function": {"name": "", "arguments": ""}
                            })

                        # 累积工具调用数据
                        if tool_call.id:
                            tool_calls_buffer[index]["id"] = tool_call.id
                        if tool_call.function:
                            if tool_call.function.name:
                                tool_calls_buffer[index]["function"]["name"] = tool_call.function.name
                            if tool_call.function.arguments:
                                tool_calls_buffer[index]["function"]["arguments"] += tool_call.function.arguments

                # 完成
                if finish_reason:
                    # 如果有工具调用，发送完整的工具调用数据
                    if tool_calls_buffer:
                        yield {
                            "type": "tool_calls",
                            "tool_calls": tool_calls_buffer,
                            "finish_reason": finish_reason
                        }

                    yield {
                        "type": "done",
                        "finish_reason": finish_reason
                    }

        except Exception as e:
            yield {"type": "error", "error": str(e)}

    def build_messages_with_memory(
        self,
        system_prompt: str,
        user_input: str,
        memory_context: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> List[Dict[str, str]]:
        """
        构建带记忆的消息列表

        Args:
            system_prompt: 系统提示词
            user_input: 用户输入
            memory_context: 记忆上下文
            conversation_history: 对话历史

        Returns:
            消息列表
        """
        messages = [
            {
                "role": "system",
                "content": f"{system_prompt}\n\n{memory_context}"
            }
        ]

        # 添加对话历史
        if conversation_history:
            messages.extend(conversation_history)

        # 添加用户输入
        messages.append({
            "role": "user",
            "content": user_input
        })

        return messages


# 单例模式（可选）
_llm_client_instance = None


def get_llm_client() -> LLMClient:
    """获取LLM客户端单例"""
    global _llm_client_instance
    if _llm_client_instance is None:
        _llm_client_instance = LLMClient()
    return _llm_client_instance
