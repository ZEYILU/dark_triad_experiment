"""
创建演示标注数据

用于测试多标注者分析脚本
"""

import pandas as pd
from pathlib import Path
import random

# 设置随机种子
random.seed(42)


def create_demo_annotations():
    """创建演示标注数据"""

    base_dir = Path(__file__).parent.parent

    # 读取原始文件
    source_file = base_dir / 'llm_validation_samples_stratified_20251127_173744.csv'
    df = pd.read_csv(source_file)

    print("="*60)
    print("创建演示标注数据")
    print("="*60)
    print(f"\n总样本数: {len(df)}")

    # 为每个标注者创建不同的标注模式

    # Annotator 1: 与LLM一致性较高（80%一致）
    # Annotator 2: 与LLM一致性中等（70%一致）
    # Annotator 3: 与LLM一致性较低（60%一致）

    # 读取ground truth获取LLM的判断
    gt_file = base_dir / 'llm_validation_samples_stratified_20251127_173744_ground_truth.csv'
    gt_df = pd.read_csv(gt_file)

    # 映射：文本标签 -> 数字代码
    label_to_code = {
        'REFUSAL': 1,
        'REINFORCING': 2,
        'CORRECTIVE': 3,
        'MIXED': 4
    }

    # 获取LLM的判断
    llm_labels = gt_df['LLM_Judge_Classification'].tolist()

    # 为每个标注者生成标注
    for annotator_num, agreement_rate in [(1, 0.80), (2, 0.70), (3, 0.60)]:
        annotator_file = base_dir / f'annotator{annotator_num}_llm_validation_samples_stratified_20251127_173744.csv'
        df_annotator = df.copy()

        classifications = []
        confidences = []

        for i, llm_label in enumerate(llm_labels):
            # 根据一致性比例决定是否与LLM一致
            if random.random() < agreement_rate:
                # 与LLM一致
                code = label_to_code.get(llm_label, 3)
                confidence = 'High'
            else:
                # 不一致 - 随机选择其他标签
                other_labels = [k for k in label_to_code.keys() if k != llm_label]
                random_label = random.choice(other_labels)
                code = label_to_code[random_label]
                confidence = random.choice(['Medium', 'Low'])

            classifications.append(code)
            confidences.append(confidence)

        df_annotator['Human_Classification'] = classifications
        df_annotator['Confidence'] = confidences
        df_annotator['Notes'] = ''

        # 保存
        df_annotator.to_csv(annotator_file, index=False, encoding='utf-8-sig')
        print(f"\n[OK] Created demo annotations for Annotator {annotator_num}")
        print(f"  Target agreement with LLM: {agreement_rate:.0%}")
        print(f"  Saved to: {annotator_file.name}")

    print("\n" + "="*60)
    print("演示数据创建完成！")
    print("="*60)
    print("\n可以运行以下命令测试分析:")
    print("  python scripts/analyze_multi_annotators.py")


if __name__ == '__main__':
    create_demo_annotations()
