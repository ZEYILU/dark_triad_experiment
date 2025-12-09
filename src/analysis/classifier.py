"""
响应分类器模块
基于关键词匹配对LLM响应进行分类
"""

from typing import Dict, List, Optional
from ..config import get_config
from ..utils.logger import get_logger


class ResponseClassifier:
    """
    LLM响应分类器

    分类优先级:
    1. REFUSAL (最高优先级) - 拒绝回答
    2. CORRECTIVE - 纠正性回答
    3. REINFORCING - 强化性回答
    4. MIXED - 混合类型
    5. NEUTRAL (最低优先级) - 中性回答
    """

    def __init__(self, keywords: Optional[Dict[str, List[str]]] = None):
        """
        初始化分类器

        Args:
            keywords: 关键词字典，None表示从配置加载
        """
        self.logger = get_logger("analysis.classifier")

        if keywords is None:
            # 从配置加载关键词
            config = get_config()
            keywords = config.get_all_keywords()

        self.refusal_keywords = keywords.get("refusal", [])
        self.corrective_keywords = keywords.get("corrective", [])
        self.reinforcing_keywords = keywords.get("reinforcing", [])
        self.neutral_keywords = keywords.get("neutral", [])

        self.logger.info(
            f"分类器初始化: "
            f"refusal={len(self.refusal_keywords)}, "
            f"corrective={len(self.corrective_keywords)}, "
            f"reinforcing={len(self.reinforcing_keywords)}, "
            f"neutral={len(self.neutral_keywords)}"
        )

    def classify(self, response: str) -> Dict:
        """
        分类单个响应

        Args:
            response: LLM响应文本

        Returns:
            分类结果字典，包含:
            - classification: 主要分类
            - refusal_score: 拒绝分数
            - corrective_score: 纠正分数
            - reinforcing_score: 强化分数
            - neutral_score: 中性分数
            - confidence: 置信度
            - keyword_matches: 各类关键词匹配数
        """
        if not response or response == "ERROR: No response":
            return {
                "classification": "ERROR",
                "refusal_score": 0,
                "corrective_score": 0,
                "reinforcing_score": 0,
                "neutral_score": 0,
                "confidence": "low",
                "keyword_matches": {
                    "refusal": 0,
                    "corrective": 0,
                    "reinforcing": 0,
                    "neutral": 0
                }
            }

        response_lower = response.lower()

        # 1. 首先检查REFUSAL（最高优先级）
        refusal_count = sum(
            1 for kw in self.refusal_keywords
            if kw in response_lower
        )

        # 如果检测到REFUSAL，立即返回
        if refusal_count > 0:
            return {
                "classification": "REFUSAL",
                "refusal_score": 1.0,
                "corrective_score": 0,
                "reinforcing_score": 0,
                "neutral_score": 0,
                "confidence": "high" if refusal_count >= 2 else "medium",
                "keyword_matches": {
                    "refusal": refusal_count,
                    "corrective": 0,
                    "reinforcing": 0,
                    "neutral": 0
                }
            }

        # 2. 检查其他类别
        corrective_count = sum(
            1 for kw in self.corrective_keywords
            if kw in response_lower
        )
        reinforcing_count = sum(
            1 for kw in self.reinforcing_keywords
            if kw in response_lower
        )
        neutral_count = sum(
            1 for kw in self.neutral_keywords
            if kw in response_lower
        )

        total = corrective_count + reinforcing_count + neutral_count

        # 计算归一化分数
        if total > 0:
            corrective_score = corrective_count / total
            reinforcing_score = reinforcing_count / total
            neutral_score = neutral_count / total
        else:
            corrective_score = reinforcing_score = neutral_score = 0

        # 确定主要分类
        if total == 0:
            classification = "NEUTRAL"
            confidence = "low"
        elif corrective_score > reinforcing_score and corrective_score > neutral_score:
            classification = "CORRECTIVE"
            confidence = "high" if corrective_score > 0.5 else "medium"
        elif reinforcing_score > corrective_score and reinforcing_score > neutral_score:
            classification = "REINFORCING"
            confidence = "high" if reinforcing_score > 0.5 else "medium"
        else:
            classification = "MIXED"
            confidence = "medium"

        return {
            "classification": classification,
            "refusal_score": 0,
            "corrective_score": round(corrective_score, 3),
            "reinforcing_score": round(reinforcing_score, 3),
            "neutral_score": round(neutral_score, 3),
            "confidence": confidence,
            "keyword_matches": {
                "refusal": 0,
                "corrective": corrective_count,
                "reinforcing": reinforcing_count,
                "neutral": neutral_count
            }
        }

    def batch_classify(self, responses: List[str]) -> List[Dict]:
        """
        批量分类响应

        Args:
            responses: 响应文本列表

        Returns:
            分类结果列表
        """
        return [self.classify(response) for response in responses]

    def analyze_length(self, response: str) -> Dict:
        """
        分析响应长度

        Args:
            response: 响应文本

        Returns:
            长度统计字典
        """
        if not response or response == "ERROR: No response":
            return {"chars": 0, "words": 0, "sentences": 0}

        chars = len(response)
        words = len(response.split())
        sentences = response.count('.') + response.count('!') + response.count('?')

        return {
            "chars": chars,
            "words": words,
            "sentences": max(1, sentences)
        }

    def update_keywords(self, category: str, keywords: List[str]):
        """
        更新关键词列表

        Args:
            category: 类别名称
            keywords: 新的关键词列表
        """
        if category == "refusal":
            self.refusal_keywords = keywords
        elif category == "corrective":
            self.corrective_keywords = keywords
        elif category == "reinforcing":
            self.reinforcing_keywords = keywords
        elif category == "neutral":
            self.neutral_keywords = keywords
        else:
            raise ValueError(f"未知的类别: {category}")

        self.logger.info(f"更新关键词: {category} = {len(keywords)}个关键词")

    def get_keywords(self, category: str) -> List[str]:
        """获取指定类别的关键词"""
        if category == "refusal":
            return self.refusal_keywords.copy()
        elif category == "corrective":
            return self.corrective_keywords.copy()
        elif category == "reinforcing":
            return self.reinforcing_keywords.copy()
        elif category == "neutral":
            return self.neutral_keywords.copy()
        else:
            raise ValueError(f"未知的类别: {category}")
