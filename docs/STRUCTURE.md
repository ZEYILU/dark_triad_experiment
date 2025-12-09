# 📁 项目文件结构说明

## 整理后的目录结构

```
dark_triad_experiment/              # 主项目目录 (原"新建文件夹")
│
├── 🔬 核心实验脚本 (4个 - 常用)
│   ├── run_quick_experiment.py     # ⭐ 一键运行实验 - 从这里开始!
│   ├── analyze_results.py          # 分析实验结果
│   ├── visualize_results.py        # 生成图表
│   ├── test_llm.py                 # LLM 测试核心模块
│   └── verify_setup.py             # 环境验证工具
│
├── ⚙️ 配置文件 (3个)
│   ├── requirements.txt            # Python 依赖列表
│   ├── .env.example               # API Key 配置模板
│   └── .env                       # 实际配置 (需自己创建)
│
├── 📖 主要文档 (4个 - 推荐阅读)
│   ├── README.md                  # 项目总览 (新创建，简洁版) ⭐
│   ├── QUICK_START.md             # 快速开始指南 (详细步骤)
│   ├── INSTALLATION.md            # 安装说明
│   ├── PROJECT_SUMMARY.md         # 项目完成总结
│   └── README_EXPERIMENT.md       # 实验框架说明 (详细版)
│
├── 📊 数据目录
│   └── data/                      # 所有数据集和统计文件
│       ├── Dark_Triad_Dataset_FINAL.csv      # ⭐ 主数据集 (126 prompts)
│       ├── scenario_mapping_table.csv        # 场景映射
│       ├── trait_breakdown_report.csv        # 特质统计
│       ├── dataset_summary_report.csv        # 数据摘要
│       ├── gap_report.csv                    # 补充记录
│       └── id_renumbering_map.csv            # ID映射
│
├── 📁 输出目录
│   ├── results/                   # 实验结果输出 (CSV, JSON)
│   └── figures/                   # 生成的图表 (PNG)
│
└── 📚 归档文档 (不常用)
    └── docs/
        ├── dataset/               # 数据集相关文档 (已整理)
        │   ├── Dataset_Cleaning_Report.md     # 数据清理报告
        │   ├── Quick_Start_Guide.md           # 数据集使用指南
        │   ├── README.md                      # 数据集说明
        │   └── 数据集清理说明_中文版.md        # 中文清理说明
        │
        └── archive/               # 旧版文档和配置 (备份)
            ├── 使用说明.md                      # 旧版使用说明
            ├── config_example.py               # 旧版配置示例
            ├── files.zip                       # 打包文件
            └── nul                             # 临时文件
```

---

## 📝 文件用途说明

### 🔬 核心脚本 (日常使用)

1. **run_quick_experiment.py** (5.5 KB)
   - **用途**: 一键运行完整实验
   - **功能**:
     - 交互式选择模型
     - 5种测试模式
     - 自动保存进度
   - **使用**: `python run_quick_experiment.py`

2. **analyze_results.py** (10 KB)
   - **用途**: 自动分析实验结果
   - **功能**:
     - 响应分类 (CORRECTIVE/REINFORCING/NEUTRAL)
     - 统计分析 (按模型/特质/严重程度)
     - 生成 JSON 报告
   - **使用**: `python analyze_results.py`

3. **visualize_results.py** (8 KB)
   - **用途**: 生成论文级别图表
   - **功能**:
     - 4 个图表 (300 DPI PNG)
     - 自动从分析结果读取
   - **使用**: `python visualize_results.py`

4. **test_llm.py** (12 KB)
   - **用途**: LLM 测试核心模块
   - **功能**:
     - API 封装 (OpenAI, Anthropic)
     - 批量测试
     - 结果保存
   - **使用**: 被其他脚本调用 (也可独立运行)

5. **verify_setup.py** (6 KB)
   - **用途**: 验证环境配置
   - **功能**:
     - 检查 Python 版本
     - 检查依赖库
     - 验证 API Keys
     - 检查数据集
   - **使用**: `python verify_setup.py`

---

### ⚙️ 配置文件

