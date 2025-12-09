"""
从LLM Judge结果中抽取样本用于人工标注验证

目的：从每个分类（CORRECTIVE、REFUSAL、MIXED、REINFORCING）中随机抽取14个样本
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

def sample_llm_results_for_validation(
    input_file: str,
    output_file: str,
    samples_per_category: int = 14,
    random_seed: int = 42
):
    """
    从LLM judge结果中抽取样本用于人工标注验证

    参数:
        input_file: LLM judge结果CSV文件路径
        output_file: 输出的人工标注样本CSV文件路径
        samples_per_category: 每个分类抽取的样本数（默认14）
        random_seed: 随机种子，用于保证可重复性
    """

    # 设置随机种子
    np.random.seed(random_seed)

    print(f"正在读取文件: {input_file}")
    df = pd.read_csv(input_file)

    print(f"\n总样本数: {len(df)}")
    print(f"成功处理的样本数: {df['Success'].sum()}")

    # 只保留成功处理的样本
    df = df[df['Success'] == True].copy()

    # 统计每个分类的样本数
    print("\n各分类样本数统计:")
    classification_counts = df['Judge_Classification'].value_counts()
    print(classification_counts)

    # 检查每个分类是否有足够的样本
    target_categories = ['CORRECTIVE', 'REFUSAL', 'MIXED', 'REINFORCING']
    print(f"\n目标分类: {target_categories}")
    print(f"每个分类需要抽取: {samples_per_category} 个样本")

    sampled_dfs = []

    for category in target_categories:
        category_df = df[df['Judge_Classification'] == category]
        available_count = len(category_df)

        print(f"\n{category}:")
        print(f"  可用样本数: {available_count}")

        if available_count < samples_per_category:
            print(f"  WARNING: 可用样本少于目标数量，将抽取全部 {available_count} 个样本")
            sampled = category_df.copy()
        else:
            # 随机抽样
            sampled = category_df.sample(n=samples_per_category, random_state=random_seed)
            print(f"  OK: 已抽取 {samples_per_category} 个样本")

        sampled_dfs.append(sampled)

    # 合并所有抽样结果
    final_samples = pd.concat(sampled_dfs, ignore_index=True)

    # 打乱顺序（避免按分类排序导致标注bias）
    final_samples = final_samples.sample(frac=1, random_state=random_seed).reset_index(drop=True)

    # 创建人工标注所需的列
    annotation_df = pd.DataFrame({
        'Annotation_ID': range(1, len(final_samples) + 1),
        'Model': final_samples['Model'],
        'User_Prompt': final_samples['User_Prompt'],
        'LLM_Response': final_samples['LLM_Response'],
        'Severity': final_samples['Severity'],
        'Primary_Trait': final_samples['Primary_Trait'],
        'Context': final_samples['Context'],
        'LLM_Judge_Classification': final_samples['Judge_Classification'],
        'LLM_Judge_Confidence': final_samples['Judge_Confidence'],
        'LLM_Judge_Reasoning': final_samples['Judge_Reasoning'],
        'Human_Classification': '',  # 待人工标注
        'Confidence': '',  # 待人工标注
        'Notes': ''  # 待人工标注
    })

    # 保存人工标注文件（不包含LLM判断结果，避免bias）
    annotation_df_for_human = annotation_df[[
        'Annotation_ID', 'Model', 'User_Prompt', 'LLM_Response',
        'Severity', 'Primary_Trait', 'Context',
        'Human_Classification', 'Confidence', 'Notes'
    ]].copy()
    annotation_df_for_human.to_csv(output_file, index=False, encoding='utf-8-sig')

    # 保存ground truth文件（包含LLM判断结果）
    ground_truth_file = output_file.replace('.csv', '_ground_truth.csv')
    annotation_df.to_csv(ground_truth_file, index=False, encoding='utf-8-sig')

    print(f"\n" + "="*60)
    print(f"抽样完成!")
    print(f"总样本数: {len(annotation_df)}")
    print(f"\n文件输出:")
    print(f"  1. 人工标注文件: {output_file}")
    print(f"  2. Ground Truth文件: {ground_truth_file}")
    print("="*60)

    # 显示最终的分类分布
    print("\n最终样本的分类分布:")
    final_distribution = annotation_df['LLM_Judge_Classification'].value_counts()
    print(final_distribution)

    # 显示模型分布
    print("\n样本的模型分布:")
    model_distribution = annotation_df['Model'].value_counts()
    print(model_distribution)

    # 显示特质分布
    print("\n样本的特质分布:")
    trait_distribution = annotation_df['Primary_Trait'].value_counts()
    print(trait_distribution)

    # 显示严重程度分布
    print("\n样本的严重程度分布:")
    severity_distribution = annotation_df['Severity'].value_counts()
    print(severity_distribution)

    return annotation_df


def main():
    # 设置路径
    base_dir = Path(__file__).parent.parent
    results_dir = base_dir / 'results'

    # 使用最新的LLM judge结果文件
    input_file = results_dir / 'llm_judge_results_20251126_194023.csv'

    # 生成输出文件名（带时间戳）
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = base_dir / f'llm_validation_samples_{timestamp}.csv'

    # 执行抽样
    annotation_df = sample_llm_results_for_validation(
        input_file=str(input_file),
        output_file=str(output_file),
        samples_per_category=14,
        random_seed=42
    )

    print("\n" + "="*60)
    print("接下来的步骤:")
    print("1. 打开人工标注文件（不包含LLM判断结果，避免bias）")
    print("2. 参考 ANNOTATION_GUIDE.txt 进行标注")
    print("3. 在以下列中填写标注结果:")
    print("   - Human_Classification: 填入 REFUSAL/REINFORCING/CORRECTIVE/MIXED")
    print("   - Confidence: 填入 Low/Medium/High")
    print("   - Notes: 记录任何疑问或特殊情况")
    print("\n注意:")
    print("- 标注时请勿查看 ground_truth 文件")
    print("- Ground truth 文件保存了LLM的判断结果，用于后续对比分析")
    print("="*60)


if __name__ == '__main__':
    main()
