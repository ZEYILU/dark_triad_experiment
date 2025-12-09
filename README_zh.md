# Dark Triad LLM Experiment (v2.0)

面向对象的模块化LLM实验框架，用于测试 LLM 对 Dark Triad 行为模式的响应。

> **🆕 v2.0 重构版本** - 现在使用模块化架构！[查看重构说明](REFACTORING_NOTES.md)

## 🚀 快速开始 (3步)

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置 API Keys
copy .env.example .env
# 编辑 .env 填入你的 API keys

# 3. 运行实验（新版本）
python scripts/run_experiment.py

# 或使用旧版本
python legacy/run_quick_experiment.py
```

## 📁 项目结构 (v2.0)

```
dark_triad_experiment/
├── 🎯 核心模块 (src/)
│   ├── config.py                 # 配置管理
│   ├── llm/                      # LLM客户端（面向对象）
│   │   ├── base.py              # 抽象基类
│   │   ├── openai_client.py     # OpenAI实现
│   │   └── anthropic_client.py  # Anthropic实现
│   ├── analysis/                 # 分析模块
│   │   └── classifier.py        # 响应分类器
│   ├── data/                     # 数据处理
│   │   └── loader.py            # 数据加载器
│   └── utils/                    # 工具集
│       └── logger.py            # 日志系统
│
├── 🚀 可执行脚本 (scripts/)
│   ├── run_experiment.py        # 主实验脚本 ⭐ 从这里开始
│   └── analyze.py               # 结果分析
│
├── ⚙️ 配置文件 (configs/)
│   ├── models.yaml              # 模型配置
│   └── keywords.yaml            # 分类关键词
│
├── 📊 数据与结果
│   ├── data/                     # 数据集
│   ├── results/                  # 实验结果
│   └── figures/                  # 可视化图表
│
├── 📖 文档 (docs/)
│   ├── QUICK_START.md            # 快速开始指南
│   ├── INSTALLATION.md           # 安装说明
│   ├── PROJECT_SUMMARY.md        # 项目总结
│   └── dataset/                  # 数据集文档
│
├── 📦 旧版本 (legacy/)
│   ├── test_llm.py              # v1.0旧脚本（归档）
│   ├── analyze_results.py       # v1.0旧脚本（归档）
│   └── ...                      # 其他旧脚本
│
└── ⚙️ 项目配置
    ├── setup.py                  # 安装配置
    ├── requirements.txt          # Python依赖
    ├── README.md                 # 本文档
    └── .env                      # API密钥配置
```

## 📊 数据集

- **126 prompts** 基于 Dark Triad 框架
- **42 scenarios** × **3 severity levels** (LOW/MEDIUM/HIGH)
- **5 contexts**: Workplace, Friendship, Romantic, Society, Family
- 位置: `data/Dark_Triad_Dataset_FINAL.csv`

## 🎯 工作流程

```
验证环境 → 运行实验 → 分析结果 → 生成图表
  (1分钟)   (2-3小时)    (5分钟)     (5分钟)
```

## 📖 详细文档

- **立即开始**: [QUICK_START.md](QUICK_START.md) - 完整使用指南
- **安装帮助**: [INSTALLATION.md](INSTALLATION.md) - 环境配置
- **项目总结**: [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - 功能说明

## 🔧 实验模式

| 模式 | 时间 | 成本 | 用途 |
|------|------|------|------|
| 测试 | 5分钟 | $0.10 | 验证环境 |
| 快速 | 30分钟 | $1-2 | 初步结果 |
| 标准 | 2-3小时 | $15-20 | 会议展示 |
| 完整 | 3-4小时 | $18-25 | 论文数据 |

## ✅ 输出结果

运行完成后你将获得:

- ✅ **实验数据**: `results/results_MODEL_*.csv`
- ✅ **分析结果**: `results/*_analyzed.csv`
- ✅ **统计报告**: `results/analysis_report_*.json`
- ✅ **图表**: `figures/fig1-4_*.png` (300 DPI)

## 💡 支持的模型

- OpenAI: GPT-4, GPT-3.5-Turbo
- Anthropic: Claude 3.5 Sonnet, Claude 3 Opus
- 可扩展到其他 LLM

## 🆘 需要帮助?

1. **环境问题**: 运行 `python verify_setup.py`
2. **使用问题**: 查看 [QUICK_START.md](QUICK_START.md)
3. **安装问题**: 查看 [INSTALLATION.md](INSTALLATION.md)

---

**用途**: ACL 2026 Submission - Dark Triad LLM Research
**状态**: ✅ 就绪
**版本**: v1.0
