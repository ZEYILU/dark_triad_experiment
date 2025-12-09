"""
OpenAI客户端实现
支持GPT-4, GPT-3.5等模型
"""

from typing import Optional
from .base import BaseLLMClient

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class OpenAIClient(BaseLLMClient):
    """OpenAI API客户端"""

    def __init__(
        self,
        model_name: str = "gpt-4",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        **kwargs
    ):
        """
        初始化OpenAI客户端

        Args:
            model_name: 模型名称 (e.g., "gpt-4", "gpt-3.5-turbo")
            api_key: API密钥
            base_url: 自定义API地址（可选，用于兼容的API）
            **kwargs: 其他参数（temperature, max_tokens等）
        """
        if not OPENAI_AVAILABLE:
            raise ImportError(
                "OpenAI库未安装。请运行: pip install openai"
            )

        if not api_key:
            raise ValueError("OpenAI API密钥不能为空")

        self.base_url = base_url
        self.client = None

        super().__init__(model_name, api_key, **kwargs)

    def _initialize_client(self):
        """初始化OpenAI客户端"""
        client_kwargs = {"api_key": self.api_key}
        if self.base_url:
            client_kwargs["base_url"] = self.base_url

        self.client = OpenAI(**client_kwargs)
        self.logger.info(f"OpenAI客户端初始化成功: {self.model_name}")

    def _call_api(self, prompt: str, **kwargs) -> Optional[str]:
        """
        调用OpenAI API

        Args:
            prompt: 用户提示
            **kwargs: 额外参数

        Returns:
            模型响应文本
        """
        # 合并参数（kwargs可以覆盖默认值）
        temperature = kwargs.get("temperature", self.temperature)
        max_tokens = kwargs.get("max_tokens", self.max_tokens)

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )

            return response.choices[0].message.content

        except Exception as e:
            self.logger.error(f"OpenAI API错误: {e}")
            return None
