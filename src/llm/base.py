"""
LLM客户端基类
定义所有LLM客户端的统一接口
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
import time
from ..utils.logger import get_logger


class BaseLLMClient(ABC):
    """LLM客户端抽象基类"""

    def __init__(
        self,
        model_name: str,
        api_key: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        rate_limit_delay: float = 1.0
    ):
        """
        初始化LLM客户端

        Args:
            model_name: 模型名称
            api_key: API密钥
            temperature: 温度参数（0-1）
            max_tokens: 最大token数
            rate_limit_delay: API调用间隔（秒），用于避免限流
        """
        self.model_name = model_name
        self.api_key = api_key
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.rate_limit_delay = rate_limit_delay

        self.logger = get_logger(f"llm.{self.__class__.__name__}")
        self._last_call_time = 0.0

        # 初始化客户端
        self._initialize_client()

    @abstractmethod
    def _initialize_client(self):
        """初始化API客户端（子类实现）"""
        pass

    @abstractmethod
    def _call_api(self, prompt: str) -> Optional[str]:
        """
        调用API（子类实现）

        Args:
            prompt: 用户提示

        Returns:
            模型响应文本，失败返回None
        """
        pass

    def call(self, prompt: str, **kwargs) -> Optional[str]:
        """
        调用LLM（公共接口）

        Args:
            prompt: 用户提示
            **kwargs: 额外参数（可覆盖默认值）

        Returns:
            模型响应文本，失败返回None
        """
        # 实现限流
        self._handle_rate_limit()

        try:
            response = self._call_api(prompt, **kwargs)
            return response
        except Exception as e:
            self.logger.error(f"API调用失败: {e}")
            return None

    def batch_call(
        self,
        prompts: List[str],
        show_progress: bool = True
    ) -> List[Optional[str]]:
        """
        批量调用LLM

        Args:
            prompts: 提示列表
            show_progress: 是否显示进度

        Returns:
            响应列表
        """
        responses = []
        total = len(prompts)

        for i, prompt in enumerate(prompts, 1):
            if show_progress:
                self.logger.info(f"处理 {i}/{total}")

            response = self.call(prompt)
            responses.append(response)

        return responses

    def _handle_rate_limit(self):
        """处理API限流"""
        if self.rate_limit_delay <= 0:
            return

        current_time = time.time()
        time_since_last_call = current_time - self._last_call_time

        if time_since_last_call < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last_call
            time.sleep(sleep_time)

        self._last_call_time = time.time()

    def get_info(self) -> Dict[str, Any]:
        """
        获取客户端信息

        Returns:
            客户端配置信息字典
        """
        return {
            "provider": self.__class__.__name__.replace("Client", ""),
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "rate_limit_delay": self.rate_limit_delay,
        }

    def __repr__(self) -> str:
        """字符串表示"""
        info = self.get_info()
        return f"{info['provider']}Client(model={self.model_name}, temp={self.temperature})"
