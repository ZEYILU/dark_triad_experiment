"""验证分层抽样的质量"""

import pandas as pd
from pathlib import Path

def main():
    base_dir = Path(__file__).parent.parent
    file_path = base_dir / 'llm_validation_samples_stratified_20251127_172645_ground_truth.csv'

    df = pd.read_csv(file_path)

    print("="*60)
    print("分层抽样质量验证报告")
    print("="*60)

    categories = ['REFUSAL', 'REINFORCING', 'MIXED', 'CORRECTIVE']

    for cls in categories:
        print(f"\n{'='*60}")
        print(f"{cls} (n={len(df[df['LLM_Judge_Classification'] == cls])})")
        print('='*60)

        cls_df = df[df['LLM_Judge_Classification'] == cls]

        print("\nModel distribution:")
        model_dist = cls_df['Model'].value_counts()
        for model, count in model_dist.items():
            print(f"  {model}: {count}")

        print("\nPrimary Trait distribution:")
        trait_dist = cls_df['Primary_Trait'].value_counts()
        for trait, count in trait_dist.items():
            print(f"  {trait}: {count}")

        print("\nSeverity distribution:")
        severity_dist = cls_df['Severity'].value_counts()
        for severity, count in severity_dist.items():
            print(f"  {severity}: {count}")

        print("\nContext distribution:")
        context_dist = cls_df['Context'].value_counts()
        for context, count in context_dist.items():
            print(f"  {context}: {count}")

    print("\n" + "="*60)
    print("Summary Statistics")
    print("="*60)

    print("\n1. Model coverage across all categories:")
    for model in df['Model'].unique():
        model_df = df[df['Model'] == model]
        classifications = model_df['LLM_Judge_Classification'].value_counts()
        print(f"\n  {model} (total: {len(model_df)}):")
        for cls, count in classifications.items():
            print(f"    {cls}: {count}")

    print("\n2. Trait category coverage:")
    def get_trait_category(trait):
        if 'Machiavellianism' in trait:
            return 'M'
        elif 'Narcissism' in trait:
            return 'N'
        elif 'Psychopathy' in trait:
            return 'P'
        else:
            return 'Mixed'

    df['Trait_Category'] = df['Primary_Trait'].apply(get_trait_category)
    trait_cat_dist = df['Trait_Category'].value_counts()
    for trait_cat, count in trait_cat_dist.items():
        print(f"  {trait_cat}: {count}")

    print("\n3. Severity coverage:")
    severity_dist = df['Severity'].value_counts()
    for severity, count in severity_dist.items():
        print(f"  {severity}: {count}")

    print("\n4. Context coverage:")
    context_dist = df['Context'].value_counts()
    for context, count in context_dist.items():
        print(f"  {context}: {count}")

    print("\n" + "="*60)
    print("Validation Complete!")
    print("="*60)


if __name__ == '__main__':
    main()
