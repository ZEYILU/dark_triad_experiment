"""
Visualization for Agreement Analysis
Generate plots and charts for inter-annotator agreement analysis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Optional
from ..utils.logger import get_logger


class AgreementVisualizer:
    """Generate visualizations for agreement analysis"""

    def __init__(self, viz_config: Optional[Dict] = None):
        """
        Initialize visualizer

        Args:
            viz_config: Visualization configuration dict
        """
        self.logger = get_logger(__name__)

        # Default configuration
        self.config = {
            'dpi': 300,
            'figsize': [12, 8],
            'confusion_matrix_figsize': [10, 8],
            'per_category_figsize': [12, 7],
            'cmap': 'Blues',
            'colors': ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#6A994E'],
            'title_fontsize': 14,
            'label_fontsize': 12,
            'tick_fontsize': 11,
            'annotation_fontsize': 8
        }

        # Update with provided config
        if viz_config:
            self.config.update(viz_config)

    def plot_confusion_matrix(
        self,
        y_true: pd.Series,
        y_pred: pd.Series,
        labels: List[str],
        title: str,
        output_path: Path,
        show_percentages: bool = False
    ):
        """
        Generate confusion matrix heatmap

        Args:
            y_true: True labels
            y_pred: Predicted labels
            labels: List of category labels
            title: Plot title
            output_path: Path to save the figure
            show_percentages: If True, show percentages instead of counts
        """
        from sklearn.metrics import confusion_matrix

        # Calculate confusion matrix
        cm = confusion_matrix(y_true, y_pred, labels=labels)

        # Create figure
        figsize = tuple(self.config['confusion_matrix_figsize'])
        plt.figure(figsize=figsize)

        # Prepare annotations
        if show_percentages:
            # Calculate percentages
            cm_pct = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis] * 100
            annot = np.array([[f'{count}\n({pct:.1f}%)'
                             for count, pct in zip(row_counts, row_pcts)]
                            for row_counts, row_pcts in zip(cm, cm_pct)])
            fmt = ''
        else:
            annot = cm
            fmt = 'd'

        # Create heatmap
        sns.heatmap(
            cm,
            annot=annot,
            fmt=fmt,
            cmap=self.config['cmap'],
            xticklabels=labels,
            yticklabels=labels,
            cbar_kws={'label': 'Count'}
        )

        plt.title(title, fontsize=self.config['title_fontsize'], fontweight='bold')
        plt.ylabel('True Label (LLM)', fontsize=self.config['label_fontsize'])
        plt.xlabel('Predicted Label (Annotator)', fontsize=self.config['label_fontsize'])
        plt.xticks(fontsize=self.config['tick_fontsize'])
        plt.yticks(fontsize=self.config['tick_fontsize'])

        # Save figure
        plt.tight_layout()
        plt.savefig(output_path, dpi=self.config['dpi'], bbox_inches='tight')
        plt.close()

        self.logger.info(f"Saved confusion matrix: {output_path}")

    def plot_per_category_agreement(
        self,
        agreement_data: Dict[str, Dict[str, float]],
        categories: List[str],
        output_path: Path,
        title: str = 'Per-Category Agreement Rates'
    ):
        """
        Generate per-category agreement bar chart

        Args:
            agreement_data: Dict mapping comparison names to category agreement rates
            categories: List of categories
            output_path: Path to save the figure
            title: Plot title
        """
        figsize = tuple(self.config['per_category_figsize'])
        fig, ax = plt.subplots(figsize=figsize)

        # Prepare data
        comparison_names = list(agreement_data.keys())
        n_comparisons = len(comparison_names)
        x = np.arange(len(categories))
        width = 0.25  # Bar width

        # Calculate bar positions
        if n_comparisons == 1:
            offsets = [0]
        else:
            offsets = np.linspace(
                -(n_comparisons-1)*width/2,
                (n_comparisons-1)*width/2,
                n_comparisons
            )

        # Create bars
        colors = self.config['colors']
        rects_list = []

        for i, (comparison_name, agreements) in enumerate(agreement_data.items()):
            values = [agreements.get(cat, 0.0) for cat in categories]
            color = colors[i % len(colors)]

            rects = ax.bar(
                x + offsets[i],
                values,
                width,
                label=comparison_name,
                color=color
            )
            rects_list.append(rects)

        # Customize plot
        ax.set_ylabel('Agreement (%)', fontsize=self.config['label_fontsize'])
        ax.set_xlabel('Category', fontsize=self.config['label_fontsize'])
        ax.set_title(title, fontsize=self.config['title_fontsize'], fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(categories, fontsize=self.config['tick_fontsize'])
        ax.legend(fontsize=10)
        ax.set_ylim(0, 110)
        ax.grid(axis='y', alpha=0.3, linestyle='--')

        # Add value labels on bars
        def autolabel(rects):
            for rect in rects:
                height = rect.get_height()
                if height > 0:
                    ax.annotate(
                        f'{height:.1f}%',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center',
                        va='bottom',
                        fontsize=self.config['annotation_fontsize']
                    )

        for rects in rects_list:
            autolabel(rects)

        # Save figure
        plt.tight_layout()
        plt.savefig(output_path, dpi=self.config['dpi'], bbox_inches='tight')
        plt.close()

        self.logger.info(f"Saved per-category agreement chart: {output_path}")

    def plot_kappa_comparison(
        self,
        kappa_data: Dict[str, float],
        output_path: Path,
        title: str = 'Kappa Comparison',
        kappa_thresholds: Optional[Dict[str, float]] = None
    ):
        """
        Generate bar chart comparing kappa values

        Args:
            kappa_data: Dict mapping names to kappa values
            output_path: Path to save the figure
            title: Plot title
            kappa_thresholds: Optional dict of interpretation thresholds
        """
        figsize = tuple(self.config['figsize'])
        fig, ax = plt.subplots(figsize=figsize)

        # Prepare data
        names = list(kappa_data.keys())
        values = list(kappa_data.values())
        x = np.arange(len(names))

        # Create bars
        colors = [self.config['colors'][i % len(self.config['colors'])]
                 for i in range(len(names))]
        bars = ax.bar(x, values, color=colors)

        # Add threshold lines if provided
        if kappa_thresholds:
            threshold_styles = {
                'slight': ('--', 'gray', 'Slight'),
                'fair': ('--', 'orange', 'Fair'),
                'moderate': ('--', 'blue', 'Moderate'),
                'substantial': ('--', 'green', 'Substantial')
            }

            for thresh_name, (style, color, label) in threshold_styles.items():
                if thresh_name in kappa_thresholds:
                    thresh_value = kappa_thresholds[thresh_name]
                    ax.axhline(
                        y=thresh_value,
                        linestyle=style,
                        color=color,
                        alpha=0.5,
                        label=f'{label} ({thresh_value})'
                    )

        # Customize plot
        ax.set_ylabel("Cohen's Kappa", fontsize=self.config['label_fontsize'])
        ax.set_title(title, fontsize=self.config['title_fontsize'], fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(names, fontsize=self.config['tick_fontsize'], rotation=45, ha='right')
        ax.set_ylim(-0.1, 1.1)
        ax.grid(axis='y', alpha=0.3, linestyle='--')

        if kappa_thresholds:
            ax.legend(fontsize=9)

        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.annotate(
                f'{height:.3f}',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha='center',
                va='bottom',
                fontsize=self.config['annotation_fontsize']
            )

        # Save figure
        plt.tight_layout()
        plt.savefig(output_path, dpi=self.config['dpi'], bbox_inches='tight')
        plt.close()

        self.logger.info(f"Saved kappa comparison chart: {output_path}")

    def plot_agreement_distribution(
        self,
        agreement_stats: Dict[str, int],
        output_path: Path,
        title: str = 'Agreement Distribution'
    ):
        """
        Generate pie chart showing distribution of agreement patterns

        Args:
            agreement_stats: Dict with keys like 'all_agree', 'exactly_two_agree', etc.
            output_path: Path to save the figure
            title: Plot title
        """
        figsize = (10, 8)
        fig, ax = plt.subplots(figsize=figsize)

        # Prepare data
        labels = []
        sizes = []
        colors_map = {
            'all_agree': '#6A994E',
            'exactly_two_agree': '#F18F01',
            'no_agreement': '#C73E1D'
        }
        colors = []

        for key, value in agreement_stats.items():
            if value > 0:
                label = key.replace('_', ' ').title()
                labels.append(label)
                sizes.append(value)
                colors.append(colors_map.get(key, '#2E86AB'))

        # Create pie chart
        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=labels,
            colors=colors,
            autopct='%1.1f%%',
            startangle=90,
            textprops={'fontsize': 11}
        )

        # Customize
        ax.set_title(title, fontsize=self.config['title_fontsize'], fontweight='bold')

        # Make percentage text bold
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')

        # Save figure
        plt.tight_layout()
        plt.savefig(output_path, dpi=self.config['dpi'], bbox_inches='tight')
        plt.close()

        self.logger.info(f"Saved agreement distribution chart: {output_path}")
