# 🚀 快速开始指南

## 为明天会议准备实验结果

本指南将帮助你在**今晚**完成一次完整的 LLM 实验，为明天的教授会议准备材料。

---

## ⏱️ 时间安排

- **环境配置**: 10分钟
- **运行实验**: 2-3小时 (自动化，可以挂机)
- **分析结果**: 5分钟
- **生成图表**: 5分钟

**总计**: ~3小时 (大部分时间可以做其他事情)

---

## 📋 第一步: 环境配置 (10分钟)

### 1.1 安装 Python 依赖

```bash
cd "d:\masterthesis\experiment\新建文件夹"
pip install -r requirements.txt
```

如果遇到安装问题,可以逐个安装:
```bash
pip install pandas openai anthropic matplotlib seaborn python-dotenv
```

### 1.2 配置 API Keys

**复制配置模板:**
```bash
copy .env.example .env
```

**编辑 .env 文件**, 填入你的 API keys:
```
OPENAI_API_KEY=sk-your-actual-openai-key-here
ANTHROPIC_API_KEY=sk-ant-your-actual-anthropic-key-here
```

**获取 API Keys:**
- OpenAI: https://platform.openai.com/api-keys
- Anthropic: https://console.anthropic.com/settings/keys

### 1.3 验证配置

```bash
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('OpenAI:', 'OK' if os.getenv('OPENAI_API_KEY') else 'Missing'); print('Anthropic:', 'OK' if os.getenv('ANTHROPIC_API_KEY') else 'Missing')"
```

应该看到:
```
OpenAI: OK
Anthropic: OK
```

---

## 🧪 第二步: 运行实验 (2-3小时)

### 2.1 选择测试模式

有3种模式可选:

**模式1: 测试模式** (推荐用于验证环境)
- 只测试 5 个 prompts
- 时间: 5-10 分钟
- 成本: ~$0.10
- 用途: 验证代码能正常运行

**模式2: 快速实验** (推荐明天会议用)
- 测试 GPT-3.5-Turbo (126 prompts)
- 时间: 30-45 分钟
- 成本: ~$1-2
- 用途: 快速获得初步结果

**模式3: 标准实验** (推荐用于论文)
- 测试 GPT-4 + Claude 3.5 Sonnet (252 prompts)
- 时间: 2-3 小时
- 成本: ~$15-20
- 用途: 完整的实验数据

### 2.2 运行实验

```bash
python run_quick_experiment.py
```

按照提示选择模式。

**建议流程:**
1. 先运行**测试模式**(选项5) 验证环境 → 5分钟
2. 确认无误后，运行**标准实验**(选项2) → 挂机2-3小时

### 2.3 实验过程中

- ✅ 可以关闭窗口，实验会继续运行
- ✅ 结果每10个prompt自动保存
- ✅ 如果中断，可以从断点继续
- ✅ 所有结果保存在 `results/` 目录

---

## 📊 第三步: 分析结果 (5分钟)

实验完成后，运行分析:

```bash
python analyze_results.py
```

这会:
- ✅ 自动分类每个响应 (CORRECTIVE/REINFORCING/NEUTRAL)
- ✅ 计算统计数据 (按模型、严重程度、特质)
- ✅ 生成汇总报告 (JSON格式)
- ✅ 保存分析后的结果 (*_analyzed.csv)

**输出文件:**
- `results/results_*_analyzed.csv` - 带分析列的详细结果
- `results/analysis_report_*.json` - 统计摘要

---

## 📈 第四步: 生成图表 (5分钟)

生成论文级别的图表:

```bash
python visualize_results.py
```

这会在 `figures/` 目录生成 4 个图表:
1. **fig1_classification_distribution.png** - 响应分类分布
2. **fig2_severity_analysis.png** - 严重程度影响
3. **fig3_trait_comparison.png** - 特质比较
4. **fig4_response_length.png** - 响应长度分布

所有图表都是 **300 DPI**，可以直接用于:
- ✅ 论文插图
- ✅ PPT展示
- ✅ 会议海报

---

## 💼 第五步: 准备会议材料

### 5.1 查看结果摘要

打开 `results/analysis_report_*.json`，你会看到:

```json
{
  "summaries": [
    {
      "model": "gpt-4",
      "total_responses": 126,
      "classification_percentages": {
        "CORRECTIVE": 45.2,
        "REINFORCING": 28.6,
        "MIXED": 18.3,
        "NEUTRAL": 7.9
      },
      "by_severity": {
        "LOW": {"corrective_pct": 23.8, "reinforcing_pct": 42.9},
        "MEDIUM": {"corrective_pct": 45.2, "reinforcing_pct": 28.6},
        "HIGH": {"corrective_pct": 66.7, "reinforcing_pct": 14.3}
      }
    }
  ]
}
```

### 5.2 关键发现总结

基于你的结果，准备以下讨论点:

1. **整体趋势**
   - GPT-4 给出了 X% 的 corrective 响应
   - Claude 给出了 Y% 的 corrective 响应

