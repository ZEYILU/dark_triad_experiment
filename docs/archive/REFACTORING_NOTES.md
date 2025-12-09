# 代码重构说明

## 重构概述

本项目已从原始的平铺脚本结构重构为**面向对象的模块化架构**（v2.0），遵循软件工程最佳实践。

## 新的目录结构

```
dark_triad_experiment/
├── src/                          # 核心源代码包
│   ├── __init__.py
│   ├── config.py                 # 配置管理
│   ├── llm/                      # LLM客户端模块
│   │   ├── __init__.py
│   │   ├── base.py              # 抽象基类
│   │   ├── openai_client.py     # OpenAI实现
│   │   └── anthropic_client.py  # Anthropic实现
│   ├── analysis/                 # 分析模块
│   │   ├── __init__.py
│   │   └── classifier.py        # 响应分类器
│   ├── data/                     # 数据处理模块
│   │   ├── __init__.py
│   │   └── loader.py            # 数据加载器
│   └── utils/                    # 工具模块
│       ├── __init__.py
│       └── logger.py            # 日志系统
│
├── scripts/                      # 可执行脚本
│   ├── run_experiment.py        # 主实验脚本（重构）
│   └── analyze.py               # 分析脚本（重构）
│
├── configs/                      # YAML配置文件
│   ├── models.yaml              # 模型配置
│   └── keywords.yaml            # 分类关键词
│
├── data/                         # 数据文件
├── results/                      # 实验结果
├── figures/                      # 图表
├── tests/                        # 单元测试（待添加）
│
├── setup.py                      # 安装配置
├── requirements.txt              # 依赖列表
└── README.md                     # 项目说明

# 旧文件（已废弃）
├── test_llm.py                   # → src/llm/
├── analyze_results.py            # → scripts/analyze.py
├── run_quick_experiment.py       # → scripts/run_experiment.py
└── verify_setup.py               # 保留（独立工具）
```

## 主要改进

### 1. 面向对象设计

#### LLM客户端层次结构
```python
BaseLLMClient (抽象基类)
    ├── OpenAIClient
    └── AnthropicClient
```

**优势：**
- 统一接口：所有客户端实现相同的`call()`和`batch_call()`方法
- 易于扩展：添加新的LLM提供商只需继承`BaseLLMClient`
- 代码复用：限流、错误处理等通用逻辑在基类中实现

#### 示例使用
```python
from src.llm import OpenAIClient, AnthropicClient

# 创建客户端
client = OpenAIClient(model_name="gpt-4", api_key="...")

# 调用LLM
response = client.call("你的提示")

# 批量调用
responses = client.batch_call(["提示1", "提示2", "提示3"])
```

### 2. 配置管理

所有配置集中管理，支持多种配置源：

```python
from src.config import get_config

config = get_config()

# API密钥（从.env加载）
api_key = config.get_api_key("openai")

# 模型配置（从YAML加载）
models = config.get_models("openai")

# 分类关键词（从YAML加载）
keywords = config.get_keywords("refusal")

# 路径配置
dataset_path = config.get_path("dataset")
```

**优势：**
- 单一数据源：不再硬编码配置
- 易于修改：更新YAML文件即可，无需改代码
- 环境分离：开发、测试、生产使用不同配置

### 3. 日志系统

统一的日志记录，替代所有`print`语句：

```python
from src.utils.logger import get_logger

logger = get_logger("my_module")

logger.info("信息消息")    # ✅ INFO
logger.warning("警告")     # ⚠️ WARNING
logger.error("错误")       # ❌ ERROR
```

**优势：**
- 颜色和Emoji：更好的可读性
- 日志级别：INFO, WARNING, ERROR等
- 文件输出：可选保存到日志文件
- 时间戳：自动记录时间

### 4. 模块化分析

响应分类器作为独立模块：

```python
from src.analysis import ResponseClassifier

classifier = ResponseClassifier()

# 分类单个响应
result = classifier.classify("LLM的响应文本")
# result = {
#     "classification": "REFUSAL",
#     "corrective_score": 0.0,
#     "reinforcing_score": 0.0,
#     "confidence": "high",
#     ...
# }

# 批量分类
results = classifier.batch_classify([resp1, resp2, resp3])
```

