"""
LLM Client - OpenAI封装
支持流式和非流式调用
"""
from typing import List, Dict, Optional, AsyncGenerator
import openai
from openai import OpenAI, AsyncOpenAI
import os


class LLMClient:
    """LLM客户端封装"""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        """
        初始化LLM客户端

        Args:
            api_key: OpenAI API Key
            model: 模型名称
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4")

        if not self.api_key:
            print("⚠️  警告: OpenAI API Key未设置")

        # 同步客户端
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

        # 异步客户端
        self.async_client = AsyncOpenAI(api_key=self.api_key) if self.api_key else None

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
        temperature: float = 0.7
    ) -> AsyncGenerator[str, None]:
        """
        异步流式调用

        Args:
            messages: 消息列表
            model: 模型名称（可选）
            temperature: 温度

        Yields:
            流式内容片段
        """
        if not self.async_client:
            yield "Error: OpenAI异步客户端未初始化"
            return

        try:
            stream = await self.async_client.chat.completions.create(
                model=model or self.model,
                messages=messages,
                temperature=temperature,
                stream=True
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            yield f"Error: {str(e)}"

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
