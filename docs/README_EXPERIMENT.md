# Dark Triad LLM Experiment - 快速实验框架

## 📦 项目概述

这是一个用于测试 LLM 对 Dark Triad 行为模式响应的完整实验框架。

**核心功能:**
- ✅ 支持多个 LLM (GPT-4, GPT-3.5, Claude)
- ✅ 自动化批量测试
- ✅ 智能响应分类 (CORRECTIVE/REINFORCING/NEUTRAL)
- ✅ 生成论文级别的可视化图表
- ✅ 断点续传和错误恢复

---

## 🚀 快速开始 (3步完成)

### 第1步: 安装依赖
```bash
pip install -r requirements.txt
```

### 第2步: 配置 API Keys
```bash
copy .env.example .env
# 编辑 .env 填入你的 API keys
```

### 第3步: 运行实验
```bash
python run_quick_experiment.py
```

**详细说明:** 请查看 [QUICK_START.md](QUICK_START.md)

---

## 📁 文件说明

### 核心脚本

| 文件 | 用途 | 何时使用 |
|------|------|---------|
| **run_quick_experiment.py** | 一键运行实验 | 开始新实验 |
| **test_llm.py** | LLM 测试核心模块 | 自动调用 |
| **analyze_results.py** | 分析实验结果 | 实验完成后 |
| **visualize_results.py** | 生成图表 | 分析完成后 |

### 配置文件

| 文件 | 用途 |
|------|------|
| **requirements.txt** | Python 依赖列表 |
| **.env.example** | API Key 配置模板 |
| **.env** | 实际配置 (需自己创建) |
| **config_example.py** | 高级配置示例 |

### 数据文件

| 文件 | 说明 |
|------|------|
| **Dark_Triad_Dataset_FINAL.csv** | 主数据集 (126 prompts) |
| **scenario_mapping_table.csv** | 场景映射表 |
| **trait_breakdown_report.csv** | 特质分布统计 |

### 文档

| 文件 | 内容 |
|------|------|
| **QUICK_START.md** | 快速开始指南 ⭐ |
| **README_EXPERIMENT.md** | 本文件 |
| **使用说明.md** | 中文使用说明 |
| **Quick_Start_Guide.md** | 数据集使用指南 |

---

## 📊 工作流程

```
1. 准备
   └─> pip install -r requirements.txt
   └─> 配置 .env

2. 运行实验
   └─> python run_quick_experiment.py
   └─> 选择模型和测试模式
   └─> 等待 2-3 小时 (可挂机)

3. 分析结果
   └─> python analyze_results.py
   └─> 生成分类和统计

4. 生成图表
   └─> python visualize_results.py
   └─> 导出论文图表

5. 查看结果
   └─> results/*_analyzed.csv
   └─> results/analysis_report_*.json
   └─> figures/*.png
```

---

## 🎯 实验模式

### 模式 1: 测试模式 (5分钟, $0.10)
- 只测试 5 个 prompts
- 用于验证环境配置
- **命令:** 运行 run_quick_experiment.py → 选项 5

### 模式 2: 快速实验 (30分钟, $1-2)
- GPT-3.5-Turbo × 126 prompts
- 获得初步结果
- **命令:** 运行 run_quick_experiment.py → 选项 1

### 模式 3: 标准实验 (2-3小时, $15-20)
- GPT-4 + Claude 3.5 × 126 prompts
- 完整的对比实验
- **命令:** 运行 run_quick_experiment.py → 选项 2

### 模式 4: 完整实验 (3-4小时, $18-25)
- GPT-4 + GPT-3.5 + Claude × 126 prompts
- 最全面的数据
- **命令:** 运行 run_quick_experiment.py → 选项 3

---

## 📈 输出结果

### results/ 目录
- **results_MODEL_TIMESTAMP.csv** - 原始结果
- **results_MODEL_TIMESTAMP.json** - JSON 格式
- **results_MODEL_TIMESTAMP_analyzed.csv** - 分析后结果
- **analysis_report_TIMESTAMP.json** - 汇总报告

### figures/ 目录
- **fig1_classification_distribution.png** - 响应分类分布
- **fig2_severity_analysis.png** - 严重程度影响
- **fig3_trait_comparison.png** - 特质比较
- **fig4_response_length.png** - 响应长度分布

所有图表为 **300 DPI PNG**，可直接用于论文。

---

## 🔧 高级用法

### 只测试特定子集

