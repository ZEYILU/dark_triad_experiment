"""
Anthropic Claude客户端实现
支持Claude 3系列模型
"""

from typing import Optional
from .base import BaseLLMClient

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class AnthropicClient(BaseLLMClient):
    """Anthropic Claude API客户端"""

    def __init__(
        self,
        model_name: str = "claude-3-haiku-20240307",
        api_key: Optional[str] = None,
        **kwargs
    ):
        """
        初始化Anthropic客户端

        Args:
            model_name: 模型名称 (e.g., "claude-3-opus-20240229")
            api_key: API密钥
            **kwargs: 其他参数（temperature, max_tokens等）
        """
        if not ANTHROPIC_AVAILABLE:
            raise ImportError(
                "Anthropic库未安装。请运行: pip install anthropic"
            )

        if not api_key:
            raise ValueError("Anthropic API密钥不能为空")

        self.client = None
        super().__init__(model_name, api_key, **kwargs)

    def _initialize_client(self):
        """初始化Anthropic客户端"""
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.logger.info(f"Anthropic客户端初始化成功: {self.model_name}")

    def _call_api(self, prompt: str, **kwargs) -> Optional[str]:
        """
        调用Anthropic API

        Args:
            prompt: 用户提示
            **kwargs: 额外参数

        Returns:
            模型响应文本
        """
        # 合并参数
        temperature = kwargs.get("temperature", self.temperature)
        max_tokens = kwargs.get("max_tokens", self.max_tokens)

        try:
            message = self.client.messages.create(
                model=self.model_name,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}]
            )

            return message.content[0].text

        except Exception as e:
            self.logger.error(f"Anthropic API错误: {e}")
            return None
