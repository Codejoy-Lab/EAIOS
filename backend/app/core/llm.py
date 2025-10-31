"""
LLM Client - OpenAI封装
支持流式和非流式调用
"""
from typing import List, Dict, Optional, AsyncGenerator
import openai
from openai import OpenAI, AsyncOpenAI
import os


class LLMClient:
    """LLM客户端封装（支持OpenAI/DeepSeek多模式切换+自动降级）"""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        """
        初始化LLM客户端

        Args:
            api_key: API Key（可选，会自动根据模式选择）
            model: 模型名称（可选，会自动根据模式选择）
        """
        # 🔧 读取LLM模式（auto | openai | deepseek）
        self.llm_mode = os.getenv("LLM_MODE", "auto").lower()

        # 根据模式选择配置
        if self.llm_mode == "auto":
            # 自动降级模式：同时初始化两个客户端
            print(f"🌐 LLM模式: 自动降级（OpenAI优先 → DeepSeek兜底）")

            # OpenAI配置
            self.openai_api_key = os.getenv("OPENAI_API_KEY")
            self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4")

            # DeepSeek配置
            self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
            self.deepseek_model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

            # 初始化OpenAI客户端
            if self.openai_api_key:
                self.openai_async_client = AsyncOpenAI(api_key=self.openai_api_key)
                print(f"  ✅ OpenAI ({self.openai_model}) 已就绪")
            else:
                self.openai_async_client = None
                print(f"  ⚠️  OpenAI API Key未设置")

            # 初始化DeepSeek客户端
            if self.deepseek_api_key:
                self.deepseek_async_client = AsyncOpenAI(
                    api_key=self.deepseek_api_key,
                    base_url="https://api.deepseek.com/v1"
                )
                print(f"  ✅ DeepSeek ({self.deepseek_model}) 已就绪（兜底）")
            else:
                self.deepseek_async_client = None
                print(f"  ⚠️  DeepSeek API Key未设置")

            # 为了兼容旧代码，设置默认客户端
            self.async_client = self.openai_async_client
            self.api_key = self.openai_api_key
            self.model = self.openai_model

        elif self.llm_mode == "deepseek":
            # DeepSeek模式
            self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
            self.model = model or os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
            self.base_url = "https://api.deepseek.com/v1"
            print(f"🌐 LLM模式: DeepSeek ({self.model}) - 国内直连")

            if self.api_key:
                self.async_client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
            else:
                self.async_client = None
                print(f"⚠️  警告: DeepSeek API Key未设置")

        else:  # openai（默认）
            # OpenAI模式
            self.api_key = api_key or os.getenv("OPENAI_API_KEY")
            self.model = model or os.getenv("OPENAI_MODEL", "gpt-4")
            self.base_url = None  # OpenAI默认地址
            print(f"🌐 LLM模式: OpenAI ({self.model})")

            if self.api_key:
                self.async_client = AsyncOpenAI(api_key=self.api_key)
            else:
                self.async_client = None
                print(f"⚠️  警告: OpenAI API Key未设置")

        # 初始化同步客户端（简化版，仅支持主模式）
        if hasattr(self, 'api_key') and self.api_key:
            client_kwargs = {"api_key": self.api_key}
            if hasattr(self, 'base_url') and self.base_url:
                client_kwargs["base_url"] = self.base_url
            self.client = OpenAI(**client_kwargs)
        else:
            self.client = None

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
        异步流式调用（支持 Function Calling + 自动降级）

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
        # 自动降级模式
        if self.llm_mode == "auto":
            # 优先尝试 OpenAI
            if self.openai_async_client:
                try:
                    print(f"🚀 尝试使用 OpenAI ({self.openai_model})...")
                    async for chunk in self._stream_with_client(
                        self.openai_async_client,
                        self.openai_model,
                        messages,
                        temperature,
                        tools
                    ):
                        yield chunk
                    print(f"✅ OpenAI 调用成功")
                    return  # 成功，直接返回

                except Exception as e:
                    error_msg = str(e)
                    print(f"⚠️  OpenAI 调用失败: {error_msg}")

                    # 判断是否是超时或网络错误
                    if "timeout" in error_msg.lower() or "timed out" in error_msg.lower() or "connection" in error_msg.lower():
                        # 自动切换到 DeepSeek
                        if self.deepseek_async_client:
                            print(f"🔄 自动切换到 DeepSeek ({self.deepseek_model})...")
                            try:
                                async for chunk in self._stream_with_client(
                                    self.deepseek_async_client,
                                    self.deepseek_model,
                                    messages,
                                    temperature,
                                    tools
                                ):
                                    yield chunk
                                print(f"✅ DeepSeek 兜底成功")
                                return
                            except Exception as e2:
                                yield {"type": "error", "error": f"OpenAI和DeepSeek均失败: {error_msg}, {str(e2)}"}
                                return
                        else:
                            yield {"type": "error", "error": f"OpenAI失败且DeepSeek未配置: {error_msg}"}
                            return
                    else:
                        # 非网络错误，直接返回错误
                        yield {"type": "error", "error": error_msg}
                        return

            # 如果 OpenAI 未配置，直接使用 DeepSeek
            elif self.deepseek_async_client:
                print(f"🌐 OpenAI未配置，使用 DeepSeek ({self.deepseek_model})...")
                async for chunk in self._stream_with_client(
                    self.deepseek_async_client,
                    self.deepseek_model,
                    messages,
                    temperature,
                    tools
                ):
                    yield chunk
                return

            else:
                yield {"type": "error", "error": "OpenAI和DeepSeek均未配置"}
                return

        # 单一模式（openai 或 deepseek）
        else:
            if not self.async_client:
                yield {"type": "error", "error": "异步客户端未初始化"}
                return

            async for chunk in self._stream_with_client(
                self.async_client,
                model or self.model,
                messages,
                temperature,
                tools
            ):
                yield chunk

    async def _stream_with_client(
        self,
        client: AsyncOpenAI,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float,
        tools: Optional[List[Dict]] = None
    ) -> AsyncGenerator[Dict, None]:
        """
        使用指定客户端进行流式调用（内部方法）
        """
        try:
            kwargs = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "stream": True
            }

            # 如果提供了 tools，添加到请求中
            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"

            stream = await client.chat.completions.create(**kwargs)

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
            raise e  # 向上抛出，由调用方处理

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
