"""
LLM Judge结果可视化工具

提供用于分析和可视化LLM Judge分类结果的辅助函数。
"""

import pandas as pd
import matplotlib.pyplot as plt


# ==================== 配置常量 ====================

ALL_CLASSIFICATIONS = ['CORRECTIVE', 'MIXED', 'REINFORCING', 'REFUSAL', 'ERROR']
COLORS = ['#2ecc71', '#3498db', '#e74c3c', '#f39c12', '#95a5a6']  # Green, Blue, Red, Orange, Gray
COLOR_MAP = dict(zip(ALL_CLASSIFICATIONS, COLORS))


# ==================== 数据处理函数 ====================

def prepare_analysis_data(df_final):
    """
    准备用于分析的数据

    Args:
        df_final: 包含LLM Judge结果的完整DataFrame

    Returns:
        DataFrame: 清洗后的分析数据，包含有序的Severity列
    """
    # 只保留成功分类的数据
    df_analysis = df_final[df_final['Judge_Classification'].notna()].copy()

    # 将Severity转换为有序分类
    df_analysis['Severity'] = pd.Categorical(
        df_analysis['Severity'],
        categories=['HIGH', 'MEDIUM', 'LOW'],
        ordered=True
    )

    return df_analysis


def aggregate_traits_by_classification(df, use_percentage=True):
    """
    聚合Mixed traits到三个主要Dark Triad特质

    将包含多个特质的样本（如Mixed (M+N)）拆分并计入各自的主要特质。
    支持返回count或percentage。

    Args:
        df: 输入DataFrame，必须包含'Primary_Trait'和'Judge_Classification'列
        use_percentage: True返回百分比，False返回原始count

    Returns:
        如果use_percentage=True:
            tuple: (DataFrame, dict)
                - DataFrame: 按trait和classification的百分比统计
                - dict: 每个trait的总样本数
        如果use_percentage=False:
            DataFrame: 按trait和classification的count统计

    Example:
        >>> data, totals = aggregate_traits_by_classification(df, use_percentage=True)
        >>> print(data)
                              CORRECTIVE  MIXED  REINFORCING  ...
        Machiavellianism          85.2    5.1          8.7  ...
        Narcissism                90.3    3.2          5.5  ...
        Psychopathy               82.1    7.8          9.1  ...
    """
    main_traits = ['Machiavellianism', 'Narcissism', 'Psychopathy']

    # 计算每个trait的总样本数
    trait_totals = {}
    for trait in main_traits:
        count = sum(1 for _, row in df.iterrows()
                   if (trait == 'Machiavellianism' and 'M' in row['Primary_Trait']) or
                      (trait == 'Narcissism' and 'N' in row['Primary_Trait']) or
                      (trait == 'Psychopathy' and 'P' in row['Primary_Trait']))
        trait_totals[trait] = count

    # 统计每个classification在每个trait的数量
    data = []
    for classification in ALL_CLASSIFICATIONS:
        for trait in main_traits:
            # 计算满足条件的样本数
            count = sum(1 for _, row in df.iterrows()
                       if row['Judge_Classification'] == classification and (
                           (trait == 'Machiavellianism' and 'M' in row['Primary_Trait']) or
                           (trait == 'Narcissism' and 'N' in row['Primary_Trait']) or
                           (trait == 'Psychopathy' and 'P' in row['Primary_Trait'])))

            # 根据参数决定返回count还是percentage
            if use_percentage and trait_totals[trait] > 0:
                value = count / trait_totals[trait] * 100
            else:
                value = count

            data.append({
                'Trait': trait,
                'Classification': classification,
                'Value': value
            })

    # 转换为pivot table格式
    result = pd.DataFrame(data).pivot(
        index='Trait',
        columns='Classification',
        values='Value'
    ).fillna(0)

    # 确保所有classification都存在且顺序正确
    result = result.reindex(columns=ALL_CLASSIFICATIONS, fill_value=0)

    # 确保trait顺序正确
    result = result.reindex(['Machiavellianism', 'Narcissism', 'Psychopathy'])

    return (result, trait_totals) if use_percentage else result


# ==================== 可视化函数 ====================

