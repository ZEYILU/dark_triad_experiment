# 多标注者验证指南

## 📋 概述

本指南用于**3个标注者**共同完成55个样本的标注，并分析：
1. 标注者之间的一致性（Inter-rater reliability）
2. 每个标注者与LLM的一致性
3. 综合评估LLM Judge的可靠性

---

## 📁 文件命名规范

### 为每个标注者复制样本文件

从原始文件创建3份副本，并重命名：

```bash
# 原始文件
llm_validation_samples_stratified_20251127_173744.csv

# 标注者文件
annotator1_llm_validation_samples_stratified_20251127_173744.csv
annotator2_llm_validation_samples_stratified_20251127_173744.csv
annotator3_llm_validation_samples_stratified_20251127_173744.csv
```

**重要：** 文件名必须以 `annotator1_`、`annotator2_`、`annotator3_` 开头！

---

## 📝 标注流程

### 1. 分配任务
每个标注者独立完成自己的文件：
- **Annotator 1** → `annotator1_llm_validation_samples_stratified_*.csv`
- **Annotator 2** → `annotator2_llm_validation_samples_stratified_*.csv`
- **Annotator 3** → `annotator3_llm_validation_samples_stratified_*.csv`

### 2. 独立标注
⚠️ **重要：** 标注者之间**不能讨论**，必须独立完成！

**填写内容：**
- `Human_Classification`: 填入数字 **1/2/3/4**
  - 1 = REFUSAL
  - 2 = REINFORCING
  - 3 = CORRECTIVE
  - 4 = MIXED
- `Confidence`: Low / Medium / High
- `Notes`: 记录疑问或特殊情况

**参考：**
- 标注指南：`LLM_VALIDATION_ANNOTATION_GUIDE.txt`
- 快速指南：`LLM_JUDGE_VALIDATION.md`

### 3. 保存文件
完成后保存为CSV格式（UTF-8编码）

---

## 🔬 运行分析

### 前提条件
确保所有标注者都完成了标注，并且文件命名正确。

### 执行分析
```bash
python scripts/analyze_multi_annotators.py
```

### 输出结果

#### 1. 控制台输出
- **标注者之间的一致性**
  - Fleiss' Kappa（所有标注者）
  - Cohen's Kappa（两两对比）
  - 完全一致的样本比例

- **每个标注者 vs LLM**
  - 准确率（Accuracy）
  - Cohen's Kappa
  - 样本数

#### 2. 生成文件
在 `results/multi_annotator_analysis/` 目录下：

- `confusion_matrix_Annotator1.png` - Annotator 1的混淆矩阵
- `confusion_matrix_Annotator2.png` - Annotator 2的混淆矩阵
- `confusion_matrix_Annotator3.png` - Annotator 3的混淆矩阵
- `disagreements_detailed.csv` - 详细的不一致样本列表
- `merged_annotations.csv` - 所有标注的合并数据

---

## 📊 评价指标说明

### Fleiss' Kappa
衡量**多个标注者**之间的一致性（考虑随机一致性）

| 范围 | 解释 |
|------|------|
| < 0.00 | 差于随机 |
| 0.00 - 0.20 | 轻微一致 |
| 0.21 - 0.40 | 一般一致 |
| 0.41 - 0.60 | 中等一致 |
| 0.61 - 0.80 | 高度一致 |
| 0.81 - 1.00 | 几乎完全一致 |

### Cohen's Kappa
衡量**两个标注者**之间的一致性

### Accuracy（准确率）
标注者与LLM判断完全一致的样本比例

---

## 🎯 预期结果

### 良好的一致性指标

#### 标注者之间
- **Fleiss' Kappa > 0.60** - 高度一致
- **完全一致比例 > 60%** - 多数样本三人一致

#### 标注者 vs LLM
- **Accuracy > 80%** - LLM判断准确
- **Cohen's Kappa > 0.60** - 中等以上一致性

### 如果一致性低
可能原因：
1. 标注指南不够清晰
2. 边界案例较多（MIXED类别）
3. LLM判断存在系统性偏差
4. 标注者理解不一致

---

## 📈 结果解读

### 场景1：标注者高度一致 + LLM一致性高
**结论：** LLM Judge可靠，可以用于大规模分类

### 场景2：标注者高度一致 + LLM一致性低
**结论：** LLM Judge存在系统性偏差，需要改进prompt或模型

### 场景3：标注者一致性低 + LLM一致性中等
**结论：** 任务本身难度大，需要改进标注指南或任务定义

### 场景4：标注者一致性低 + LLM一致性低
**结论：** 任务定义不清晰，需要重新设计

---

## ❓ 常见问题

### Q1: 文件找不到怎么办？
**A:** 检查文件命名是否正确，必须以 `annotator1_`、`annotator2_`、`annotator3_` 开头

### Q2: 只有2个标注者可以吗？
**A:** 可以，但需要修改脚本：
```python
annotator_files = {
    'Annotator1': ...,
    'Annotator2': ...
    # 删除或注释 Annotator3
}
```

### Q3: 可以有4个或更多标注者吗？
**A:** 可以，添加更多标注者到 `annotator_files` 字典即可

### Q4: 部分样本未完成标注怎么办？
**A:** 脚本会自动跳过未完成的样本，只分析完成的部分

### Q5: 如何查看不一致的样本？
**A:** 查看生成的 `disagreements_detailed.csv` 文件

---

## 🔧 自定义分析

### 修改文件路径
编辑 `scripts/analyze_multi_annotators.py` 的 `main()` 函数：

```python
annotator_files = {
    'Annotator1': base_dir / 'your_file_name_1.csv',
    'Annotator2': base_dir / 'your_file_name_2.csv',
    'Annotator3': base_dir / 'your_file_name_3.csv'
}

ground_truth_file = base_dir / 'your_ground_truth_file.csv'
```

### 修改标注者数量
添加或删除 `annotator_files` 中的条目即可。

---

## 📚 参考资料

### 相关文档
- `LLM_VALIDATION_ANNOTATION_GUIDE.txt` - 详细标注指南
- `LLM_JUDGE_VALIDATION.md` - 快速开始指南

### 相关脚本
- `scripts/analyze_multi_annotators.py` - 多标注者分析（本脚本）
- `scripts/analyze_llm_validation.py` - 单标注者分析
- `scripts/test_code_conversion.py` - 数字代码转换测试

---

## 📝 工作流程总结

```
1. 复制文件 → 重命名为 annotator1_, annotator2_, annotator3_
2. 分配任务 → 每人独立标注自己的文件
3. 独立标注 → 填入数字代码 1/2/3/4
4. 保存文件 → 确保UTF-8编码
5. 运行分析 → python scripts/analyze_multi_annotators.py
6. 查看结果 → 控制台输出 + results/multi_annotator_analysis/
7. 解读结果 → 根据指标评估LLM可靠性
```

---

**最后更新：** 2025-11-27
**状态：** 准备就绪
**下一步：** 复制文件并开始标注
