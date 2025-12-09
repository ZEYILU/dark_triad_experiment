# 文件组织结构

## 📋 整理日期
2025-11-27

## ✅ 整理完成

项目文件已重新组织，现在结构清晰，易于导航。

---

## 📁 当前文件结构

### 根目录（主要文件）

```
dark_triad_experiment/
├── README.md                                ← 主实验项目说明
├── LLM_JUDGE_VALIDATION.md                  ← LLM Judge验证快速指南 ⭐ 从这里开始
├── LLM_VALIDATION_ANNOTATION_GUIDE.txt      ← 标注指南
│
├── llm_validation_samples_*.csv             ← 标注文件（55个样本）
├── llm_validation_samples_*_ground_truth.csv ← Ground Truth文件
│
└── requirements.txt                         ← Python依赖
```

### docs/ 目录（详细文档和历史文件）

```
docs/
├── llm_validation/                          ← LLM验证详细文档
│   ├── LLM_VALIDATION_README.md            ← 完整说明文档
│   ├── QUICK_START_LLM_VALIDATION.md       ← 详细快速指南
│   ├── STRATIFIED_SAMPLING_REPORT.md       ← 抽样策略报告
│   ├── SAMPLE_UPDATE_NOTES.md              ← 样本更新说明
│   └── ANNOTATION_GUIDE.txt                ← 旧标注指南（归档）
│
└── archive/                                 ← 历史文档
    ├── REFACTORING_NOTES.md                ← 重构笔记
    └── REFACTORING_SUMMARY.md              ← 重构总结
```

---

## 🎯 快速导航

### 你想做什么？

#### 1. 开始标注样本
👉 打开 **LLM_JUDGE_VALIDATION.md**

#### 2. 了解项目整体
👉 打开 **README.md**

#### 3. 查看详细说明
👉 查看 **docs/llm_validation/LLM_VALIDATION_README.md**

#### 4. 了解抽样策略
👉 查看 **docs/llm_validation/STRATIFIED_SAMPLING_REPORT.md**

---

## 🗑️ 已删除的文件

### 旧版本样本文件
- ❌ `llm_validation_samples_20251127_171325.csv`
- ❌ `llm_validation_samples_20251127_171325_ground_truth.csv`
- ❌ `llm_validation_samples_stratified_20251127_172645.csv`
- ❌ `llm_validation_samples_stratified_20251127_172645_ground_truth.csv`

**原因：** 包含空白响应或列太多，已被新版本替代

### 旧文档文件
- ❌ `CLEANUP_REPORT.md`
- ❌ `QUICK_START_GUIDE.md`

**原因：** 过时，内容已合并到新文档

---

## 📦 已归档的文件

### 移动到 docs/archive/
- 📦 `REFACTORING_NOTES.md` - 重构笔记
- 📦 `REFACTORING_SUMMARY.md` - 重构总结

### 移动到 docs/llm_validation/
- 📦 `ANNOTATION_GUIDE.txt` - 旧标注指南
- 📦 `LLM_VALIDATION_README.md` - 完整说明
- 📦 `QUICK_START_LLM_VALIDATION.md` - 详细快速指南
- 📦 `STRATIFIED_SAMPLING_REPORT.md` - 抽样报告
- 📦 `SAMPLE_UPDATE_NOTES.md` - 更新说明

---

## ✨ 整理效果

### 之前（22个文件） 😵
```
根目录：一堆md文档、txt文档、csv文件，杂乱无章
```

### 现在（10个主要文件） 😊
```
根目录：2个主文档 + 2个数据文件 + 1个标注指南
docs/：详细文档分类存放
```

---

## 📝 文件命名规则

### 标注文件
```
llm_validation_samples_stratified_YYYYMMDD_HHMMSS.csv
```

### Ground Truth文件
```
llm_validation_samples_stratified_YYYYMMDD_HHMMSS_ground_truth.csv
```

### 当前使用
```
llm_validation_samples_stratified_20251127_173744.csv          ← 标注用
llm_validation_samples_stratified_20251127_173744_ground_truth.csv  ← 分析用
```

---

## 🔍 查找文件指南

### 我想找标注指南
**位置：** 根目录 `LLM_VALIDATION_ANNOTATION_GUIDE.txt`

### 我想找抽样报告
**位置：** `docs/llm_validation/STRATIFIED_SAMPLING_REPORT.md`

### 我想找样本文件
**位置：** 根目录 `llm_validation_samples_stratified_*.csv`

### 我想找历史文档
**位置：** `docs/archive/`

---

## 🎯 推荐阅读顺序

1. **开始标注** → `LLM_JUDGE_VALIDATION.md` (3分钟)
2. **标注指南** → `LLM_VALIDATION_ANNOTATION_GUIDE.txt` (10分钟)
3. **详细说明** → `docs/llm_validation/LLM_VALIDATION_README.md` (可选)
4. **抽样策略** → `docs/llm_validation/STRATIFIED_SAMPLING_REPORT.md` (可选)

---

## 📊 统计

- **删除文件：** 6个
- **归档文件：** 7个
- **新建文件：** 2个（LLM_JUDGE_VALIDATION.md, FILE_ORGANIZATION.md）
- **保留文件：** 10个（根目录）

---

**整理完成！** 🎉

现在你可以轻松找到需要的文件。