def plot_classification_distribution(data, ax, title, xlabel, ylabel,
                                    x_rotation=0, color_map=None):
    """
    统一的分类分布绘图函数

    自动应用一致的颜色映射和样式。

    Args:
        data: DataFrame，用于绘图的数据（通常来自pd.crosstab或aggregate函数）
        ax: matplotlib axes对象
        title: 图表标题
        xlabel: X轴标签
        ylabel: Y轴标签
        x_rotation: X轴标签旋转角度（0或45）
        color_map: 可选的颜色映射dict，默认使用COLOR_MAP

    Example:
        >>> fig, ax = plt.subplots(figsize=(12, 6))
        >>> data = pd.crosstab(df['Severity'], df['Judge_Classification'])
        >>> plot_classification_distribution(
        ...     data, ax,
        ...     title='Classification by Severity',
        ...     xlabel='Severity',
        ...     ylabel='Count'
        ... )
        >>> plt.show()
    """
    if color_map is None:
        color_map = COLOR_MAP

    # 确保所有classification都存在
    if isinstance(data, pd.DataFrame):
        data = data.reindex(columns=ALL_CLASSIFICATIONS, fill_value=0)

    # 绘制柱状图
    data.plot(
        kind='bar',
        ax=ax,
        width=0.8,
        color=[color_map[col] for col in data.columns]
    )

    # 设置标题和标签
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend(title='Classification', bbox_to_anchor=(1.05, 1), loc='upper left')

    # 设置X轴标签旋转
    if x_rotation != 0:
        plt.setp(ax.get_xticklabels(), rotation=x_rotation, ha='right')
    else:
        ax.tick_params(axis='x', rotation=0)


def plot_model_comparison(df_analysis, models, comparison_type='severity',
                          use_percentage=False, figsize=(20, 5)):
    """
    绘制模型间比较图（Severity或Trait）

    Args:
        df_analysis: 分析数据DataFrame
        models: 模型名称列表
        comparison_type: 'severity'或'trait'
        use_percentage: 是否使用百分比（仅对trait有效）
        figsize: 图表尺寸

    Returns:
        tuple: (fig, axes) matplotlib对象

    Example:
        >>> fig, axes = plot_model_comparison(
        ...     df_analysis,
        ...     ['gpt-4o', 'gpt-4o-mini'],
        ...     comparison_type='trait',
        ...     use_percentage=True
        ... )
        >>> plt.show()
    """
    fig, axes = plt.subplots(1, len(models), figsize=figsize, sharey=True)

    # 确保axes是数组（即使只有1个模型）
    if len(models) == 1:
        axes = [axes]

    for idx, model in enumerate(models):
        df_model = df_analysis[df_analysis['Model'] == model]

        # 根据比较类型准备数据
        if comparison_type == 'severity':
            data = pd.crosstab(df_model['Severity'], df_model['Judge_Classification'])
            xlabel = 'Severity'
            ylabel = 'Count'
            x_rotation = 0
            title_suffix = 'Severity'
        elif comparison_type == 'trait':
            data, _ = aggregate_traits_by_classification(df_model, use_percentage=use_percentage)
            xlabel = 'Trait'
            ylabel = 'Percentage (%)' if use_percentage else 'Count'
            x_rotation = 45
            title_suffix = 'Trait'
        else:
            raise ValueError(f"comparison_type必须是'severity'或'trait'，得到: {comparison_type}")

        # 绘图
        plot_classification_distribution(
            data, axes[idx],
            title=f'{model}',
            xlabel=xlabel,
            ylabel=ylabel if idx == 0 else '',
            x_rotation=x_rotation
        )

        # 只在最后一个子图显示legend
        if idx < len(models) - 1:
            axes[idx].get_legend().remove()

    # 设置总标题
    pct_text = ' (%)' if comparison_type == 'trait' and use_percentage else ''
    fig.suptitle(f'Classification Distribution by {title_suffix.title()} - Model Comparison{pct_text}',
                 fontsize=16, fontweight='bold', y=1.02)

    return fig, axes


# ==================== 导出配置 ====================

__all__ = [
    'ALL_CLASSIFICATIONS',
    'COLOR_MAP',
    'prepare_analysis_data',
    'aggregate_traits_by_classification',
    'plot_classification_distribution',
    'plot_model_comparison',
]
