import pandas as pd
import os

# 定义文件路径
base_dir = r"D:\masterthesis\experiment\dark_triad_experiment\dataset_to_be_merged"
output_dir = r"D:\masterthesis\experiment\dark_triad_experiment\data"

# 确保输出目录存在
os.makedirs(output_dir, exist_ok=True)

# 读取三个CSV文件
file1 = os.path.join(base_dir, "Dark_Triad_Dataset_V1_FINAL_BALANCED.csv")
file2 = os.path.join(base_dir, "Dark_Triad_Dataset_V2_KEEP_12prompts.csv")
file3 = os.path.join(base_dir, "Dark_Triad_Dataset_V2_NEW_54prompts.csv")

print("正在读取文件...")
df1 = pd.read_csv(file1)
df2 = pd.read_csv(file2)
df3 = pd.read_csv(file3)

print(f"文件1: {len(df1)} 行")
print(f"文件2: {len(df2)} 行")
print(f"文件3: {len(df3)} 行")

# 合并所有数据
merged_df = pd.concat([df1, df2, df3], ignore_index=True)
print(f"\n合并后总共: {len(merged_df)} 行")

# 显示基本信息
print("\n合并后的数据集信息:")
print(merged_df.info())
print("\n各特征分布:")
print(merged_df['Primary Trait'].value_counts())
print("\n严重程度分布:")
print(merged_df['Severity'].value_counts())

# 保存合并后的文件
output_file = os.path.join(output_dir, "Dark_Triad_Dataset_Merged.csv")
merged_df.to_csv(output_file, index=False, encoding='utf-8')
print(f"\n合并后的文件已保存到: {output_file}")
