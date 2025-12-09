"""
分层抽样策略 - 用于LLM Judge验证

设计原则：
1. 确保各个维度的代表性（Model, Trait, Severity, Context）
2. 对于重要类别（REINFORCING），优先选择有研究价值的样本
3. 对于边界案例（MIXED），注意包含争议性样本
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import List, Dict

def extract_trait_category(trait: str) -> str:
    """提取主要特质类别"""
    if 'Machiavellianism' in trait or trait.startswith('M'):
        return 'M'
    elif 'Narcissism' in trait or trait.startswith('N'):
        return 'N'
    elif 'Psychopathy' in trait or trait.startswith('P'):
        return 'P'
    elif 'Mixed' in trait:
        return 'Mixed'
    else:
        return 'Other'


def sample_refusal(df: pd.DataFrame) -> pd.DataFrame:
    """
    REFUSAL类别：全部抽取（只有14个）

    特点：
    - 全部是HIGH severity
    - 主要是gpt-4o (12/14)
    """
    refusal_df = df[df['Judge_Classification'] == 'REFUSAL'].copy()
    print(f"\nREFUSAL: 全部抽取 {len(refusal_df)} 个样本")
    return refusal_df


def sample_reinforcing(df: pd.DataFrame, n_samples: int = 14, random_seed: int = 42) -> pd.DataFrame:
    """
    REINFORCING类别：最重要的类别，需要精心选择

    策略：
    - 按Model比例分配
    - 在每个Model内考虑Trait和Context的多样性
    - 优先选择有研究价值的样本
    """
    reinforcing_df = df[df['Judge_Classification'] == 'REINFORCING'].copy()
    total = len(reinforcing_df)

    print(f"\nREINFORCING: 从 {total} 个样本中抽取 {n_samples} 个")

    # Model分配（按比例）
    model_allocation = {
        'gpt-3.5-turbo': 6,      # 15/32 * 14 ≈ 6.5
        'gpt-4o-mini': 5,        # 12/32 * 14 ≈ 5.3
        'gpt-4o': 3              # 5/32 * 14 ≈ 2.2
    }

    sampled_list = []

    for model, n in model_allocation.items():
        model_df = reinforcing_df[reinforcing_df['Model'] == model]

        if len(model_df) == 0:
            print(f"  警告: {model} 没有样本")
            continue

        print(f"  {model}: 从 {len(model_df)} 个样本中抽取 {n} 个")

        # 在model内进行分层抽样
        # 优先考虑：不同的Trait和Context
        model_df['Trait_Category'] = model_df['Primary_Trait'].apply(extract_trait_category)

        # 统计各trait的样本数
        trait_counts = model_df['Trait_Category'].value_counts()

        # 尝试每个trait至少选1个
        trait_samples = []
        remaining_n = n

        for trait in ['M', 'N', 'P', 'Mixed']:
            trait_df = model_df[model_df['Trait_Category'] == trait]
            if len(trait_df) > 0 and remaining_n > 0:
                # 每个trait选1个
                sample = trait_df.sample(n=1, random_state=random_seed)
                trait_samples.append(sample)
                remaining_n -= 1

        # 剩余的样本随机抽取
        if remaining_n > 0:
            already_selected = pd.concat(trait_samples) if trait_samples else pd.DataFrame()
            remaining_df = model_df[~model_df.index.isin(already_selected.index)]

            if len(remaining_df) >= remaining_n:
                additional = remaining_df.sample(n=remaining_n, random_state=random_seed)
                trait_samples.append(additional)
            else:
                trait_samples.append(remaining_df)

        model_sampled = pd.concat(trait_samples) if trait_samples else pd.DataFrame()
        sampled_list.append(model_sampled)

    final_samples = pd.concat(sampled_list, ignore_index=True)
    print(f"  实际抽取: {len(final_samples)} 个样本")

    return final_samples


def sample_mixed(df: pd.DataFrame, n_samples: int = 14, random_seed: int = 42) -> pd.DataFrame:
    """
    MIXED类别：边界案例，需要多样性

    策略：
    - 按Model比例分配
    - 确保不同Trait都有代表
    - 优先选择有争议的样本
    """
    mixed_df = df[df['Judge_Classification'] == 'MIXED'].copy()
    total = len(mixed_df)

    print(f"\nMIXED: 从 {total} 个样本中抽取 {n_samples} 个")

    # Model分配
    model_allocation = {
        'gpt-4o': 4,                        # 12/38 * 14 ≈ 4.4
        'gpt-4o-mini': 4,                   # 12/38 * 14 ≈ 4.4
        'gpt-3.5-turbo': 3,                 # 7/38 * 14 ≈ 2.6
        'claude-sonnet-4-5-20250929': 2,    # 4/38 * 14 ≈ 1.5
        'claude-haiku-4-5-20251001': 1      # 3/38 * 14 ≈ 1.1
    }

    sampled_list = []

    for model, n in model_allocation.items():
        model_df = mixed_df[mixed_df['Model'] == model]

        if len(model_df) == 0:
            print(f"  警告: {model} 没有样本")
            continue

        if len(model_df) < n:
            print(f"  {model}: 样本不足，抽取全部 {len(model_df)} 个")
            sampled_list.append(model_df)
        else:
            print(f"  {model}: 从 {len(model_df)} 个样本中抽取 {n} 个")

            # 添加trait类别
            model_df['Trait_Category'] = model_df['Primary_Trait'].apply(extract_trait_category)

            # 尝试每个trait选1个（如果有的话）
            trait_samples = []
            remaining_n = n

            for trait in ['M', 'N', 'P', 'Mixed']:
                trait_df = model_df[model_df['Trait_Category'] == trait]
                if len(trait_df) > 0 and remaining_n > 0:
                    sample = trait_df.sample(n=1, random_state=random_seed)
                    trait_samples.append(sample)
                    remaining_n -= 1

            # 剩余的随机抽取
            if remaining_n > 0:
                already_selected = pd.concat(trait_samples) if trait_samples else pd.DataFrame()
                remaining_df = model_df[~model_df.index.isin(already_selected.index)]

                if len(remaining_df) >= remaining_n:
                    additional = remaining_df.sample(n=remaining_n, random_state=random_seed)
                    trait_samples.append(additional)
                else:
                    trait_samples.append(remaining_df)

            model_sampled = pd.concat(trait_samples) if trait_samples else pd.DataFrame()
            sampled_list.append(model_sampled)

    final_samples = pd.concat(sampled_list, ignore_index=True)
    print(f"  实际抽取: {len(final_samples)} 个样本")

    return final_samples


def sample_corrective(df: pd.DataFrame, n_samples: int = 14, random_seed: int = 42) -> pd.DataFrame:
    """
    CORRECTIVE类别：样本量最大，需要确保代表性

    策略：
    - 每个Model选约3个样本
    - 在每个Model内确保Trait、Severity、Context的多样性
    """
    corrective_df = df[df['Judge_Classification'] == 'CORRECTIVE'].copy()
    total = len(corrective_df)

    print(f"\nCORRECTIVE: 从 {total} 个样本中抽取 {n_samples} 个")

    # Model分配（尽量平均）
    model_allocation = {
        'claude-haiku-4-5-20251001': 3,
        'claude-sonnet-4-5-20250929': 3,
        'gpt-3.5-turbo': 3,
        'gpt-4o': 3,
        'gpt-4o-mini': 2
    }

    sampled_list = []

    for model, n in model_allocation.items():
        model_df = corrective_df[corrective_df['Model'] == model]

        if len(model_df) == 0:
            print(f"  警告: {model} 没有样本")
            continue

        print(f"  {model}: 从 {len(model_df)} 个样本中抽取 {n} 个")

        # 多维度分层抽样
        model_df['Trait_Category'] = model_df['Primary_Trait'].apply(extract_trait_category)

        # 策略：先按Trait分，再在Trait内按Severity分
        samples = []
        remaining_n = n

        # 确保M/N/P三个主要trait都有代表
        main_traits = ['M', 'N', 'P']
        samples_per_trait = remaining_n // len(main_traits)  # 每个trait选1个

        for trait in main_traits:
            trait_df = model_df[model_df['Trait_Category'] == trait]
            if len(trait_df) > 0 and remaining_n > 0:
                # 在该trait内，尽量选不同的severity
                severities = ['LOW', 'MEDIUM', 'HIGH']
                trait_sample = None

                for severity in severities:
                    severity_df = trait_df[trait_df['Severity'] == severity]
                    if len(severity_df) > 0:
                        trait_sample = severity_df.sample(n=1, random_state=random_seed)
                        break

                if trait_sample is None:
                    trait_sample = trait_df.sample(n=1, random_state=random_seed)

                samples.append(trait_sample)
                remaining_n -= 1

        # 剩余的样本随机抽取（但确保diversity）
        if remaining_n > 0:
            already_selected = pd.concat(samples) if samples else pd.DataFrame()
            remaining_df = model_df[~model_df.index.isin(already_selected.index)]

            if len(remaining_df) >= remaining_n:
                # 尝试选择不同的context
                contexts = remaining_df['Context'].unique()
                context_samples = []

                for context in contexts:
                    if remaining_n <= 0:
                        break
                    context_df = remaining_df[remaining_df['Context'] == context]
                    if len(context_df) > 0:
                        sample = context_df.sample(n=1, random_state=random_seed)
                        context_samples.append(sample)
                        remaining_n -= 1

                if context_samples:
                    samples.extend(context_samples)
            else:
                samples.append(remaining_df)

        model_sampled = pd.concat(samples) if samples else pd.DataFrame()
        sampled_list.append(model_sampled)

    final_samples = pd.concat(sampled_list, ignore_index=True)
    print(f"  实际抽取: {len(final_samples)} 个样本")

    return final_samples


def main():
    """主函数"""
    print("="*60)
    print("分层抽样 - LLM Judge验证")
    print("="*60)

    # 设置路径
    base_dir = Path(__file__).parent.parent
    results_dir = base_dir / 'results'
    input_file = results_dir / 'llm_judge_results_20251126_194023.csv'

    # 读取数据
    print(f"\n正在读取文件: {input_file}")
    df = pd.read_csv(input_file)

    # 只保留成功处理的样本
    df = df[df['Success'] == True].copy()
    print(f"成功处理的样本数: {len(df)}")

    # 过滤掉空白响应的样本
    before_filter = len(df)
    df = df[df['LLM_Response'].notna() & (df['LLM_Response'] != '')].copy()
    filtered_count = before_filter - len(df)
    if filtered_count > 0:
        print(f"过滤掉空白响应样本: {filtered_count} 个")
    print(f"有效样本数: {len(df)}")

    # 设置随机种子
    random_seed = 42
    np.random.seed(random_seed)

    # 分别抽样每个类别
    refusal_samples = sample_refusal(df)
    reinforcing_samples = sample_reinforcing(df, n_samples=14, random_seed=random_seed)
    mixed_samples = sample_mixed(df, n_samples=14, random_seed=random_seed)
    corrective_samples = sample_corrective(df, n_samples=14, random_seed=random_seed)

    # 合并所有样本
    all_samples = pd.concat([
        refusal_samples,
        reinforcing_samples,
        mixed_samples,
        corrective_samples
    ], ignore_index=True)

    # 打乱顺序（避免按分类排序导致bias）
    all_samples = all_samples.sample(frac=1, random_state=random_seed).reset_index(drop=True)

    print("\n" + "="*60)
    print(f"总样本数: {len(all_samples)}")
    print("="*60)

    # 创建人工标注所需的DataFrame
    annotation_df = pd.DataFrame({
        'Annotation_ID': range(1, len(all_samples) + 1),
        'Model': all_samples['Model'],
        'User_Prompt': all_samples['User_Prompt'],
        'LLM_Response': all_samples['LLM_Response'],
        'Severity': all_samples['Severity'],
        'Primary_Trait': all_samples['Primary_Trait'],
        'Context': all_samples['Context'],
        'LLM_Judge_Classification': all_samples['Judge_Classification'],
        'LLM_Judge_Confidence': all_samples['Judge_Confidence'],
        'LLM_Judge_Reasoning': all_samples['Judge_Reasoning'],
        'Human_Classification': '',
        'Confidence': '',
        'Notes': ''
    })

    # 生成输出文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = base_dir / f'llm_validation_samples_stratified_{timestamp}.csv'
    ground_truth_file = base_dir / f'llm_validation_samples_stratified_{timestamp}_ground_truth.csv'

    # 保存人工标注文件（不包含LLM判断结果，只保留必要的列）
    annotation_df_for_human = annotation_df[[
        'Annotation_ID', 'User_Prompt', 'LLM_Response',
        'Human_Classification', 'Confidence', 'Notes'
    ]].copy()
    annotation_df_for_human.to_csv(output_file, index=False, encoding='utf-8-sig')

    # 保存ground truth文件
    annotation_df.to_csv(ground_truth_file, index=False, encoding='utf-8-sig')

    print("\n文件输出:")
    print(f"  1. 人工标注文件: {output_file}")
    print(f"  2. Ground Truth文件: {ground_truth_file}")

    # 显示最终的分布统计
    print("\n" + "="*60)
    print("样本分布统计")
    print("="*60)

    print("\n分类分布:")
    print(annotation_df['LLM_Judge_Classification'].value_counts())

    print("\n模型分布:")
    print(annotation_df['Model'].value_counts())

    print("\n特质分布:")
    print(annotation_df['Primary_Trait'].value_counts())

    print("\n严重程度分布:")
    print(annotation_df['Severity'].value_counts())

    print("\nContext分布:")
    print(annotation_df['Context'].value_counts())

    # 交叉分析：Classification × Model
    print("\n分类 × 模型交叉表:")
    cross_tab = pd.crosstab(annotation_df['LLM_Judge_Classification'], annotation_df['Model'])
    print(cross_tab)

    print("\n" + "="*60)
    print("抽样完成！")
    print("="*60)


if __name__ == '__main__':
    main()
