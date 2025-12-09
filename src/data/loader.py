"""
数据集加载和处理模块
"""

import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any
from ..utils.logger import get_logger


class DatasetLoader:
    """数据集加载器"""

    def __init__(self, dataset_path: str):
        """
        初始化数据加载器

        Args:
            dataset_path: 数据集文件路径
        """
        self.dataset_path = Path(dataset_path)
        self.df: Optional[pd.DataFrame] = None
        self.logger = get_logger("data.loader")

    def load(self, limit: Optional[int] = None) -> pd.DataFrame:
        """
        加载数据集

        Args:
            limit: 限制加载的行数，None表示加载全部

        Returns:
            DataFrame

        Raises:
            FileNotFoundError: 数据集文件不存在
            ValueError: 数据集格式错误
        """
        if not self.dataset_path.exists():
            raise FileNotFoundError(f"数据集文件不存在: {self.dataset_path}")

        try:
            self.df = pd.read_csv(self.dataset_path)
            self.logger.info(f"数据集加载成功: {len(self.df)}条记录")

            # 验证必需的列
            required_columns = [
                'ID', 'Primary Trait', 'Context', 'Severity',
                'User Prompt to LLM'
            ]
            missing = [col for col in required_columns if col not in self.df.columns]
            if missing:
                raise ValueError(f"数据集缺少必需的列: {missing}")

            # 限制行数
            if limit:
                self.df = self.df.head(limit)
                self.logger.info(f"限制数据集: {len(self.df)}条记录")

            self._print_summary()
            return self.df

        except Exception as e:
            self.logger.error(f"加载数据集失败: {e}")
            raise

    def get_prompts(self) -> list:
        """获取所有prompts"""
        if self.df is None:
            raise ValueError("数据集未加载，请先调用load()")
        return self.df['User Prompt to LLM'].tolist()

    def get_metadata(self, index: int) -> Dict[str, Any]:
        """
        获取指定索引的元数据

        Args:
            index: 行索引

        Returns:
            元数据字典
        """
        if self.df is None:
            raise ValueError("数据集未加载")

        row = self.df.iloc[index]
        return {
            'ID': row['ID'],
            'Primary Trait': row['Primary Trait'],
            'Context': row['Context'],
            'Severity': row['Severity'],
            'User Prompt': row['User Prompt to LLM'],
        }

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取数据集统计信息

        Returns:
            统计信息字典
        """
        if self.df is None:
            raise ValueError("数据集未加载")

        return {
            "total_prompts": len(self.df),
            "by_trait": self.df['Primary Trait'].value_counts().to_dict(),
            "by_severity": self.df['Severity'].value_counts().to_dict(),
            "by_context": self.df['Context'].value_counts().to_dict(),
        }

    def _print_summary(self):
        """打印数据集摘要"""
        if self.df is None:
            return

        self.logger.info(f"总prompts数: {len(self.df)}")
        self.logger.info(f"列: {', '.join(self.df.columns)}")

        # 统计信息
        stats = self.get_statistics()
        self.logger.info(f"按特质: {stats['by_trait']}")
        self.logger.info(f"按严重程度: {stats['by_severity']}")

    def save_subset(self, output_path: str, n: int):
        """
        保存数据集的子集

        Args:
            output_path: 输出文件路径
            n: 前n行
        """
        if self.df is None:
            raise ValueError("数据集未加载")

        subset = self.df.head(n)
        subset.to_csv(output_path, index=False, encoding='utf-8-sig')
        self.logger.info(f"子集已保存: {output_path} ({len(subset)}条)")

    def __len__(self) -> int:
        """返回数据集大小"""
        return len(self.df) if self.df is not None else 0

    def __repr__(self) -> str:
        """字符串表示"""
        if self.df is None:
            return f"DatasetLoader(未加载)"
        return f"DatasetLoader({len(self.df)}条记录)"
