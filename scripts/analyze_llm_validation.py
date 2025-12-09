"""
分析LLM判断结果与人工标注的一致性

用于评估LLM Judge的准确性和可靠性
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.metrics import (
    confusion_matrix,
    classification_report,
    cohen_kappa_score,
    accuracy_score
)
import seaborn as sns
import matplotlib.pyplot as plt

def load_and_merge_data(human_file: str, ground_truth_file: str):
    """
    加载人工标注文件和ground truth文件，并合并

    参数:
        human_file: 人工标注完成的CSV文件
        ground_truth_file: 包含LLM判断结果的CSV文件

    返回:
        合并后的DataFrame
    """
    print("正在加载文件...")

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

    # 读取人工标注结果
    human_df = pd.read_csv(human_file)
    print(f"人工标注样本数: {len(human_df)}")

    # 读取ground truth
    gt_df = pd.read_csv(ground_truth_file)
    print(f"Ground truth样本数: {len(gt_df)}")

    # 确保两个文件的样本数量一致
    assert len(human_df) == len(gt_df), "人工标注和ground truth的样本数不一致！"

    # 检查人工标注是否完成
    missing_annotations = human_df['Human_Classification'].isna().sum()
    if missing_annotations > 0:
        print(f"\nWARNING: 有 {missing_annotations} 个样本未完成标注")
        print("未完成标注的样本ID:")
        print(human_df[human_df['Human_Classification'].isna()]['Annotation_ID'].tolist())

    # 将数字代码转换为文本标签（如果需要）
    # 检查是否使用了数字代码
    human_df_valid = human_df[human_df['Human_Classification'].notna()].copy()
    if len(human_df_valid) > 0:
        # 检查第一个非空值的类型
        first_value = human_df_valid['Human_Classification'].iloc[0]
        if isinstance(first_value, (int, float)) or (isinstance(first_value, str) and first_value.isdigit()):
            print("\n检测到数字代码，正在转换为文本标签...")
            human_df['Human_Classification'] = human_df['Human_Classification'].map(
                lambda x: CODE_TO_LABEL.get(x, x) if pd.notna(x) else x
            )
            print("转换完成！")

    # 合并数据（基于Annotation_ID）
    merged_df = pd.merge(
        human_df[['Annotation_ID', 'Human_Classification', 'Confidence', 'Notes']],
        gt_df,
        on='Annotation_ID',
        how='inner'
    )

    print(f"合并后样本数: {len(merged_df)}")

    return merged_df


def calculate_agreement_metrics(df: pd.DataFrame):
    """
    计算人工标注与LLM判断的一致性指标
    """
    print("\n" + "="*60)
    print("一致性分析")
    print("="*60)

    # 移除未标注的样本
    df_valid = df[df['Human_Classification'].notna()].copy()

    human_labels = df_valid['Human_Classification']
    llm_labels = df_valid['LLM_Judge_Classification']

    # 整体准确率
    accuracy = accuracy_score(human_labels, llm_labels)
    print(f"\n整体一致性 (Accuracy): {accuracy:.2%}")

    # Cohen's Kappa（考虑随机一致性）
    kappa = cohen_kappa_score(human_labels, llm_labels)
    print(f"Cohen's Kappa: {kappa:.3f}")

    # Kappa解释
    if kappa < 0:
        kappa_interpretation = "差于随机"
    elif kappa < 0.20:
        kappa_interpretation = "轻微一致"
    elif kappa < 0.40:
        kappa_interpretation = "一般一致"
    elif kappa < 0.60:
        kappa_interpretation = "中等一致"
    elif kappa < 0.80:
        kappa_interpretation = "高度一致"
    else:
        kappa_interpretation = "几乎完全一致"
    print(f"Kappa解释: {kappa_interpretation}")

    # 一致和不一致的样本数
    agreement = (human_labels == llm_labels).sum()
    disagreement = (human_labels != llm_labels).sum()
    print(f"\n一致样本数: {agreement}")
    print(f"不一致样本数: {disagreement}")

    return accuracy, kappa


def analyze_by_category(df: pd.DataFrame):
    """
    按分类分析LLM的表现
    """
    print("\n" + "="*60)
    print("各分类准确率分析")
    print("="*60)

    df_valid = df[df['Human_Classification'].notna()].copy()

    categories = ['CORRECTIVE', 'REFUSAL', 'MIXED', 'REINFORCING']

    for category in categories:
        # LLM判断为该类别的样本
        llm_category = df_valid[df_valid['LLM_Judge_Classification'] == category]

        if len(llm_category) == 0:
            continue

        # 人工标注也判断为该类别的数量
        correct = (llm_category['Human_Classification'] == category).sum()
        total = len(llm_category)
        precision = correct / total if total > 0 else 0

        print(f"\n{category}:")
        print(f"  LLM判断为此类的样本数: {total}")
        print(f"  人工标注一致的样本数: {correct}")
        print(f"  精确率 (Precision): {precision:.2%}")


def analyze_by_confidence(df: pd.DataFrame):
    """
    按人工标注confidence分析
    """
    print("\n" + "="*60)
    print("按标注信心度分析")
    print("="*60)

    df_valid = df[df['Human_Classification'].notna()].copy()

    confidence_levels = ['High', 'Medium', 'Low']

    for conf in confidence_levels:
        conf_df = df_valid[df_valid['Confidence'] == conf]

        if len(conf_df) == 0:
            continue

        agreement = (conf_df['Human_Classification'] == conf_df['LLM_Judge_Classification']).sum()
        total = len(conf_df)
        agreement_rate = agreement / total if total > 0 else 0

        print(f"\n{conf} Confidence:")
        print(f"  样本数: {total}")
        print(f"  一致样本数: {agreement}")
        print(f"  一致率: {agreement_rate:.2%}")


def generate_confusion_matrix(df: pd.DataFrame, output_dir: str):
    """
    生成混淆矩阵
    """
    print("\n" + "="*60)
    print("混淆矩阵")
    print("="*60)

    df_valid = df[df['Human_Classification'].notna()].copy()

    human_labels = df_valid['Human_Classification']
    llm_labels = df_valid['LLM_Judge_Classification']

    # 定义类别顺序
    categories = ['REFUSAL', 'REINFORCING', 'CORRECTIVE', 'MIXED']

    # 生成混淆矩阵
    cm = confusion_matrix(human_labels, llm_labels, labels=categories)

    # 打印文本版混淆矩阵
    print("\n混淆矩阵 (行=人工标注, 列=LLM判断):")
    print(f"{'':15} " + " ".join([f"{c:12}" for c in categories]))
    for i, category in enumerate(categories):
        print(f"{category:15} " + " ".join([f"{cm[i][j]:12}" for j in range(len(categories))]))

    # 生成分类报告
    print("\n分类报告:")
    report = classification_report(
        human_labels,
        llm_labels,
        labels=categories,
        target_names=categories,
        digits=3
    )
    print(report)

    # 可视化混淆矩阵（如果安装了matplotlib和seaborn）
    try:
        plt.figure(figsize=(10, 8))
        sns.heatmap(
            cm,
            annot=True,
            fmt='d',
            cmap='Blues',
            xticklabels=categories,
            yticklabels=categories
        )
        plt.title('Confusion Matrix: Human vs LLM Classification')
        plt.ylabel('Human Classification')
        plt.xlabel('LLM Classification')

        output_path = Path(output_dir) / 'confusion_matrix.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"\n混淆矩阵图已保存至: {output_path}")
        plt.close()
    except Exception as e:
        print(f"\n无法生成混淆矩阵图: {e}")


def analyze_disagreements(df: pd.DataFrame, output_file: str):
    """
    分析不一致的样本
    """
    print("\n" + "="*60)
    print("不一致样本分析")
    print("="*60)

    df_valid = df[df['Human_Classification'].notna()].copy()

    # 找出不一致的样本
    disagreements = df_valid[
        df_valid['Human_Classification'] != df_valid['LLM_Judge_Classification']
    ].copy()

    print(f"\n不一致样本数: {len(disagreements)}")

    if len(disagreements) > 0:
        # 统计不一致的模式
        print("\n不一致模式统计:")
        disagreement_patterns = disagreements.groupby(
            ['LLM_Judge_Classification', 'Human_Classification']
        ).size().sort_values(ascending=False)

        for (llm_class, human_class), count in disagreement_patterns.items():
            print(f"  LLM判断为 {llm_class}, 人工标注为 {human_class}: {count}个")

        # 保存不一致样本到文件
        disagreement_output = disagreements[[
            'Annotation_ID', 'Model', 'LLM_Judge_Classification',
            'Human_Classification', 'Confidence', 'Notes',
            'User_Prompt', 'LLM_Response', 'LLM_Judge_Reasoning'
        ]].copy()

        disagreement_output.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\n不一致样本已保存至: {output_file}")


def analyze_by_model(df: pd.DataFrame):
    """
    按模型分析LLM判断的准确性
    """
    print("\n" + "="*60)
    print("按模型分析")
    print("="*60)

    df_valid = df[df['Human_Classification'].notna()].copy()

    models = df_valid['Model'].unique()

    for model in models:
        model_df = df_valid[df_valid['Model'] == model]

        if len(model_df) == 0:
            continue

        agreement = (model_df['Human_Classification'] == model_df['LLM_Judge_Classification']).sum()
        total = len(model_df)
        agreement_rate = agreement / total if total > 0 else 0

        print(f"\n{model}:")
        print(f"  样本数: {total}")
        print(f"  一致样本数: {agreement}")
        print(f"  一致率: {agreement_rate:.2%}")


def main():
    """
    主函数：执行完整的一致性分析
    """
    # 设置路径
    base_dir = Path(__file__).parent.parent

    # 输入文件（需要根据实际生成的文件名修改）
    # 使用分层抽样的文件（已过滤空白响应）
    human_file = base_dir / 'llm_validation_samples_stratified_20251127_173744.csv'  # 人工标注完成的文件
    ground_truth_file = base_dir / 'llm_validation_samples_stratified_20251127_173744_ground_truth.csv'

    # 输出文件
    disagreement_file = base_dir / 'llm_validation_disagreements.csv'
    output_dir = base_dir / 'results'
    output_dir.mkdir(exist_ok=True)

    # 加载数据
    df = load_and_merge_data(str(human_file), str(ground_truth_file))

    # 执行分析
    calculate_agreement_metrics(df)
    analyze_by_category(df)
    analyze_by_confidence(df)
    analyze_by_model(df)
    generate_confusion_matrix(df, str(output_dir))
    analyze_disagreements(df, str(disagreement_file))

    print("\n" + "="*60)
    print("分析完成！")
    print("="*60)


if __name__ == '__main__':
    main()
