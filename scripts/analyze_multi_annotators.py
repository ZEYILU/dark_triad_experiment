"""
Multi-Annotator Analysis Script

Analysis includes:
1. Inter-annotator agreement (Inter-rater reliability)
2. Agreement between each annotator and LLM
3. Comprehensive analysis and visualization
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.metrics import (
    confusion_matrix,
    cohen_kappa_score,
    accuracy_score
)
import seaborn as sns
import matplotlib.pyplot as plt
from itertools import combinations
import glob
import re

# 数字代码到文本标签的映射
CODE_TO_LABEL = {
    1: 'REFUSAL',
    2: 'REINFORCING',
    3: 'CORRECTIVE',
    4: 'MIXED',
    '1': 'REFUSAL',
    '2': 'REINFORCING',
    '3': 'CORRECTIVE',
    '4': 'MIXED'
}


def convert_codes_to_labels(df: pd.DataFrame, column: str = 'Human_Classification') -> pd.DataFrame:
    """Convert numeric codes to text labels"""
    df = df.copy()

    # Check if column exists
    if column not in df.columns:
        print(f"  [WARNING] Column '{column}' not found in dataframe")
        return df

    # Check if conversion is needed
    df_valid = df[df[column].notna()].copy()
    if len(df_valid) > 0:
        first_value = df_valid[column].iloc[0]
        if isinstance(first_value, (int, float, np.integer, np.floating)) or (isinstance(first_value, str) and str(first_value).isdigit()):
            print(f"  [INFO] Converting numeric codes to text labels...")
            df[column] = df[column].map(lambda x: CODE_TO_LABEL.get(x, x) if pd.notna(x) else x)
            print(f"  [OK] Conversion completed")

    return df


def load_annotator_data(file_path: str, annotator_name: str) -> pd.DataFrame:
    """Load data from a single annotator"""
    print(f"\nLoading annotations from {annotator_name}...")
    df = pd.read_csv(file_path)

    # Check and fix missing Annotation_ID column name
    # If the first column is empty or unnamed, rename it to Annotation_ID
    if df.columns[0] == '' or 'Unnamed' in df.columns[0]:
        df = df.rename(columns={df.columns[0]: 'Annotation_ID'})
        print(f"  [INFO] Fixed missing Annotation_ID column name")

    # Convert codes (before renaming)
    df = convert_codes_to_labels(df, column='Human_Classification')

    # Rename columns to distinguish annotators
    rename_dict = {
        'Human_Classification': f'{annotator_name}_Classification',
        'Notes': f'{annotator_name}_Notes'
    }
    # Only rename Confidence column if it exists
    if 'Confidence' in df.columns:
        rename_dict['Confidence'] = f'{annotator_name}_Confidence'

    df = df.rename(columns=rename_dict)

    print(f"  Samples: {len(df)}")
    completed = df[f'{annotator_name}_Classification'].notna().sum()
    print(f"  Completed: {completed}/{len(df)} ({completed/len(df)*100:.1f}%)")

    # Keep only necessary columns
    keep_cols = ['Annotation_ID', f'{annotator_name}_Classification']

    # Dynamically add existing columns
    if f'{annotator_name}_Confidence' in df.columns:
        keep_cols.append(f'{annotator_name}_Confidence')
    if f'{annotator_name}_Notes' in df.columns:
        keep_cols.append(f'{annotator_name}_Notes')

    df = df[keep_cols]

    return df


def calculate_fleiss_kappa(df: pd.DataFrame, annotator_cols: list) -> float:
    """
    Calculate Fleiss' Kappa (multi-annotator agreement)

    Args:
        df: DataFrame containing all annotators' annotations
        annotator_cols: List of annotator column names

    Returns:
        Fleiss' Kappa value
    """
    # Keep only samples completed by all annotators
    valid_mask = df[annotator_cols].notna().all(axis=1)
    df_valid = df[valid_mask].copy()

    if len(df_valid) == 0:
        return np.nan

    n_samples = len(df_valid)
    n_raters = len(annotator_cols)

    # Get all possible categories
    categories = ['REFUSAL', 'REINFORCING', 'CORRECTIVE', 'MIXED']
    n_categories = len(categories)

    # Build matrix: each row is a sample, each column is the count of annotations for a category
    matrix = np.zeros((n_samples, n_categories))

    for i, (_, row) in enumerate(df_valid.iterrows()):
        for annotator_col in annotator_cols:
            label = row[annotator_col]
            if label in categories:
                cat_idx = categories.index(label)
                matrix[i, cat_idx] += 1

    # Calculate Fleiss' Kappa
    # P_j: proportion of all assignments which were to the j-th category
    P_j = np.sum(matrix, axis=0) / (n_samples * n_raters)

    # P_e: proportion of agreement expected by chance
    P_e = np.sum(P_j ** 2)

    # P_bar: mean of P_i over all samples
    P_i = (np.sum(matrix ** 2, axis=1) - n_raters) / (n_raters * (n_raters - 1))
    P_bar = np.mean(P_i)

    # Fleiss' Kappa
    kappa = (P_bar - P_e) / (1 - P_e)

    return kappa


def analyze_inter_annotator_agreement(df: pd.DataFrame, annotator_cols: list):
    """Analyze inter-annotator agreement"""
    print("\n" + "="*60)
    print("Inter-Annotator Agreement Analysis")
    print("="*60)

    # Calculate Fleiss' Kappa (all annotators)
    fleiss_k = calculate_fleiss_kappa(df, annotator_cols)
    print(f"\nFleiss' Kappa (all annotators): {fleiss_k:.3f}")

    # Interpretation
    if fleiss_k < 0:
        interpretation = "Poor (worse than random)"
    elif fleiss_k < 0.20:
        interpretation = "Slight agreement"
    elif fleiss_k < 0.40:
        interpretation = "Fair agreement"
    elif fleiss_k < 0.60:
        interpretation = "Moderate agreement"
    elif fleiss_k < 0.80:
        interpretation = "Substantial agreement"
    else:
        interpretation = "Almost perfect agreement"
    print(f"Interpretation: {interpretation}")

    # Pairwise comparison (Cohen's Kappa)
    print("\nPairwise Agreement (Cohen's Kappa):")
    pairwise_results = []
    for ann1, ann2 in combinations(annotator_cols, 2):
        # Keep only samples completed by both annotators
        valid_mask = df[[ann1, ann2]].notna().all(axis=1)
        df_valid = df[valid_mask]

        if len(df_valid) > 0:
            kappa = cohen_kappa_score(df_valid[ann1], df_valid[ann2])
            ann1_name = ann1.replace('_Classification', '')
            ann2_name = ann2.replace('_Classification', '')
            print(f"  {ann1_name} vs {ann2_name}: {kappa:.3f}")
            pairwise_results.append({
                'Annotator1': ann1_name,
                'Annotator2': ann2_name,
                'Cohen_Kappa': kappa,
                'N_Samples': len(df_valid)
            })

    # Agreement matrix
    print("\nAgreement Statistics:")
    valid_mask = df[annotator_cols].notna().all(axis=1)
    df_valid = df[valid_mask]

    all_agree = 0
    any_two_agree = 0
    exactly_two_agree = 0
    no_agreement = 0

    if len(df_valid) > 0:
        # Check if all values in each row are the same
        all_agree = df_valid[annotator_cols].apply(lambda row: len(set(row)) == 1, axis=1).sum()

        # At least two agree
        any_two_agree = df_valid[annotator_cols].apply(
            lambda row: any(len([x for x in row if x == val]) >= 2 for val in set(row)),
            axis=1
        ).sum()

        # Exactly two agree (not all three)
        exactly_two_agree = df_valid[annotator_cols].apply(
            lambda row: len(set(row)) == 2 and any(len([x for x in row if x == val]) == 2 for val in set(row)),
            axis=1
        ).sum()

        # No agreement (all different)
        no_agreement = df_valid[annotator_cols].apply(lambda row: len(set(row)) == len(row), axis=1).sum()

        print(f"  All annotators agree: {all_agree}/{len(df_valid)} ({all_agree/len(df_valid)*100:.1f}%)")
        print(f"  At least 2 annotators agree: {any_two_agree}/{len(df_valid)} ({any_two_agree/len(df_valid)*100:.1f}%)")
        print(f"  Exactly 2 annotators agree: {exactly_two_agree}/{len(df_valid)} ({exactly_two_agree/len(df_valid)*100:.1f}%)")
        print(f"  No agreement (all different): {no_agreement}/{len(df_valid)} ({no_agreement/len(df_valid)*100:.1f}%)")

    # Return results for report generation
    return {
        'fleiss_kappa': fleiss_k,
        'interpretation': interpretation,
        'pairwise_results': pairwise_results,
        'n_samples': len(df_valid) if len(df_valid) > 0 else 0,
        'all_agree': all_agree,
        'any_two_agree': any_two_agree,
        'exactly_two_agree': exactly_two_agree,
        'no_agreement': no_agreement
    }


def analyze_annotator_vs_llm(df: pd.DataFrame, annotator_col: str, llm_col: str, annotator_name: str):
    """Analyze agreement between a single annotator and LLM"""
    print(f"\n{annotator_name} vs LLM:")

    # Keep only samples completed by this annotator
    valid_mask = df[annotator_col].notna()
    df_valid = df[valid_mask]

    if len(df_valid) == 0:
        print("  No valid samples")
        return None

    # Calculate metrics
    accuracy = accuracy_score(df_valid[llm_col], df_valid[annotator_col])
    kappa = cohen_kappa_score(df_valid[llm_col], df_valid[annotator_col])

    print(f"  Samples: {len(df_valid)}")
    print(f"  Accuracy: {accuracy:.2%}")
    print(f"  Cohen's Kappa: {kappa:.3f}")

    # Confusion matrix
    categories = ['REFUSAL', 'REINFORCING', 'CORRECTIVE', 'MIXED']
    cm = confusion_matrix(df_valid[llm_col], df_valid[annotator_col], labels=categories)

    return {
        'name': annotator_name,
        'n_samples': len(df_valid),
        'accuracy': accuracy,
        'kappa': kappa,
        'confusion_matrix': cm
    }


def analyze_all_vs_llm(df: pd.DataFrame, annotator_cols: list, llm_col: str):
    """Analyze agreement between all annotators and LLM"""
    print("\n" + "="*60)
    print("Annotator vs LLM Agreement Analysis")
    print("="*60)

    results = []
    for col in annotator_cols:
        name = col.replace('_Classification', '')
        result = analyze_annotator_vs_llm(df, col, llm_col, name)
        if result:
            results.append(result)

    return results


def calculate_per_category_agreement(df: pd.DataFrame, col1: str, col2: str, categories: list) -> dict:
    """Calculate per-category agreement rates between two classification columns"""
    valid_mask = df[[col1, col2]].notna().all(axis=1)
    df_valid = df[valid_mask]

    agreement_rates = {}
    for category in categories:
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


def generate_comparison_report(df: pd.DataFrame, annotator_cols: list, llm_col: str, output_dir: str):
    """Generate detailed comparison report"""
    print("\n" + "="*60)
    print("Generating Detailed Comparison Report")
    print("="*60)

    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)

    categories = ['REFUSAL', 'REINFORCING', 'CORRECTIVE', 'MIXED']

    # 1. Generate confusion matrix for each annotator
    for col in annotator_cols:
        name = col.replace('_Classification', '')
        valid_mask = df[col].notna()
        df_valid = df[valid_mask]

        if len(df_valid) == 0:
            continue

        cm = confusion_matrix(df_valid[llm_col], df_valid[col], labels=categories)

        plt.figure(figsize=(10, 8))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                    xticklabels=categories, yticklabels=categories)
        plt.title(f'Confusion Matrix: {name} vs LLM')
        plt.ylabel('LLM Classification')
        plt.xlabel(f'{name} Classification')

        output_path = output_dir / f'confusion_matrix_{name}.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  Saved confusion matrix: {output_path}")

    # 2. Generate disagreement samples report
    valid_mask = df[annotator_cols + [llm_col]].notna().all(axis=1)
    df_valid = df[valid_mask].copy()

    if len(df_valid) > 0:
        # Find disagreement samples
        disagreements = []

        for _, row in df_valid.iterrows():
            llm_label = row[llm_col]
            annotator_labels = [row[col] for col in annotator_cols]

            # Check if any annotator disagrees with LLM
            if any(label != llm_label for label in annotator_labels):
                disagreements.append({
                    'Annotation_ID': row['Annotation_ID'],
                    'LLM_Classification': llm_label,
                    **{col.replace('_Classification', ''): row[col] for col in annotator_cols},
                    'User_Prompt': row.get('User Prompt', row.get('User_Prompt', '')),
                    'LLM_Response': row.get('LLM Response', row.get('LLM_Response', ''))
                })

        if disagreements:
            disagreement_df = pd.DataFrame(disagreements)
            output_path = output_dir / 'disagreements_detailed.csv'
            disagreement_df.to_csv(output_path, index=False, encoding='utf-8-sig')
            print(f"  Saved disagreement samples: {output_path}")
            print(f"  Disagreement samples: {len(disagreements)}/{len(df_valid)} ({len(disagreements)/len(df_valid)*100:.1f}%)")

    # 3. Generate per-category agreement chart
    valid_mask = df[annotator_cols + [llm_col]].notna().all(axis=1)
    df_valid = df[valid_mask]

    if len(df_valid) > 0 and len(annotator_cols) >= 2:
        # Calculate per-category agreement rates
        per_cat_agreements = {}

        # Annotator vs LLM agreements
        for col in annotator_cols:
            name = col.replace('_Classification', '')
            agreements = calculate_per_category_agreement(df_valid, llm_col, col, categories)
            per_cat_agreements[f'{name} vs LLM'] = agreements

        # Human vs Human agreement (first two annotators)
        if len(annotator_cols) >= 2:
            ann1_name = annotator_cols[0].replace('_Classification', '')
            ann2_name = annotator_cols[1].replace('_Classification', '')
            agreements = calculate_per_category_agreement(df_valid, annotator_cols[0], annotator_cols[1], categories)
            per_cat_agreements[f'{ann1_name} vs {ann2_name}'] = agreements

        # Create bar chart
        x = np.arange(len(categories))
        width = 0.25
        colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#6A994E']

        fig, ax = plt.subplots(figsize=(12, 7))

        comparison_names = list(per_cat_agreements.keys())
        n_comparisons = len(comparison_names)

        # Calculate bar positions
        offsets = np.linspace(-(n_comparisons-1)*width/2, (n_comparisons-1)*width/2, n_comparisons)

        rects_list = []
        for i, (comparison_name, agreements) in enumerate(per_cat_agreements.items()):
            values = [agreements[cat] for cat in categories]
            rects = ax.bar(x + offsets[i], values, width, label=comparison_name, color=colors[i % len(colors)])
            rects_list.append(rects)

        ax.set_ylabel('Agreement (%)', fontsize=12)
        ax.set_xlabel('Category', fontsize=12)
        ax.set_title('Per-Category Agreement Rates', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(categories, fontsize=11)
        ax.legend(fontsize=10)
        ax.set_ylim(0, 110)
        ax.grid(axis='y', alpha=0.3, linestyle='--')

        # Add value labels on bars
        def autolabel(rects):
            for rect in rects:
                height = rect.get_height()
                if height > 0:
                    ax.annotate(f'{height:.1f}%',
                                xy=(rect.get_x() + rect.get_width() / 2, height),
                                xytext=(0, 3),
                                textcoords="offset points",
                                ha='center', va='bottom', fontsize=8)

        for rects in rects_list:
            autolabel(rects)

        plt.tight_layout()
        output_path = output_dir / 'per_category_agreement.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  Saved per-category agreement chart: {output_path}")

        # Save per-category agreement data as CSV
        per_cat_df = pd.DataFrame(per_cat_agreements, index=categories)
        csv_path = output_dir / 'per_category_agreement.csv'
        per_cat_df.to_csv(csv_path, encoding='utf-8-sig')
        print(f"  Saved per-category agreement CSV: {csv_path}")


def generate_agreement_report(inter_results: dict, vs_llm_results: list, output_dir: str):
    """Generate inter-annotator agreement report file"""
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)

    # Create report content
    report_lines = []
    report_lines.append("="*80)
    report_lines.append("INTER-ANNOTATOR AGREEMENT REPORT")
    report_lines.append("="*80)
    report_lines.append("")

    # Overall agreement
    report_lines.append("1. OVERALL AGREEMENT (Fleiss' Kappa)")
    report_lines.append("-" * 80)
    report_lines.append(f"Fleiss' Kappa: {inter_results['fleiss_kappa']:.3f}")
    report_lines.append(f"Interpretation: {inter_results['interpretation']}")
    report_lines.append(f"Number of samples: {inter_results['n_samples']}")
    report_lines.append("")

    # Pairwise agreement
    report_lines.append("2. PAIRWISE AGREEMENT (Cohen's Kappa)")
    report_lines.append("-" * 80)
    for pair in inter_results['pairwise_results']:
        report_lines.append(f"{pair['Annotator1']} vs {pair['Annotator2']}: "
                          f"{pair['Cohen_Kappa']:.3f} (n={pair['N_Samples']})")
    report_lines.append("")

    # Agreement statistics
    report_lines.append("3. AGREEMENT STATISTICS")
    report_lines.append("-" * 80)
    n_samples = inter_results['n_samples']
    all_agree = inter_results['all_agree']
    any_two = inter_results['any_two_agree']
    exactly_two = inter_results['exactly_two_agree']
    no_agreement = inter_results['no_agreement']
    report_lines.append(f"All annotators agree: {all_agree}/{n_samples} ({all_agree/n_samples*100:.1f}%)")
    report_lines.append(f"At least 2 annotators agree: {any_two}/{n_samples} ({any_two/n_samples*100:.1f}%)")
    report_lines.append(f"Exactly 2 annotators agree: {exactly_two}/{n_samples} ({exactly_two/n_samples*100:.1f}%)")
    report_lines.append(f"No agreement (all different): {no_agreement}/{n_samples} ({no_agreement/n_samples*100:.1f}%)")
    report_lines.append("")

    # Annotator vs LLM
    report_lines.append("4. ANNOTATOR VS LLM AGREEMENT")
    report_lines.append("-" * 80)
    for result in vs_llm_results:
        report_lines.append(f"{result['name']} vs LLM:")
        report_lines.append(f"  Accuracy: {result['accuracy']:.2%}")
        report_lines.append(f"  Cohen's Kappa: {result['kappa']:.3f}")
        report_lines.append(f"  Number of samples: {result['n_samples']}")
        report_lines.append("")

    # Write to file
    output_path = output_dir / 'inter_annotator_agreement_report.txt'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))

    print(f"  Saved agreement report: {output_path}")

    # Also save as CSV for easy analysis
    pairwise_df = pd.DataFrame(inter_results['pairwise_results'])
    if len(pairwise_df) > 0:
        csv_path = output_dir / 'pairwise_agreement.csv'
        pairwise_df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f"  Saved pairwise agreement CSV: {csv_path}")

    # Save annotator vs LLM results as CSV
    if vs_llm_results:
        llm_results_df = pd.DataFrame([
            {
                'Annotator': r['name'],
                'Accuracy': f"{r['accuracy']:.4f}",
                'Cohen_Kappa': f"{r['kappa']:.4f}",
                'N_Samples': r['n_samples']
            }
            for r in vs_llm_results
        ])
        csv_path = output_dir / 'annotator_vs_llm_agreement.csv'
        llm_results_df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f"  Saved annotator vs LLM CSV: {csv_path}")


def main():
    """Main function"""
    print("="*60)
    print("Multi-Annotator Analysis - LLM Judge Validation")
    print("="*60)

    # Set up paths
    base_dir = Path(__file__).parent.parent

    # Automatically scan all annotator files
    # File naming pattern: annotator{N}_llm_validation_samples_stratified_*.csv
    annotator_pattern = str(base_dir / 'annotator*_llm_validation_samples_stratified_*.csv')
    annotator_file_paths = sorted(glob.glob(annotator_pattern))

    print(f"\nFound {len(annotator_file_paths)} annotator file(s):")
    for path in annotator_file_paths:
        print(f"  - {Path(path).name}")

    # Build annotator_files dictionary
    annotator_files = {}
    for file_path in annotator_file_paths:
        file_name = Path(file_path).name
        # Extract annotator number from filename, e.g., annotator1 -> Annotator1
        match = re.search(r'annotator(\d+)', file_name)
        if match:
            annotator_num = match.group(1)
            annotator_name = f'Annotator{annotator_num}'
            annotator_files[annotator_name] = Path(file_path)

    if len(annotator_files) == 0:
        print("\nError: No annotator files found!")
        print(f"\nPlease ensure file naming pattern: annotator{{N}}_llm_validation_samples_stratified_*.csv")
        print(f"Scan directory: {base_dir}")
        return

    # Automatically find ground truth file
    # Try to find file matching the annotator file pattern
    gt_pattern = str(base_dir / 'llm_validation_samples_stratified_*_ground_truth.csv')
    gt_files = glob.glob(gt_pattern)

    if len(gt_files) == 0:
        # Fallback to annotation_ground_truth.csv
        gt_pattern = str(base_dir / 'annotation_ground_truth.csv')
        gt_files = glob.glob(gt_pattern)

    if len(gt_files) == 0:
        print("\nError: Ground truth file not found!")
        print(f"Please ensure file exists with naming pattern:")
        print(f"  - llm_validation_samples_stratified_*_ground_truth.csv")
        print(f"  - or annotation_ground_truth.csv")
        return

    ground_truth_file = Path(gt_files[0])  # Use the first file found
    print(f"\nGround Truth file: {ground_truth_file.name}")

    # Load ground truth
    print("\nLoading Ground Truth...")
    gt_df = pd.read_csv(ground_truth_file)
    print(f"  Samples: {len(gt_df)}")

    # Convert LLM classification codes if needed
    if 'LLM_Judge_Classification' in gt_df.columns:
        gt_df = convert_codes_to_labels(gt_df, column='LLM_Judge_Classification')
    elif 'Response_Classification' in gt_df.columns:
        gt_df = convert_codes_to_labels(gt_df, column='Response_Classification')

    # Load all annotators' data
    annotator_dfs = {}
    for name, file_path in annotator_files.items():
        if file_path.exists():
            annotator_dfs[name] = load_annotator_data(str(file_path), name)
        else:
            print(f"\nWarning: File does not exist: {file_path}")

    if len(annotator_dfs) == 0:
        print("\nError: Failed to load any annotator files!")
        return

    # Merge all data
    print("\nMerging data...")
    merged_df = gt_df.copy()
    for name, df in annotator_dfs.items():
        merged_df = merged_df.merge(df, on='Annotation_ID', how='left')

    print(f"  Merged samples: {len(merged_df)}")

    # Extract annotation columns
    annotator_cols = [f'{name}_Classification' for name in annotator_dfs.keys()]

    # Automatically detect LLM classification column name
    if 'LLM_Judge_Classification' in merged_df.columns:
        llm_col = 'LLM_Judge_Classification'
    elif 'Response_Classification' in merged_df.columns:
        llm_col = 'Response_Classification'
    else:
        print("\nError: No LLM classification column found!")
        print("Expected columns: 'LLM_Judge_Classification' or 'Response_Classification'")
        print(f"Available columns: {list(merged_df.columns)}")
        return

    print(f"\nUsing LLM classification column: {llm_col}")

    # Analysis 1: Inter-annotator agreement
    inter_results = analyze_inter_annotator_agreement(merged_df, annotator_cols)

    # Analysis 2: Each annotator vs LLM
    vs_llm_results = analyze_all_vs_llm(merged_df, annotator_cols, llm_col)

    # Generate reports
    output_dir = base_dir / 'results' / 'multi_annotator_analysis'

    # Generate comparison report (confusion matrices and disagreements)
    generate_comparison_report(merged_df, annotator_cols, llm_col, str(output_dir))

    # Generate agreement report (inter-annotator agreement statistics)
    generate_agreement_report(inter_results, vs_llm_results, str(output_dir))

    # Save merged data
    output_file = output_dir / 'merged_annotations.csv'
    merged_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\nSaved merged data: {output_file}")

    print("\n" + "="*60)
    print("Analysis complete!")
    print("="*60)


if __name__ == '__main__':
    main()
