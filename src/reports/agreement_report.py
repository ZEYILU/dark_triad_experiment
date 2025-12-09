"""
Agreement Report Generator
Generate comprehensive reports for annotation agreement analysis
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List
from ..analysis.agreement_metrics import AgreementResult, AnnotatorVsLLMResult
from ..data.annotation_loader import AnnotationDataset
from ..utils.logger import get_logger


class AgreementReportGenerator:
    """Generate comprehensive agreement analysis reports"""

    def __init__(self, config=None):
        """
        Initialize report generator

        Args:
            config: Configuration object (optional)
        """
        self.config = config
        self.logger = get_logger(__name__)

    def generate_text_report(
        self,
        inter_results: AgreementResult,
        vs_llm_results: List[AnnotatorVsLLMResult],
        output_path: Path
    ):
        """
        Generate text-based agreement report

        Args:
            inter_results: Inter-annotator agreement results
            vs_llm_results: Annotator vs LLM results
            output_path: Path to save the report
        """
        report_lines = []

        # Header
        report_lines.append("="*80)
        report_lines.append("INTER-ANNOTATOR AGREEMENT REPORT")
        report_lines.append("="*80)
        report_lines.append("")

        # 1. Overall agreement
        report_lines.append("1. OVERALL AGREEMENT (Fleiss' Kappa)")
        report_lines.append("-" * 80)
        report_lines.append(f"Fleiss' Kappa: {inter_results.fleiss_kappa:.3f}")
        report_lines.append(f"Interpretation: {inter_results.interpretation}")
        report_lines.append(f"Number of samples: {inter_results.statistics.n_samples}")
        report_lines.append("")

        # 2. Pairwise agreement
        report_lines.append("2. PAIRWISE AGREEMENT (Cohen's Kappa)")
        report_lines.append("-" * 80)
        for pair in inter_results.pairwise_results:
            report_lines.append(
                f"{pair.annotator1} vs {pair.annotator2}: "
                f"{pair.cohen_kappa:.3f} (n={pair.n_samples})"
            )
        report_lines.append("")

        # 3. Agreement statistics
        report_lines.append("3. AGREEMENT STATISTICS")
        report_lines.append("-" * 80)
        stats = inter_results.statistics
        report_lines.append(
            f"All annotators agree: {stats.all_agree}/{stats.n_samples} "
            f"({stats.all_agree_pct:.1f}%)"
        )
        report_lines.append(
            f"At least 2 annotators agree: {stats.any_two_agree}/{stats.n_samples} "
            f"({stats.any_two_agree_pct:.1f}%)"
        )
        report_lines.append(
            f"Exactly 2 annotators agree: {stats.exactly_two_agree}/{stats.n_samples}"
        )
        report_lines.append(
            f"No agreement (all different): {stats.no_agreement}/{stats.n_samples}"
        )
        report_lines.append("")

        # 4. Annotator vs LLM
        report_lines.append("4. ANNOTATOR VS LLM AGREEMENT")
        report_lines.append("-" * 80)
        for result in vs_llm_results:
            report_lines.append(f"{result.name} vs LLM:")
            report_lines.append(f"  Accuracy: {result.accuracy:.2%}")
            report_lines.append(f"  Cohen's Kappa: {result.kappa:.3f}")
            report_lines.append(f"  Number of samples: {result.n_samples}")
            report_lines.append("")

        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))

        self.logger.info(f"Saved agreement report: {output_path}")

    def save_pairwise_csv(
        self,
        inter_results: AgreementResult,
        output_path: Path,
        encoding: str = 'utf-8-sig'
    ):
        """
        Save pairwise agreement results as CSV

        Args:
            inter_results: Inter-annotator agreement results
            output_path: Path to save CSV
            encoding: CSV encoding
        """
        pairwise_data = [
            {
                'Annotator1': pr.annotator1,
                'Annotator2': pr.annotator2,
                'Cohen_Kappa': pr.cohen_kappa,
                'N_Samples': pr.n_samples
            }
            for pr in inter_results.pairwise_results
        ]

        df = pd.DataFrame(pairwise_data)
        df.to_csv(output_path, index=False, encoding=encoding)

        self.logger.info(f"Saved pairwise agreement CSV: {output_path}")

    def save_annotator_vs_llm_csv(
        self,
        vs_llm_results: List[AnnotatorVsLLMResult],
        output_path: Path,
        encoding: str = 'utf-8-sig'
    ):
        """
        Save annotator vs LLM results as CSV

        Args:
            vs_llm_results: List of annotator vs LLM results
            output_path: Path to save CSV
            encoding: CSV encoding
        """
        data = [
            {
                'Annotator': r.name,
                'Accuracy': f"{r.accuracy:.4f}",
                'Cohen_Kappa': f"{r.kappa:.4f}",
                'N_Samples': r.n_samples
            }
            for r in vs_llm_results
        ]

        df = pd.DataFrame(data)
        df.to_csv(output_path, index=False, encoding=encoding)

        self.logger.info(f"Saved annotator vs LLM CSV: {output_path}")

    def save_disagreements_csv(
        self,
        dataset: AnnotationDataset,
        annotator_cols: List[str],
        llm_col: str,
        output_path: Path,
        encoding: str = 'utf-8-sig'
    ):
        """
        Generate and save disagreement samples as CSV

        Args:
            dataset: AnnotationDataset object
            annotator_cols: List of annotator column names
            llm_col: LLM classification column name
            output_path: Path to save CSV
            encoding: CSV encoding
        """
        df = dataset.merged

        # Find samples with valid annotations
        valid_mask = df[annotator_cols + [llm_col]].notna().all(axis=1)
        df_valid = df[valid_mask].copy()

        if len(df_valid) == 0:
            self.logger.warning("No valid samples for disagreement analysis")
            return

        # Find disagreements
        disagreements = []

        for _, row in df_valid.iterrows():
            llm_label = row[llm_col]
            annotator_labels = [row[col] for col in annotator_cols]

            # Check if any annotator disagrees with LLM
            if any(label != llm_label for label in annotator_labels):
                disagreement_row = {
                    'Annotation_ID': row['Annotation_ID'],
                    'LLM_Classification': llm_label
                }

                # Add annotator classifications
                for col in annotator_cols:
                    annotator_name = col.replace('_Classification', '')
                    disagreement_row[annotator_name] = row[col]

                # Add prompt and response if available
                for prompt_col in ['User Prompt', 'User_Prompt']:
                    if prompt_col in row:
                        disagreement_row['User_Prompt'] = row[prompt_col]
                        break

                for response_col in ['LLM Response', 'LLM_Response']:
                    if response_col in row:
                        disagreement_row['LLM_Response'] = row[response_col]
                        break

                disagreements.append(disagreement_row)

        # Save to CSV
        if disagreements:
            disagreement_df = pd.DataFrame(disagreements)
            disagreement_df.to_csv(output_path, index=False, encoding=encoding)

            pct = len(disagreements) / len(df_valid) * 100
            self.logger.info(
                f"Saved disagreement samples: {output_path} "
                f"({len(disagreements)}/{len(df_valid)}, {pct:.1f}%)"
            )
        else:
            self.logger.info("No disagreements found")

    def save_per_category_agreement_csv(
        self,
        per_cat_data: Dict[str, Dict[str, float]],
        categories: List[str],
        output_path: Path,
        encoding: str = 'utf-8-sig'
    ):
        """
        Save per-category agreement data as CSV

        Args:
            per_cat_data: Dict mapping comparison names to category agreements
            categories: List of categories
            output_path: Path to save CSV
            encoding: CSV encoding
        """
        df = pd.DataFrame(per_cat_data, index=categories)
        df.to_csv(output_path, encoding=encoding)

        self.logger.info(f"Saved per-category agreement CSV: {output_path}")

    def generate_full_report(
        self,
        inter_results: AgreementResult,
        vs_llm_results: List[AnnotatorVsLLMResult],
        dataset: AnnotationDataset,
        annotator_cols: List[str],
        llm_col: str,
        output_dir: Path,
        per_cat_data: Dict[str, Dict[str, float]] = None
    ):
        """
        Generate all reports and save to output directory

        Args:
            inter_results: Inter-annotator agreement results
            vs_llm_results: Annotator vs LLM results
            dataset: AnnotationDataset object
            annotator_cols: List of annotator column names
            llm_col: LLM classification column name
            output_dir: Output directory
            per_cat_data: Optional per-category agreement data
        """
        self.logger.info("="*60)
        self.logger.info("Generating Reports")
        self.logger.info("="*60)

        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)

        # Get encoding from config if available
        encoding = 'utf-8-sig'
        if self.config:
            encoding = self.config.get_csv_encoding()

        # 1. Text report
        report_path = output_dir / 'inter_annotator_agreement_report.txt'
        self.generate_text_report(inter_results, vs_llm_results, report_path)

        # 2. Pairwise CSV
        pairwise_path = output_dir / 'pairwise_agreement.csv'
        self.save_pairwise_csv(inter_results, pairwise_path, encoding)

        # 3. Annotator vs LLM CSV
        vs_llm_path = output_dir / 'annotator_vs_llm_agreement.csv'
        self.save_annotator_vs_llm_csv(vs_llm_results, vs_llm_path, encoding)

        # 4. Disagreements CSV
        disagreement_path = output_dir / 'disagreements_detailed.csv'
        self.save_disagreements_csv(
            dataset, annotator_cols, llm_col, disagreement_path, encoding
        )

        # 5. Per-category agreement CSV (if provided)
        if per_cat_data:
            per_cat_path = output_dir / 'per_category_agreement.csv'
            categories = list(next(iter(per_cat_data.values())).keys())
            self.save_per_category_agreement_csv(
                per_cat_data, categories, per_cat_path, encoding
            )

        # 6. Merged data
        merged_path = output_dir / 'merged_annotations.csv'
        dataset.merged.to_csv(merged_path, index=False, encoding=encoding)
        self.logger.info(f"Saved merged data: {merged_path}")

        self.logger.info("="*60)
        self.logger.info("All reports generated successfully!")
        self.logger.info("="*60)
