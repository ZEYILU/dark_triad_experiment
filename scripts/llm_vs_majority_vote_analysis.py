"""
LLM Judge vs Majority Vote Analysis

This script analyzes the agreement between LLM Judge and the majority vote
from three human annotators. This provides a more robust comparison than
individual annotator comparisons.

Author: Generated with Claude Code
Date: 2025-12-03
"""

import pandas as pd
import numpy as np
from sklearn.metrics import cohen_kappa_score, accuracy_score, confusion_matrix, classification_report
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Set style
sns.set_style('whitegrid')
plt.rcParams['figure.dpi'] = 300

# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).parent.parent
DATA_PATH = BASE_DIR / 'results' / 'multi_annotator_analysis' / 'merged_annotations.csv'
OUTPUT_DIR = BASE_DIR / 'results' / 'llm_vs_majority_vote'

# Create output directory
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Category mapping
CATEGORY_MAP = {
    1: 'REFUSAL',
    2: 'REINFORCING',
    3: 'CORRECTIVE',
    4: 'MIXED'
}

CATEGORY_TO_NUM = {v: k for k, v in CATEGORY_MAP.items()}


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def convert_to_numeric(value):
    """Convert text labels to numeric codes."""
    if pd.isna(value):
        return np.nan
    if isinstance(value, (int, float)):
        return int(value) if not np.isnan(value) else np.nan
    return CATEGORY_TO_NUM.get(value.strip().upper(), np.nan)


def get_majority_vote(row):
    """
    Calculate majority vote from three annotators.
    Returns (majority_label, vote_count)
    """
    votes = [
        convert_to_numeric(row['Annotator1_Classification']),
        convert_to_numeric(row['Annotator2_Classification']),
        convert_to_numeric(row['Annotator3_Classification'])
    ]

    # Remove NaN values
    votes = [v for v in votes if not np.isnan(v)]

    if len(votes) == 0:
        return np.nan, 0

    # Use scipy.stats.mode
    mode_result = stats.mode(votes, keepdims=True)
    majority = mode_result.mode[0]
    count = mode_result.count[0]

    # At least 2 votes needed for consensus
    if count >= 2:
        return int(majority), int(count)
    else:
        return np.nan, 0


def interpret_kappa(kappa):
    """Interpret Cohen's Kappa value."""
    if kappa >= 0.81:
        return "Almost Perfect"
    elif kappa >= 0.61:
        return "Substantial"
    elif kappa >= 0.41:
        return "Moderate"
    elif kappa >= 0.21:
        return "Fair"
    else:
        return "Slight/Poor"


# ============================================================
# MAIN ANALYSIS
# ============================================================