```python
# 编辑 run_quick_experiment.py，在 batch_test_models 调用前添加:
import pandas as pd
df = pd.read_csv(dataset_path)

# 只测试 HIGH severity
df_high = df[df['Severity'] == 'HIGH']
df_high.to_csv('temp_dataset.csv', index=False)
dataset_path = 'temp_dataset.csv'
```

### 添加新的 LLM

编辑 `test_llm.py`，参考 `test_openai` 和 `test_anthropic` 方法添加新的 API 调用。

### 自定义分类关键词

编辑 `analyze_results.py`，修改 `ResponseAnalyzer` 类中的:
- `CORRECTIVE_KEYWORDS`
- `REINFORCING_KEYWORDS`
- `NEUTRAL_KEYWORDS`

---

## 📊 数据集信息

- **总 prompts:** 126
- **场景数:** 42
- **严重程度:** LOW (42), MEDIUM (42), HIGH (42)
- **特质:**
  - Machiavellianism: 21 prompts
  - Narcissism: 18 prompts
  - Psychopathy: 48 prompts
  - Mixed: 39 prompts
- **场景:**
  - Workplace
  - Personal-Friendship
  - Personal-Romantic
  - Public-Society
  - Personal-Family

---

## ⚠️ 注意事项

1. **API 成本**
   - 完整实验 (3个模型) ≈ $20-25
   - 建议先用测试模式验证

2. **时间投入**
   - 2-3 小时运行时间 (可挂机)
   - 大部分时间在等待 API 响应

3. **数据安全**
   - `.env` 文件包含 API keys，不要上传到 Git
   - 建议在 `.gitignore` 中添加 `.env`

4. **错误处理**
   - 如遇 API 限流，脚本会自动延迟重试
   - 结果每10个 prompt 自动保存

---

## 🐛 常见问题

### ImportError: No module named 'XXX'
```bash
pip install XXX
# 或重新安装所有依赖
pip install -r requirements.txt
```

### API Key 错误
检查 `.env` 文件:
- 确保 key 正确无误
- 确保没有多余的空格或引号
- 格式: `OPENAI_API_KEY=sk-...`

### Rate limit exceeded
- 脚本已内置 1 秒延迟
- 如仍报错，检查 API quota
- 可以暂停后继续

### 中文显示乱码
- 使用 Excel 打开 CSV 时选择 UTF-8 编码
- 或使用 pandas 读取: `pd.read_csv(file, encoding='utf-8-sig')`

---

## 📞 获取帮助

1. **查看文档**
   - [QUICK_START.md](QUICK_START.md) - 详细步骤
   - [使用说明.md](使用说明.md) - 中文说明

2. **检查代码**
   - 所有脚本都有详细注释
   - 错误消息通常会指出问题

3. **调试模式**
   - 使用测试模式 (5个 prompts) 快速验证
   - 查看 results/ 中的部分输出

---

## 🎓 用于论文

### Methods 部分
> "We tested X LLM models using a corpus of 126 prompts based on the Dark Triad framework, with 42 base scenarios each instantiated at three severity levels (LOW, MEDIUM, HIGH). Responses were automatically classified as CORRECTIVE, REINFORCING, MIXED, or NEUTRAL using keyword-based pattern matching."

### Results 部分
使用生成的图表和统计数据:
- Table 1: 从 `analysis_report_*.json` 提取
- Figure 1-4: 直接使用 `figures/` 中的 PNG

### 可重复性
所有代码、数据集和配置都已包含，确保研究可重复。

---

## ✅ 检查清单

**实验前:**
- [ ] 已安装所有依赖
- [ ] 已配置 API keys (.env 文件)
- [ ] 已验证配置 (测试模式)

**实验中:**
- [ ] 选择合适的测试模式
- [ ] 监控第一个模型的输出
- [ ] 确认结果正常保存

**实验后:**
- [ ] 运行 analyze_results.py
- [ ] 运行 visualize_results.py
- [ ] 查看生成的图表和报告
- [ ] 准备会议材料

---

## 📅 时间线

**今晚 (实验):**
- 环境配置: 10分钟
- 运行实验: 2-3小时
- 分析结果: 10分钟
- **总计: ~3小时**

**明天 (会议):**
- 展示图表和初步发现
- 讨论下一步方向
- 根据反馈调整实验

**未来 (论文):**
- 补充更多模型
- 深入分析特定案例
- 完善可视化
- 撰写论文

---

**祝实验顺利! Good luck! 🚀📊🎓**

---

**版本:** v1.0
**日期:** 2025-11-11
**用途:** ACL 2026 Submission Preparation