1. **requirements.txt** (354 bytes)
   - Python 依赖列表
   - 包含: pandas, openai, anthropic, matplotlib, seaborn, etc.

2. **.env.example** (544 bytes)
   - API Key 配置模板
   - 需要复制为 `.env` 并填入实际 keys

3. **.env** (需自己创建)
   - 实际的 API keys
   - ⚠️ 不要上传到 Git!

---

### 📖 文档文件

#### 主要文档 (推荐阅读)

1. **README.md** (新创建)
   - 简洁的项目总览
   - 快速开始指南
   - 文件结构说明

2. **QUICK_START.md** (8 KB)
   - 为明天会议准备的完整流程
   - 详细的 5 步指南
   - 常见问题解答

3. **INSTALLATION.md** (6 KB)
   - 详细安装步骤
   - 常见问题解决
   - 高级配置

4. **PROJECT_SUMMARY.md** (12 KB)
   - 项目完成总结
   - 所有创建的文件列表
   - 工作流程说明

5. **README_EXPERIMENT.md** (7 KB)
   - 实验框架详细说明
   - 高级用法
   - 论文写作建议

#### 归档文档 (不常用)

6. **docs/dataset/** - 数据集文档
   - 数据清理报告
   - 数据集使用指南
   - 中英文说明

7. **docs/archive/** - 旧版文档
   - 旧版使用说明
   - 旧版配置示例

---

### 📊 数据文件 (data/ 目录)

1. **Dark_Triad_Dataset_FINAL.csv** (60 KB)
   - ⭐ 主数据集
   - 126 prompts, 42 scenarios
   - 3 severity levels

2. **scenario_mapping_table.csv** (2.3 KB)
   - 场景完整性映射

3. **trait_breakdown_report.csv** (258 bytes)
   - 特质分布统计

4. **dataset_summary_report.csv** (102 bytes)
   - 数据集摘要

5. **gap_report.csv** (1.3 KB)
   - 补充 prompts 记录

6. **id_renumbering_map.csv** (387 bytes)
   - ID 重编号映射

---

## 🎯 推荐工作流程

### 初次使用

1. 阅读 `README.md` - 了解项目
2. 阅读 `INSTALLATION.md` - 配置环境
3. 运行 `verify_setup.py` - 验证配置
4. 阅读 `QUICK_START.md` - 了解详细步骤
5. 运行 `run_quick_experiment.py` - 开始实验

### 日常使用

1. `python run_quick_experiment.py` - 运行实验
2. `python analyze_results.py` - 分析结果
3. `python visualize_results.py` - 生成图表
4. 查看 `results/` 和 `figures/` - 获取输出

### 遇到问题

1. 运行 `verify_setup.py` - 诊断环境
2. 查看 `INSTALLATION.md` - 常见问题
3. 查看 `QUICK_START.md` - 使用帮助

---

## 📦 与原"新建文件夹"的对比

### 改进

✅ **重命名**: "新建文件夹" → "dark_triad_experiment" (更专业)
✅ **分类整理**: 数据、文档、归档分开存放
✅ **简化主目录**: 只保留常用文件
✅ **新增 README**: 简洁的项目说明
✅ **路径更新**: 所有脚本已更新数据集路径

### 保持不变

✅ 所有核心功能完全保留
✅ 所有数据文件完整保存
✅ 所有文档可访问
✅ 实验流程不受影响

---

## 🗂️ 文件大小统计

- **核心脚本**: ~40 KB (5个文件)
- **文档**: ~50 KB (9个文件)
- **数据集**: ~65 KB (6个文件)
- **配置**: ~1 KB (2个文件)
- **总计**: ~156 KB

---

## ✅ 整理完成!

现在的目录结构:
- ✅ 清晰明了
- ✅ 易于导航
- ✅ 专业规范
- ✅ 便于使用

**开始实验:**
```bash
cd dark_triad_experiment
python verify_setup.py
python run_quick_experiment.py
```

---

**创建时间**: 2025-11-11
**整理原因**: 优化项目结构，提高可用性
**状态**: ✅ 完成