def main():
    print("="*80)
    print("LLM JUDGE vs MAJORITY VOTE ANALYSIS")
    print("="*80)
    print(f"\nLoading data from: {DATA_PATH}")

    # Load data
    df = pd.read_csv(DATA_PATH, encoding='utf-8-sig')
    print(f"[OK] Loaded {len(df)} samples")

    # ========== 1. Calculate Majority Vote ==========
    print("\n" + "="*80)
    print("1. CALCULATING MAJORITY VOTE")
    print("="*80)

    df[['Majority_Vote', 'Vote_Count']] = df.apply(
        lambda row: pd.Series(get_majority_vote(row)), axis=1
    )

    # Convert LLM classification to numeric
    df['LLM_Judge_Numeric'] = df['LLM_Judge_Classification'].apply(convert_to_numeric)

    # Filter to samples with majority consensus
    consensus_df = df[df['Majority_Vote'].notna()].copy()

    n_total = len(df)
    n_consensus = len(consensus_df)
    n_3way = (consensus_df['Vote_Count'] == 3).sum()
    n_2way = (consensus_df['Vote_Count'] == 2).sum()

    print(f"\n[OK] Samples with majority consensus (>=2 annotators agree): {n_consensus}/{n_total} ({n_consensus/n_total:.1%})")
    print(f"  - 3-way consensus (all agree): {n_3way}")
    print(f"  - 2-way consensus (2/3 agree): {n_2way}")

    # ========== 2. Overall Metrics ==========
    print("\n" + "="*80)
    print("2. OVERALL METRICS: LLM Judge vs Majority Vote")
    print("="*80)

    llm_vs_majority_kappa = cohen_kappa_score(
        consensus_df['Majority_Vote'],
        consensus_df['LLM_Judge_Numeric']
    )

    llm_vs_majority_acc = accuracy_score(
        consensus_df['Majority_Vote'],
        consensus_df['LLM_Judge_Numeric']
    )

    agreement_rate = (consensus_df['Majority_Vote'] == consensus_df['LLM_Judge_Numeric']).mean()

    print(f"\nKEY METRICS:")
    print(f"   Cohen's Kappa:  {llm_vs_majority_kappa:.3f}")
    print(f"   Accuracy:       {llm_vs_majority_acc:.3f} ({llm_vs_majority_acc:.1%})")
    print(f"   Agreement Rate: {agreement_rate:.3f} ({agreement_rate:.1%})")
    print(f"   N samples:      {n_consensus}")
    print(f"\n   Interpretation: {interpret_kappa(llm_vs_majority_kappa)}")

    # ========== 3. Per-Category Analysis ==========
    print("\n" + "="*80)
    print("3. PER-CATEGORY ANALYSIS")
    print("="*80)

    results_table = []

    for cat_num, cat_name in CATEGORY_MAP.items():
        # Samples where majority voted for this category
        cat_samples = consensus_df[consensus_df['Majority_Vote'] == cat_num]

        if len(cat_samples) == 0:
            continue

        # How many did LLM get correct?
        llm_correct = (cat_samples['LLM_Judge_Numeric'] == cat_num).sum()

        # Precision: of samples majority labeled as X, how many did LLM also label as X?
        precision = llm_correct / len(cat_samples)

        # Recall: of samples LLM labeled as X, how many match majority?
        llm_identified = consensus_df[consensus_df['LLM_Judge_Numeric'] == cat_num]
        true_positives = llm_identified[llm_identified['Majority_Vote'] == cat_num]
        recall = len(true_positives) / len(cat_samples) if len(cat_samples) > 0 else 0

        # F1 Score
        if precision + recall > 0:
            f1 = 2 * precision * recall / (precision + recall)
        else:
            f1 = 0

        results_table.append({
            'Category': cat_name,
            'N (Majority)': len(cat_samples),
            'LLM Correct': llm_correct,
            'Precision': precision,
            'Recall': recall,
            'F1-Score': f1
        })

        print(f"\n{cat_name}:")
        print(f"  Samples (by majority): {len(cat_samples)}")
        print(f"  LLM correct: {llm_correct}/{len(cat_samples)} ({precision:.1%})")
        print(f"  Precision: {precision:.3f}")
        print(f"  Recall:    {recall:.3f}")
        print(f"  F1-Score:  {f1:.3f}")

        # Show misclassifications
        misclassified = cat_samples[cat_samples['LLM_Judge_Numeric'] != cat_num]
        if len(misclassified) > 0:
            print(f"  LLM misclassifications:")
            for wrong_cat, count in misclassified['LLM_Judge_Numeric'].value_counts().items():
                print(f"    → {CATEGORY_MAP[int(wrong_cat)]}: {count} cases")

    # Save results table
    results_df = pd.DataFrame(results_table)
    results_path = OUTPUT_DIR / 'per_category_metrics.csv'
    results_df.to_csv(results_path, index=False)
    print(f"\n[SAVED] {results_path}")

    # ========== 4. Confusion Matrix ==========
    print("\n" + "="*80)
    print("4. CONFUSION MATRIX")
    print("="*80)

    cm = confusion_matrix(
        consensus_df['Majority_Vote'],
        consensus_df['LLM_Judge_Numeric'],
        labels=[1, 2, 3, 4]
    )

    print("\n           LLM Classification")
    print("           REF  REIN CORR  MIX")
    print("Majority  ┌─────────────────────")
    labels = ['REF', 'REIN', 'CORR', 'MIX']
    for i, label in enumerate(labels):
        print(f"  {label:5s}  │ {cm[i][0]:3d}  {cm[i][1]:3d}  {cm[i][2]:3d}  {cm[i][3]:3d}")

    # Visualize confusion matrix
    plt.figure(figsize=(12, 10))
    sns.heatmap(
        cm,
        annot=True,
        fmt='d',
        cmap='Blues',
        xticklabels=['REFUSAL', 'REINFORCING', 'CORRECTIVE', 'MIXED'],
        yticklabels=['REFUSAL', 'REINFORCING', 'CORRECTIVE', 'MIXED'],
        cbar_kws={'label': 'Count'},
        square=True
    )
    plt.xlabel('LLM Judge Classification', fontsize=13, fontweight='bold')
    plt.ylabel('Majority Vote (Gold Standard)', fontsize=13, fontweight='bold')
    plt.title(
        f'Confusion Matrix: LLM vs Majority Vote\n(κ={llm_vs_majority_kappa:.3f}, n={n_consensus})',
        fontsize=15,
        fontweight='bold',
        pad=20
    )
    plt.tight_layout()

    cm_path = OUTPUT_DIR / 'confusion_matrix_llm_vs_majority.png'
    plt.savefig(cm_path, dpi=300, bbox_inches='tight')
    print(f"\n[SAVED] {cm_path}")
    plt.close()

    # ========== 5. Classification Report ==========
    print("\n" + "="*80)
    print("5. DETAILED CLASSIFICATION REPORT")
    print("="*80)

    report = classification_report(
        consensus_df['Majority_Vote'],
        consensus_df['LLM_Judge_Numeric'],
        labels=[1, 2, 3, 4],
        target_names=['REFUSAL', 'REINFORCING', 'CORRECTIVE', 'MIXED'],
        digits=3
    )
    print("\n" + report)

    # ========== 6. 3-Way Perfect Agreement ==========
    print("\n" + "="*80)
    print("6. AGREEMENT ON PERFECT 3-WAY CONSENSUS")
    print("="*80)

    perfect_3way = consensus_df[consensus_df['Vote_Count'] == 3]
    llm_agreement_on_perfect = (
        perfect_3way['Majority_Vote'] == perfect_3way['LLM_Judge_Numeric']
    ).mean()

    print(f"\nWhen all 3 humans agree ({len(perfect_3way)} cases):")
    print(f"  LLM also agrees: {llm_agreement_on_perfect:.3f} ({llm_agreement_on_perfect:.1%})")

    # ========== 7. 2-Way Consensus ==========
    two_way = consensus_df[consensus_df['Vote_Count'] == 2]
    if len(two_way) > 0:
        llm_agreement_on_2way = (
            two_way['Majority_Vote'] == two_way['LLM_Judge_Numeric']
        ).mean()

        print(f"\nWhen 2/3 humans agree ({len(two_way)} cases):")
        print(f"  LLM agrees with majority: {llm_agreement_on_2way:.3f} ({llm_agreement_on_2way:.1%})")

    # ========== 8. Cases Where LLM Disagrees with Unanimous Humans ==========
    print("\n" + "="*80)
    print("7. CASES WHERE LLM DISAGREES WITH UNANIMOUS HUMANS")
    print("="*80)

    unanimous_disagreement = perfect_3way[
        perfect_3way['Majority_Vote'] != perfect_3way['LLM_Judge_Numeric']
    ]

    if len(unanimous_disagreement) > 0:
        print(f"\nFound {len(unanimous_disagreement)} cases where all 3 humans agree but LLM differs:\n")

        for idx, row in unanimous_disagreement.iterrows():
            cat_map = {1:'REF', 2:'REIN', 3:'CORR', 4:'MIX'}
            print(f"Sample {int(row['Annotation_ID']):03d}:")
            print(f"  All humans agree: {cat_map[int(row['Majority_Vote'])]}")
            print(f"  LLM classified:   {cat_map[int(row['LLM_Judge_Numeric'])]}")
            print()
    else:
        print("\n[OK] No cases found - LLM agrees with all unanimous human judgments!")

    # ========== 9. Save Final Analysis ==========
    print("\n" + "="*80)
    print("8. SAVING RESULTS")
    print("="*80)

    # Save full dataset with majority vote
    output_path = OUTPUT_DIR / 'llm_vs_majority_analysis.csv'
    consensus_df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"\n[SAVED] Full analysis: {output_path}")

    # Create summary statistics
    summary_data = {
        'Metric': [
            'Overall Cohen\'s Kappa',
            'Accuracy',
            'Agreement Rate',
            'N samples with consensus',
            'N 3-way consensus',
            'N 2-way consensus',
            'REFUSAL Precision',
            'REFUSAL Recall',
            'REFUSAL F1',
            'REINFORCING Precision',
            'REINFORCING Recall',
            'REINFORCING F1',
            'CORRECTIVE Precision',
            'CORRECTIVE Recall',
            'CORRECTIVE F1',
            'MIXED Precision',
            'MIXED Recall',
            'MIXED F1'
        ],
        'Value': [
            f"{llm_vs_majority_kappa:.3f}",
            f"{llm_vs_majority_acc:.3f}",
            f"{agreement_rate:.3f}",
            f"{n_consensus}",
            f"{n_3way}",
            f"{n_2way}",
        ] + [
            f"{row[metric]:.3f}"
            for row in results_table
            for metric in ['Precision', 'Recall', 'F1-Score']
        ]
    }

    summary_df = pd.DataFrame(summary_data)
    summary_path = OUTPUT_DIR / 'summary_metrics.csv'
    summary_df.to_csv(summary_path, index=False)
    print(f"[SAVED] Summary metrics: {summary_path}")

    # Create detailed text report
    report_path = OUTPUT_DIR / 'llm_vs_majority_report.txt'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("LLM JUDGE vs MAJORITY VOTE ANALYSIS REPORT\n")
        f.write("="*80 + "\n\n")

        f.write(f"Date: 2025-12-03\n")
        f.write(f"Total samples: {len(df)}\n")
        f.write(f"Samples with majority consensus: {n_consensus}/{len(df)} ({n_consensus/len(df):.1%})\n\n")

        f.write("OVERALL METRICS\n")
        f.write("-"*80 + "\n")
        f.write(f"Cohen's Kappa:  {llm_vs_majority_kappa:.3f} ({interpret_kappa(llm_vs_majority_kappa)})\n")
        f.write(f"Accuracy:       {llm_vs_majority_acc:.3f}\n")
        f.write(f"Agreement Rate: {agreement_rate:.3f}\n\n")

        f.write("PER-CATEGORY METRICS\n")
        f.write("-"*80 + "\n")
        f.write(results_df.to_string(index=False))
        f.write("\n\n")

        f.write("CLASSIFICATION REPORT\n")
        f.write("-"*80 + "\n")
        f.write(report)
        f.write("\n")

    print(f"[SAVED] Text report: {report_path}")

    print("\n" + "="*80)
    print("[SUCCESS] ANALYSIS COMPLETE!")
    print("="*80)
    print(f"\nAll results saved to: {OUTPUT_DIR}")
    print("\nFiles generated:")
    print(f"  1. {output_path.name} - Full dataset with majority vote")
    print(f"  2. {summary_path.name} - Summary metrics")
    print(f"  3. {results_path.name} - Per-category metrics")
    print(f"  4. {cm_path.name} - Confusion matrix visualization")
    print(f"  5. {report_path.name} - Detailed text report")


if __name__ == "__main__":
    main()
