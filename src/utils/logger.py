"""
日志系统模块
提供统一的日志记录功能
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


# 自定义日志格式
class ColoredFormatter(logging.Formatter):
    """带颜色的日志格式化器（用于控制台）"""

    # ANSI颜色代码
    COLORS = {
        'DEBUG': '\033[36m',    # 青色
        'INFO': '\033[32m',     # 绿色
        'WARNING': '\033[33m',  # 黄色
        'ERROR': '\033[31m',    # 红色
        'CRITICAL': '\033[35m', # 紫色
        'RESET': '\033[0m',     # 重置
    }

    # Emoji前缀
    EMOJI = {
        'DEBUG': '🔍',
        'INFO': '✅',
        'WARNING': '⚠️',
        'ERROR': '❌',
        'CRITICAL': '🚨',
    }

    def format(self, record):
        """格式化日志记录"""
        # 添加颜色和emoji
        levelname = record.levelname
        color = self.COLORS.get(levelname, self.COLORS['RESET'])
        emoji = self.EMOJI.get(levelname, '')
        reset = self.COLORS['RESET']

        # 格式化消息
        record.levelname = f"{emoji} {levelname}"
        formatted = super().format(record)

        return f"{color}{formatted}{reset}"


def setup_logger(
    name: str,
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    use_colors: bool = True
) -> logging.Logger:
    """
    设置日志记录器

    Args:
        name: 日志记录器名称
        level: 日志级别
        log_file: 日志文件路径，None表示不写入文件
        use_colors: 是否使用彩色输出

    Returns:
        配置好的Logger实例
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 避免重复添加handler
    if logger.handlers:
        return logger

    # 控制台handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    if use_colors:
        console_format = ColoredFormatter(
            '%(levelname)s - %(message)s'
        )
    else:
        console_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # 文件handler（如果指定）
    if log_file:
        # 确保日志目录存在
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    获取日志记录器

    Args:
        name: 日志记录器名称

    Returns:
        Logger实例
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        # 如果还没有配置，使用默认配置
        return setup_logger(name)
    return logger


def create_experiment_logger(experiment_name: str, log_dir: str = "logs") -> logging.Logger:
    """
    为实验创建专用日志记录器

    Args:
        experiment_name: 实验名称
        log_dir: 日志目录

    Returns:
        配置好的Logger实例
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"{log_dir}/{experiment_name}_{timestamp}.log"

    return setup_logger(
        name=f"experiment.{experiment_name}",
        log_file=log_file,
        use_colors=True
    )
