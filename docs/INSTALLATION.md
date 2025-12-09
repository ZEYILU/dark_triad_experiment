# 📦 安装指南

## 快速安装 (5分钟)

```bash
# 1. 进入项目目录
cd "d:\masterthesis\experiment\新建文件夹"

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置 API Keys
copy .env.example .env
# 然后编辑 .env 文件填入你的 API keys

# 4. 验证环境
python verify_setup.py

# 5. 运行实验
python run_quick_experiment.py
```

---

## 详细步骤

### 步骤 1: 确认 Python 版本

需要 Python 3.8 或更高版本。

**检查版本:**
```bash
python --version
```

应该看到类似:
```
Python 3.10.x
```

如果版本过低，请从 [python.org](https://www.python.org/downloads/) 下载安装。

---

### 步骤 2: 安装依赖库

**方法 1: 一键安装 (推荐)**
```bash
pip install -r requirements.txt
```

**方法 2: 逐个安装**
```bash
pip install pandas
pip install openai
pip install anthropic
pip install matplotlib
pip install seaborn
pip install python-dotenv
pip install tqdm
```

**验证安装:**
```bash
python -c "import pandas, openai, anthropic, matplotlib, seaborn; print('All packages installed!')"
```

---

### 步骤 3: 配置 API Keys

#### 3.1 创建 .env 文件

**Windows:**
```bash
copy .env.example .env
```

**Linux/Mac:**
```bash
cp .env.example .env
```

#### 3.2 获取 API Keys

**OpenAI (必需):**
1. 访问 https://platform.openai.com/api-keys
2. 登录或注册账号
3. 点击 "Create new secret key"
4. 复制 key (格式: `sk-...`)

**Anthropic (可选):**
1. 访问 https://console.anthropic.com/settings/keys
2. 登录或注册账号
3. 创建新的 API key
4. 复制 key (格式: `sk-ant-...`)

#### 3.3 填入 API Keys

编辑 `.env` 文件:

```bash
# 用文本编辑器打开
notepad .env
# 或
code .env
```

修改为:
```
OPENAI_API_KEY=sk-your-actual-key-here
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
```

**注意:**
- 去掉示例文本，填入实际的 key
- 不要添加引号
- 确保没有多余的空格

---

### 步骤 4: 验证环境

运行验证脚本:
```bash
python verify_setup.py
```

**期望输出:**
```
1️⃣  检查 Python 版本...
   ✅ Python 3.10.x

2️⃣  检查依赖库...
   ✅ pandas
   ✅ openai
   ✅ anthropic
   ✅ matplotlib
   ✅ seaborn
   ✅ python-dotenv

3️⃣  检查配置文件...
   ✅ .env 文件存在

4️⃣  检查 API Keys...
   ✅ OPENAI_API_KEY 已配置
   ✅ ANTHROPIC_API_KEY 已配置

5️⃣  检查数据集...
   ✅ 数据集加载成功
   📊 包含 126 个 prompts
   ✅ 数据格式正确

6️⃣  检查目录结构...
   ✅ results/ 目录存在
   ✅ figures/ 目录存在

🎉 所有检查通过! 环境配置完成!
```

如果有失败项，请根据提示修复。

---

## 常见问题

### ❌ pip: command not found

**原因:** Python 没有正确安装或未添加到 PATH

**解决:**
- Windows: 重新安装 Python，勾选 "Add Python to PATH"
- 或使用 `python -m pip install` 代替 `pip install`

---

### ❌ ModuleNotFoundError: No module named 'XXX'

**原因:** 依赖库未安装

**解决:**
```bash
pip install XXX
# 或重新安装所有依赖
pip install -r requirements.txt
```

---

### ❌ API Key 无效

**原因:** Key 复制错误或未激活

**解决:**
1. 检查 `.env` 文件中 key 是否完整
2. 确保 key 前后没有空格或引号
3. 在 API 提供商网站验证 key 是否激活
4. 重新生成新的 key

---

### ❌ Permission denied

**原因:** 权限不足

**解决:**
- Windows: 以管理员身份运行命令提示符
- Linux/Mac: 使用 `sudo pip install` (不推荐)
- 或使用虚拟环境 (推荐):
  ```bash
  python -m venv venv
  venv\Scripts\activate  # Windows
  # 或
  source venv/bin/activate  # Linux/Mac
  pip install -r requirements.txt
  ```

---

### ⚠️  中国大陆网络问题

**问题:** pip 下载缓慢或失败

**解决:** 使用国内镜像源
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

**问题:** OpenAI API 无法访问

**解决:**
- 使用代理
- 或使用兼容的国内服务 (需要修改 `base_url`)

---

## 高级配置

### 使用虚拟环境 (推荐)

**创建虚拟环境:**
```bash
python -m venv venv
```

**激活虚拟环境:**
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

**安装依赖:**
```bash
pip install -r requirements.txt
```

**好处:**
- 隔离项目依赖
- 避免版本冲突
- 易于管理

---

### 配置代理 (可选)

如果需要通过代理访问 API:

**方法 1: 环境变量**
```bash
# Windows
set HTTP_PROXY=http://proxy.example.com:8080
set HTTPS_PROXY=http://proxy.example.com:8080

# Linux/Mac
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080
```

**方法 2: 修改代码**
在 `test_llm.py` 中设置 `openai.proxy`:
```python
import openai
openai.proxy = "http://proxy.example.com:8080"
```

---

### 自定义配置

如需高级配置，复制并编辑 `config_example.py`:

```bash
copy config_example.py config.py
```

然后在 `config.py` 中修改:
- API endpoints
- 模型参数
- 筛选条件
- 输出格式
- 等

---

## 验证安装完成

运行测试模式验证一切正常:

```bash
python run_quick_experiment.py
# 选择选项 5 (测试模式)
```

这会:
- 测试 5 个 prompts
- 验证 API 连接
- 确认输出正常
- 成本约 $0.10

如果测试成功，你就可以开始完整实验了! 🎉

---

## 下一步

环境配置完成后:

1. **阅读快速开始指南**
   ```bash
   # 打开文件查看
   notepad QUICK_START.md
   ```

2. **运行完整实验**
   ```bash
   python run_quick_experiment.py
   ```

3. **查看结果**
   ```bash
   python analyze_results.py
   python visualize_results.py
   ```

---

## 获取帮助

如果遇到问题:

1. **运行验证脚本**
   ```bash
   python verify_setup.py
   ```

2. **查看文档**
   - `QUICK_START.md` - 使用指南
   - `README_EXPERIMENT.md` - 项目概述

3. **检查错误消息**
   - 大多数错误消息会指出问题
   - 复制错误消息搜索解决方案

4. **常见问题**
   - 本文档包含常见问题解决方法
   - 查看 `使用说明.md` (中文)

---

**祝你顺利完成环境配置! 🚀**
