"""
Inter-Annotator Agreement Metrics
Calculate various agreement metrics for multi-annotator annotation tasks
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from dataclasses import dataclass
from itertools import combinations
from sklearn.metrics import cohen_kappa_score, accuracy_score
from ..utils.logger import get_logger


@dataclass
class PairwiseResult:
    """Results of pairwise agreement analysis"""
    annotator1: str
    annotator2: str
    cohen_kappa: float
    n_samples: int


@dataclass
class AgreementStatistics:
    """Agreement statistics for multi-annotator analysis"""
    n_samples: int
    all_agree: int
    any_two_agree: int
    exactly_two_agree: int
    no_agreement: int

    @property
    def all_agree_pct(self) -> float:
        """Percentage of samples where all annotators agree"""
        return (self.all_agree / self.n_samples * 100) if self.n_samples > 0 else 0.0

    @property
    def any_two_agree_pct(self) -> float:
        """Percentage of samples where at least two annotators agree"""
        return (self.any_two_agree / self.n_samples * 100) if self.n_samples > 0 else 0.0


@dataclass
class AgreementResult:
    """Complete inter-annotator agreement analysis results"""
    fleiss_kappa: float
    interpretation: str
    pairwise_results: List[PairwiseResult]
    statistics: AgreementStatistics

    def to_dict(self) -> Dict:
        """Convert to dictionary for reporting"""
        return {
            'fleiss_kappa': self.fleiss_kappa,
            'interpretation': self.interpretation,
            'pairwise_results': [
                {
                    'Annotator1': pr.annotator1,
                    'Annotator2': pr.annotator2,
                    'Cohen_Kappa': pr.cohen_kappa,
                    'N_Samples': pr.n_samples
                }
                for pr in self.pairwise_results
            ],
            'n_samples': self.statistics.n_samples,
            'all_agree': self.statistics.all_agree,
            'any_two_agree': self.statistics.any_two_agree,
            'exactly_two_agree': self.statistics.exactly_two_agree,
            'no_agreement': self.statistics.no_agreement
        }


@dataclass
class AnnotatorVsLLMResult:
    """Results of annotator vs LLM comparison"""
    name: str
    n_samples: int
    accuracy: float
    kappa: float
    confusion_matrix: np.ndarray

    def to_dict(self) -> Dict:
        """Convert to dictionary for reporting"""
        return {
            'name': self.name,
            'n_samples': self.n_samples,
            'accuracy': self.accuracy,
            'kappa': self.kappa
        }


class AgreementAnalyzer:
    """Calculate various inter-annotator agreement metrics"""

    def __init__(self, categories: List[str]):
        """
        Initialize agreement analyzer

        Args:
            categories: List of classification categories
        """
        self.categories = categories
        self.logger = get_logger(__name__)

    def calculate_fleiss_kappa(
        self,
        df: pd.DataFrame,
        annotator_cols: List[str]
    ) -> float:
        """
        Calculate Fleiss' Kappa for multi-annotator agreement

        Fleiss' Kappa is a statistical measure for assessing the reliability
        of agreement between multiple raters when assigning categorical ratings.

        Args:
            df: DataFrame containing annotations
            annotator_cols: List of column names for annotators

        Returns:
            Fleiss' Kappa value (0.0 to 1.0, can be negative)
        """
        # Keep only samples completed by all annotators
        valid_mask = df[annotator_cols].notna().all(axis=1)
        df_valid = df[valid_mask].copy()

        if len(df_valid) == 0:
            self.logger.warning("No valid samples for Fleiss' Kappa calculation")
            return np.nan

        n_samples = len(df_valid)
        n_raters = len(annotator_cols)
        n_categories = len(self.categories)

        # Build matrix: each row is a sample, each column is the count of
        # annotations for a category
        matrix = np.zeros((n_samples, n_categories))

        for i, (_, row) in enumerate(df_valid.iterrows()):
            for annotator_col in annotator_cols:
                label = row[annotator_col]
                if label in self.categories:
                    cat_idx = self.categories.index(label)
                    matrix[i, cat_idx] += 1

        # Calculate Fleiss' Kappa
        # P_j: proportion of all assignments which were to the j-th category
        P_j = np.sum(matrix, axis=0) / (n_samples * n_raters)

        # P_e: proportion of agreement expected by chance
        P_e = np.sum(P_j ** 2)

        # P_i: extent of agreement for the i-th subject
        P_i = (np.sum(matrix ** 2, axis=1) - n_raters) / (n_raters * (n_raters - 1))

        # P_bar: mean of P_i over all samples
        P_bar = np.mean(P_i)

        # Fleiss' Kappa
        if P_e == 1.0:
            # Perfect expected agreement (all categories have same frequency)
            return 1.0

        kappa = (P_bar - P_e) / (1 - P_e)

        return kappa

    def calculate_pairwise_kappa(
        self,
        df: pd.DataFrame,
        annotator_cols: List[str]
    ) -> List[PairwiseResult]:
        """
        Calculate pairwise Cohen's Kappa for all annotator pairs

        Args:
            df: DataFrame containing annotations
            annotator_cols: List of column names for annotators

        Returns:
            List of PairwiseResult objects
        """
        results = []

        for ann1, ann2 in combinations(annotator_cols, 2):
            # Keep only samples completed by both annotators
            valid_mask = df[[ann1, ann2]].notna().all(axis=1)
            df_valid = df[valid_mask]

            if len(df_valid) > 0:
                kappa = cohen_kappa_score(df_valid[ann1], df_valid[ann2])

                ann1_name = ann1.replace('_Classification', '')
                ann2_name = ann2.replace('_Classification', '')

                results.append(PairwiseResult(
                    annotator1=ann1_name,
                    annotator2=ann2_name,
                    cohen_kappa=kappa,
                    n_samples=len(df_valid)
                ))

                self.logger.info(
                    f"Pairwise: {ann1_name} vs {ann2_name}: "
                    f"κ={kappa:.3f} (n={len(df_valid)})"
                )

        return results

    def calculate_agreement_statistics(
        self,
        df: pd.DataFrame,
        annotator_cols: List[str]
    ) -> AgreementStatistics:
        """
        Calculate agreement statistics (all agree, majority agree, etc.)

        Args:
            df: DataFrame containing annotations
            annotator_cols: List of column names for annotators

        Returns:
            AgreementStatistics object
        """
        valid_mask = df[annotator_cols].notna().all(axis=1)
        df_valid = df[valid_mask]

        if len(df_valid) == 0:
            return AgreementStatistics(
                n_samples=0,
                all_agree=0,
                any_two_agree=0,
                exactly_two_agree=0,
                no_agreement=0
            )

        # Count different agreement patterns
        # All annotators agree
        all_agree = df_valid[annotator_cols].apply(
            lambda row: len(set(row)) == 1,
            axis=1
        ).sum()

        # At least two annotators agree
        any_two_agree = df_valid[annotator_cols].apply(
            lambda row: any(len([x for x in row if x == val]) >= 2 for val in set(row)),
            axis=1
        ).sum()

        # Exactly two annotators agree (not all three)
        exactly_two_agree = df_valid[annotator_cols].apply(
            lambda row: len(set(row)) == 2 and any(
                len([x for x in row if x == val]) == 2 for val in set(row)
            ),
            axis=1
        ).sum()

        # No agreement (all different)
        no_agreement = df_valid[annotator_cols].apply(
            lambda row: len(set(row)) == len(row),
            axis=1
        ).sum()

        return AgreementStatistics(
            n_samples=len(df_valid),
            all_agree=all_agree,
            any_two_agree=any_two_agree,
            exactly_two_agree=exactly_two_agree,
            no_agreement=no_agreement
        )

    def analyze_inter_annotator_agreement(
        self,
        df: pd.DataFrame,
        annotator_cols: List[str],
        interpret_fn=None
    ) -> AgreementResult:
        """
        Complete inter-annotator agreement analysis

        Args:
            df: DataFrame containing annotations
            annotator_cols: List of column names for annotators
            interpret_fn: Optional function to interpret kappa values

        Returns:
            AgreementResult with all metrics
        """
        self.logger.info("="*60)
        self.logger.info("Inter-Annotator Agreement Analysis")
        self.logger.info("="*60)

        # Calculate Fleiss' Kappa
        fleiss_k = self.calculate_fleiss_kappa(df, annotator_cols)
        self.logger.info(f"Fleiss' Kappa (all annotators): {fleiss_k:.3f}")

        # Interpret kappa
        if interpret_fn:
            interpretation = interpret_fn(fleiss_k)
        else:
            interpretation = self._default_interpret_kappa(fleiss_k)

        self.logger.info(f"Interpretation: {interpretation}")

        # Pairwise agreement
        self.logger.info("\nPairwise Agreement (Cohen's Kappa):")
        pairwise_results = self.calculate_pairwise_kappa(df, annotator_cols)

        # Agreement statistics
        self.logger.info("\nAgreement Statistics:")
        statistics = self.calculate_agreement_statistics(df, annotator_cols)

        self.logger.info(
            f"  All annotators agree: {statistics.all_agree}/{statistics.n_samples} "
            f"({statistics.all_agree_pct:.1f}%)"
        )
        self.logger.info(
            f"  At least 2 annotators agree: {statistics.any_two_agree}/{statistics.n_samples} "
            f"({statistics.any_two_agree_pct:.1f}%)"
        )
        self.logger.info(
            f"  Exactly 2 annotators agree: {statistics.exactly_two_agree}/{statistics.n_samples}"
        )
        self.logger.info(
            f"  No agreement: {statistics.no_agreement}/{statistics.n_samples}"
        )

        return AgreementResult(
            fleiss_kappa=fleiss_k,
            interpretation=interpretation,
            pairwise_results=pairwise_results,
            statistics=statistics
        )

    def analyze_annotator_vs_llm(
        self,
        df: pd.DataFrame,
        annotator_col: str,
        llm_col: str,
        annotator_name: str
    ) -> AnnotatorVsLLMResult:
        """
        Analyze agreement between a single annotator and LLM

        Args:
            df: DataFrame containing annotations
            annotator_col: Column name for annotator
            llm_col: Column name for LLM classifications
            annotator_name: Name of annotator (for display)

        Returns:
            AnnotatorVsLLMResult object
        """
        # Keep only samples completed by this annotator
        valid_mask = df[annotator_col].notna()
        df_valid = df[valid_mask]

        if len(df_valid) == 0:
            self.logger.warning(f"No valid samples for {annotator_name} vs LLM")
            return None

        # Calculate metrics
        from sklearn.metrics import confusion_matrix

        accuracy = accuracy_score(df_valid[llm_col], df_valid[annotator_col])
        kappa = cohen_kappa_score(df_valid[llm_col], df_valid[annotator_col])
        cm = confusion_matrix(
            df_valid[llm_col],
            df_valid[annotator_col],
            labels=self.categories
        )

        self.logger.info(f"\n{annotator_name} vs LLM:")
        self.logger.info(f"  Samples: {len(df_valid)}")
        self.logger.info(f"  Accuracy: {accuracy:.2%}")
        self.logger.info(f"  Cohen's Kappa: {kappa:.3f}")

        return AnnotatorVsLLMResult(
            name=annotator_name,
            n_samples=len(df_valid),
            accuracy=accuracy,
            kappa=kappa,
            confusion_matrix=cm
        )

    def analyze_all_vs_llm(
        self,
        df: pd.DataFrame,
        annotator_cols: List[str],
        llm_col: str
    ) -> List[AnnotatorVsLLMResult]:
        """
        Analyze agreement between all annotators and LLM

        Args:
            df: DataFrame containing annotations
            annotator_cols: List of column names for annotators
            llm_col: Column name for LLM classifications

        Returns:
            List of AnnotatorVsLLMResult objects
        """
        self.logger.info("\n" + "="*60)
        self.logger.info("Annotator vs LLM Agreement Analysis")
        self.logger.info("="*60)

        results = []
        for col in annotator_cols:
            name = col.replace('_Classification', '')
            result = self.analyze_annotator_vs_llm(df, col, llm_col, name)
            if result:
                results.append(result)

        return results

    def calculate_per_category_agreement(
        self,
        df: pd.DataFrame,
        col1: str,
        col2: str
    ) -> Dict[str, float]:
        """
        Calculate per-category agreement rates between two columns

        Args:
            df: DataFrame containing classifications
            col1: First classification column
            col2: Second classification column

        Returns:
            Dictionary mapping categories to agreement rates (0-100)
        """
        valid_mask = df[[col1, col2]].notna().all(axis=1)
        df_valid = df[valid_mask]

        agreement_rates = {}

        for category in self.categories:
            # Find samples where col1 has this category
            category_mask = df_valid[col1] == category
            category_samples = df_valid[category_mask]

            if len(category_samples) > 0:
                # Calculate agreement rate
                agreement = (category_samples[col1] == category_samples[col2]).sum()
                agreement_rate = (agreement / len(category_samples)) * 100
                agreement_rates[category] = agreement_rate
            else:
                agreement_rates[category] = 0.0

        return agreement_rates

    @staticmethod
    def _default_interpret_kappa(kappa: float) -> str:
        """
        Default interpretation of Fleiss' Kappa (Landis & Koch, 1977)

        Args:
            kappa: Kappa value

        Returns:
            Interpretation string
        """
        if kappa < 0:
            return "Poor (worse than random)"
        elif kappa < 0.20:
            return "Slight agreement"
        elif kappa < 0.40:
            return "Fair agreement"
        elif kappa < 0.60:
            return "Moderate agreement"
        elif kappa < 0.80:
            return "Substantial agreement"
        else:
            return "Almost perfect agreement"