2. **严重程度效应**
   - LOW severity: 更多 reinforcing 响应
   - HIGH severity: 更多 corrective 响应
   - 说明模型对严重程度敏感

3. **特质差异**
   - Psychopathy prompts 触发更多 corrective
   - Narcissism prompts 触发更多 reinforcing
   - (根据你的实际数据调整)

4. **模型比较**
   - GPT-4 vs Claude 的差异
   - 哪个模型更"保守"?
   - 哪个模型更"迎合"?

### 5.3 准备 PPT/文档

**会议大纲建议:**

**Slide 1: 研究问题**
- LLMs 如何响应负面行为模式?
- 是提供道德指导还是迎合用户?

**Slide 2: 数据集**
- 126 prompts, 42 scenarios
- Dark Triad 框架 (Machiavellianism, Narcissism, Psychopathy)
- 3 severity levels (LOW, MEDIUM, HIGH)
- 5 contexts (Workplace, Friendship, Romantic, Society, Family)

**Slide 3: 方法**
- 测试了 X 个模型
- 126 prompts × X models = Y total responses
- 自动分类: CORRECTIVE vs REINFORCING

**Slide 4: 主要发现**
- 插入 fig1_classification_distribution.png
- 模型表现差异

**Slide 5: 严重程度效应**
- 插入 fig2_severity_analysis.png
- 讨论趋势

**Slide 6: 特质效应**
- 插入 fig3_trait_comparison.png
- 哪些特质触发更多 corrective?

**Slide 7: 下一步**
- 增加更多模型?
- 深入分析特定场景?
- 定性分析有趣案例?

---

## 🔍 查看具体案例

如果教授想看具体例子:

```bash
# 在 Python 中查看
python
>>> import pandas as pd
>>> df = pd.read_csv('results/results_gpt-4_*_analyzed.csv')

# 查看 REINFORCING 响应的例子
>>> df[df['Response_Classification'] == 'REINFORCING'][['ID', 'User Prompt', 'LLM Response']].head()

# 查看 HIGH severity 的 CORRECTIVE 响应
>>> df[(df['Severity'] == 'HIGH') & (df['Response_Classification'] == 'CORRECTIVE')][['ID', 'User Prompt', 'LLM Response']].head()
```

---

## ⚠️ 常见问题

### Q1: 实验中断了怎么办?
**A:** 重新运行 `python run_quick_experiment.py`，选择相同的模型。如果之前的结果已保存，可以手动删除 `results/` 中的文件重新开始。

### Q2: API key 无效
**A:**
1. 检查 `.env` 文件中的 key 是否正确复制
2. 确保 key 前后没有空格或引号
3. 验证 API key 在对应平台上是否激活

### Q3: 成本太高怎么办?
**A:**
1. 使用**测试模式**(只测5个prompts)
2. 只测试 GPT-3.5 (便宜10倍)
3. 先测试一部分 prompts:
   ```python
   # 修改 run_quick_experiment.py
   # 在 batch_test_models 调用前添加:
   import pandas as pd
   df = pd.read_csv(dataset_path)
   df.head(20).to_csv('temp_dataset.csv', index=False)
   dataset_path = 'temp_dataset.csv'
   ```

### Q4: 图表显示有问题
**A:**
1. 确保已运行 `analyze_results.py`
2. 检查 `results/` 中是否有 `*_analyzed.csv` 文件
3. 如果中文显示乱码，不影响使用(图表标签都是英文)

### Q5: 想要修改分类标准
**A:** 编辑 `analyze_results.py`，修改 `CORRECTIVE_KEYWORDS` 和 `REINFORCING_KEYWORDS` 列表，然后重新运行分析。

---

## 📞 紧急联系

如果遇到问题:
1. 检查本文档的"常见问题"部分
2. 查看错误消息，通常会指出问题所在
3. 检查 `results/` 目录是否有部分结果文件

---

## ✅ 检查清单

**会议前确保:**
- [ ] 至少完成 1 个模型的完整测试 (126 prompts)
- [ ] 运行了分析脚本
- [ ] 生成了至少 3 个图表
- [ ] 查看了汇总报告 (JSON)
- [ ] 准备了 2-3 个具体案例
- [ ] 理解了主要发现
- [ ] 准备了下一步研究方向的想法

---

## 🎯 预期输出

成功完成后，你应该有:

```
新建文件夹/
├── results/
│   ├── results_gpt-4_*.csv               (原始结果)
│   ├── results_gpt-4_*_analyzed.csv      (分析后结果)
│   ├── results_claude-*_analyzed.csv     (如果测试了Claude)
│   └── analysis_report_*.json            (汇总报告)
├── figures/
│   ├── fig1_classification_distribution.png
│   ├── fig2_severity_analysis.png
│   ├── fig3_trait_comparison.png
│   └── fig4_response_length.png
└── ...
```

**祝会议顺利! 加油! 🎓📊**
