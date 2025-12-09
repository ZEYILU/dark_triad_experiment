"""
准备多标注者文件

自动复制原始标注文件，并为每个标注者创建独立的副本
"""

import shutil
from pathlib import Path


def prepare_annotator_files(source_file: str, n_annotators: int = 3):
    """
    为多个标注者准备文件

    参数:
        source_file: 原始标注文件路径
        n_annotators: 标注者数量（默认3个）
    """
    source_path = Path(source_file)

    if not source_path.exists():
        print(f"错误: 文件不存在: {source_file}")
        return

    print("="*60)
    print("准备多标注者文件")
    print("="*60)

    print(f"\n原始文件: {source_path.name}")
    print(f"标注者数量: {n_annotators}")

    created_files = []

    for i in range(1, n_annotators + 1):
        # 生成新文件名
        new_name = f"annotator{i}_{source_path.name}"
        new_path = source_path.parent / new_name

        # 复制文件
        try:
            shutil.copy2(source_path, new_path)
            created_files.append(new_path)
            print(f"\n[OK] Created: {new_name}")
        except Exception as e:
            print(f"\n[FAIL] Failed: {new_name}")
            print(f"  Error: {e}")

    if created_files:
        print("\n" + "="*60)
        print("文件准备完成！")
        print("="*60)

        print("\n已创建的文件:")
        for i, file_path in enumerate(created_files, 1):
            print(f"  {i}. {file_path.name}")

        print("\n下一步:")
        print("1. 将这些文件分配给不同的标注者")
        print("2. 每个标注者独立完成标注（不要讨论）")
        print("3. 完成后运行: python scripts/analyze_multi_annotators.py")

        print("\n注意:")
        print("- 标注时填入数字代码: 1/2/3/4")
        print("- 参考指南: LLM_VALIDATION_ANNOTATION_GUIDE.txt")
        print("- 详细说明: MULTI_ANNOTATOR_GUIDE.md")
    else:
        print("\n没有成功创建任何文件。")


def main():
    """主函数"""
    # 设置路径
    base_dir = Path(__file__).parent.parent

    # 原始标注文件
    source_file = base_dir / 'llm_validation_samples_stratified_20251127_173744.csv'

    # 检查文件是否存在
    if not source_file.exists():
        print(f"错误: 找不到文件 {source_file}")
        print("\n请确认文件名和路径是否正确")
        print("当前查找的文件:")
        print(f"  {source_file}")
        return

    # 准备文件
    prepare_annotator_files(str(source_file), n_annotators=3)


if __name__ == '__main__':
    main()