**优势：**
- 关键词外部化：在YAML中配置，易于调整
- 可测试性：独立模块便于单元测试
- 可复用性：其他项目也可使用

### 5. 数据加载器

专门的数据加载类：

```python
from src.data import DatasetLoader

loader = DatasetLoader("data/Dark_Triad_Dataset_FINAL.csv")
loader.load()

# 获取prompts
prompts = loader.get_prompts()

# 获取元数据
metadata = loader.get_metadata(index=0)

# 统计信息
stats = loader.get_statistics()
```

## 使用方法

### 安装依赖

```bash
# 安装新增的依赖
pip install pyyaml

# 或重新安装所有依赖
pip install -r requirements.txt
```

### 运行实验（新方法）

```bash
# 使用重构后的脚本
python scripts/run_experiment.py

# 分析结果
python scripts/analyze.py
```

### 作为Python包安装（可选）

```bash
# 安装为可编辑模式
pip install -e .

# 然后可以从任何地方使用
dark-triad-run
dark-triad-analyze
```

## 配置文件说明

### configs/models.yaml

定义所有支持的模型及其参数：

```yaml
openai:
  - name: "gpt-4"
    temperature: 0.7
    max_tokens: 1000

anthropic:
  - name: "claude-3-haiku-20240307"
    temperature: 0.7
    max_tokens: 1000
```

### configs/keywords.yaml

分类关键词列表：

```yaml
refusal:
  - "i can't assist"
  - "i cannot help"
  ...

corrective:
  - "consider"
  - "suggest"
  ...
```

## 兼容性

### 旧脚本仍然可用

重构不影响旧脚本的运行：

- `test_llm.py` - 仍然可用
- `analyze_results.py` - 仍然可用
- `run_quick_experiment.py` - 仍然可用

### 数据格式兼容

- 输入数据集格式不变
- 输出结果格式不变（CSV和JSON）
- 分析结果格式不变

## 迁移指南

如果你想将旧代码迁移到新架构：

### 1. LLM测试

**旧代码：**
```python
from test_llm import LLMTester

tester = LLMTester("data/dataset.csv")
tester.load_dataset()
tester.test_openai(model="gpt-4")
```

**新代码：**
```python
from src.llm import OpenAIClient
from src.data import DatasetLoader
from src.config import get_config

config = get_config()
loader = DatasetLoader(config.get_path("dataset"))
loader.load()

client = OpenAIClient(
    model_name="gpt-4",
    api_key=config.get_api_key("openai")
)

for prompt in loader.get_prompts():
    response = client.call(prompt)
```

### 2. 结果分析

**旧代码：**
```python
from analyze_results import ResponseAnalyzer

analyzer = ResponseAnalyzer()
result = analyzer.classify_response(response)
```

**新代码：**
```python
from src.analysis import ResponseClassifier

classifier = ResponseClassifier()
result = classifier.classify(response)
```

## 下一步改进（建议）

1. **添加单元测试**
   - tests/test_classifier.py
   - tests/test_llm_clients.py
   - tests/test_data_loader.py

2. **添加CI/CD**
   - GitHub Actions自动测试
   - 代码质量检查（pylint, mypy）

3. **完善文档**
   - API文档（使用Sphinx）
   - 更多使用示例

4. **性能优化**
   - 异步API调用
   - 并行处理

5. **可视化模块重构**
   - 创建 src/visualization/ 模块
   - 面向对象的图表类

## 问题反馈

如果遇到问题：

1. 检查依赖是否完整安装：`pip list | grep -E "pyyaml|openai|anthropic"`
2. 确认.env文件配置正确
3. 查看日志输出了解详细错误

## 版本历史

- **v2.0.0** (2025-01-20) - 面向对象重构
  - 模块化架构
  - 配置管理系统
  - 日志系统
  - 抽象基类设计

- **v1.0.0** - 原始版本
  - 功能脚本
  - 硬编码配置
  - print输出
