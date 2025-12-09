# LLM Judge 可视化工具使用指南

## 概述

`src/analysis/visualization.py` 提供了一套用于分析和可视化LLM Judge分类结果的工具函数。

## 快速开始

### 在Notebook中使用

```python
from src.analysis.visualization import (
    ALL_CLASSIFICATIONS,
    COLOR_MAP,
    prepare_analysis_data,
    aggregate_traits_by_classification,
    plot_classification_distribution,
    plot_model_comparison
)

# 1. 准备数据
df_analysis = prepare_analysis_data(df_final)

# 2. 绘制单个图表
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(12, 6))
data = pd.crosstab(df_analysis['Severity'], df_analysis['Judge_Classification'])
plot_classification_distribution(
    data, ax,
    title='Classification by Severity',
    xlabel='Severity',
    ylabel='Count'
)
plt.show()

# 3. 绘制模型比较图
fig, axes = plot_model_comparison(
    df_analysis,
    models=['gpt-4o', 'gpt-4o-mini'],
    comparison_type='trait',
    use_percentage=True
)
plt.show()
```

## 核心函数

### 1. `prepare_analysis_data(df_final)`

准备用于分析的数据，过滤成功分类的样本并转换Severity为有序分类。

**参数**:
- `df_final`: 完整的结果DataFrame

**返回**:
- `DataFrame`: 清洗后的分析数据

---

### 2. `aggregate_traits_by_classification(df, use_percentage=True)`

聚合Mixed traits到三个主要特质（Machiavellianism, Narcissism, Psychopathy）。

**参数**:
- `df`: 输入DataFrame
- `use_percentage`: 是否返回百分比（默认True）

**返回**:
- 如果 `use_percentage=True`: `(DataFrame, dict)` - 数据和样本总数
- 如果 `use_percentage=False`: `DataFrame` - 原始count数据

**示例**:
```python
# 获取百分比
data_pct, totals = aggregate_traits_by_classification(df_analysis, use_percentage=True)
print(data_pct)
#                       CORRECTIVE  MIXED  REINFORCING  ...
# Machiavellianism          85.2    5.1          8.7  ...
# Narcissism                90.3    3.2          5.5  ...
# Psychopathy               82.1    7.8          9.1  ...

# 获取count
data_count = aggregate_traits_by_classification(df_analysis, use_percentage=False)
```

---

### 3. `plot_classification_distribution(data, ax, title, xlabel, ylabel, x_rotation=0, color_map=None)`

统一的分类分布绘图函数。

**参数**:
- `data`: DataFrame，用于绘图的数据
- `ax`: matplotlib axes对象
- `title`: 图表标题
- `xlabel`: X轴标签
- `ylabel`: Y轴标签
- `x_rotation`: X轴标签旋转角度（0或45）
- `color_map`: 可选的颜色映射dict

**示例**:
```python
fig, ax = plt.subplots(figsize=(12, 6))
data = pd.crosstab(df['Model'], df['Judge_Classification'])
plot_classification_distribution(
    data, ax,
    title='Classification by Model',
    xlabel='Model',
    ylabel='Count',
    x_rotation=45
)
plt.show()
```

---

### 4. `plot_model_comparison(df_analysis, models, comparison_type='severity', use_percentage=False, figsize=(20, 5))`

绘制模型间比较图（Severity或Trait）。

**参数**:
- `df_analysis`: 分析数据DataFrame
- `models`: 模型名称列表
- `comparison_type`: `'severity'` 或 `'trait'`
- `use_percentage`: 是否使用百分比（仅对trait有效）
- `figsize`: 图表尺寸

**返回**:
- `(fig, axes)`: matplotlib对象

**示例**:
```python
# Severity比较
fig, axes = plot_model_comparison(
    df_analysis,
    models=['gpt-4o', 'gpt-4o-mini', 'claude-sonnet-4'],
    comparison_type='severity'
)

# Trait比较（百分比）
fig, axes = plot_model_comparison(
    df_analysis,
    models=['gpt-4o', 'gpt-4o-mini'],
    comparison_type='trait',
    use_percentage=True
)
```

## 配置常量

### `ALL_CLASSIFICATIONS`
所有分类类别的列表：
```python
['CORRECTIVE', 'MIXED', 'REINFORCING', 'REFUSAL', 'ERROR']
```

### `COLOR_MAP`
分类到颜色的映射：
```python
{
    'CORRECTIVE': '#2ecc71',   # 绿色
    'MIXED': '#3498db',        # 蓝色
    'REINFORCING': '#e74c3c',  # 红色
    'REFUSAL': '#f39c12',      # 橙色
    'ERROR': '#95a5a6'         # 灰色
}
```

## 自定义颜色方案

如果需要自定义颜色：

```python
from src.analysis.visualization import plot_classification_distribution

# 自定义颜色映射
custom_colors = {
    'CORRECTIVE': '#00ff00',
    'MIXED': '#0000ff',
    # ...
}

plot_classification_distribution(
    data, ax, title, xlabel, ylabel,
    color_map=custom_colors
)
```

## 注意事项

1. **数据格式**: 输入DataFrame必须包含以下列：
   - `Judge_Classification`
   - `Primary_Trait`
   - `Model`
   - `Severity`

2. **Mixed Traits处理**:
   - `Mixed (M+N)` 会同时计入 Machiavellianism 和 Narcissism
   - 百分比是相对于每个trait的总样本数计算的

3. **颜色一致性**: 所有图表使用统一的颜色映射，确保跨图表可比性

## 扩展功能

如需添加新的可视化功能，可以在 `visualization.py` 中添加新函数，并遵循以下原则：

1. 使用 `ALL_CLASSIFICATIONS` 确保分类顺序一致
2. 使用 `COLOR_MAP` 确保颜色一致
3. 提供清晰的docstring文档
4. 在 `__all__` 中导出新函数
