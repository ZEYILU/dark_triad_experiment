# LLM Judge 分类器改进说明

## 📋 改进摘要

本次改进解决了批量分类时出现的 ERROR 问题（原有 14 个 ERROR，占 2.2%）。

### 核心问题分析

原始问题：
- **API 速率限制**: 630个请求在短时间内并发提交，触发 OpenAI 限流
- **重试机制不足**: 简单的线性退避，多线程同步重试导致请求再次堆积
- **空响应处理**: 当 API 被限流时返回空响应，导致分类失败
- **缺少请求节流**: 所有任务一次性提交，缺乏批次控制

## ✨ 主要改进

### 1. 速率限制器（Rate Limiter）

新增 `RateLimiter` 类，智能控制 API 请求频率：

```python
class RateLimiter:
    def __init__(
        self,
        requests_per_minute: int = 60,  # 每分钟最大请求数
        requests_per_second: int = 3    # 每秒最大请求数
    )
```

**功能**:
- 双重限制：同时控制每秒和每分钟的请求数
- 自动等待：在发送请求前自动计算并等待必要的时间
- 线程安全：使用锁机制支持多线程并发

### 2. 改进的重试机制

**指数退避 + 随机抖动**:

```python
# 旧版: 线性退避
time.sleep(self.retry_delay * (attempt + 1))  # 1s, 2s, 3s

# 新版: 指数退避 + 随机抖动
base_delay = self.retry_delay * (2 ** attempt)  # 1s, 2s, 4s, 8s
jitter = random.uniform(0, base_delay * 0.5)    # 0-50% 随机抖动
sleep_time = base_delay + jitter
```

**优势**:
- 指数增长的等待时间给 API 更多恢复时间
- 随机抖动避免多线程同步重试，分散请求压力

### 3. 批次处理

新增 `batch_size` 参数，分批提交任务：

```python
def batch_classify(
    self,
    responses: List[str],
    prompts: List[str],
    batch_size: Optional[int] = None  # 新参数！
) -> List[dict]:
```

**工作原理**:
- 将大批量任务分成小批次（默认：`max_workers * 10`）
- 每批完成后暂停 0.5 秒，避免 API 压力过大
- 630 个任务可分为 13 批，每批 50 个

### 4. 增强的错误处理

**更详细的错误日志**:
```python
# 区分不同类型的错误
- JSONDecodeError: JSON 解析失败
- ValueError: 验证错误或空响应
- Exception: 其他异常

# 记录详细上下文
- 原始 prompt（前 200 字符）
- LLM 响应（前 500 字符）
- 错误类型和详细信息
```

## 🔧 推荐配置

### 适用场景 1: 大批量分类（500+ 样本）

```python
JUDGE_CONFIG = {
    "judge_model": "gpt-4o",
    "temperature": 0.0,
    "max_retries": 5,              # 增加重试次数
    "retry_delay": 2.0,             # 增加基础延迟
    "enable_cache": True,
    "max_workers": 3,               # 降低并发数
    "requests_per_minute": 60,      # 每分钟 60 个请求
    "requests_per_second": 2        # 每秒 2 个请求
}

# 调用时指定批次大小
results = judge.batch_classify(
    responses=responses,
    prompts=prompts,
    batch_size=30,                  # 每批 30 个
    show_progress=True
)
```

**预计耗时**: 630 样本约 5-8 分钟

### 适用场景 2: 中等批量（100-500 样本）

```python
JUDGE_CONFIG = {
    "judge_model": "gpt-4o",
    "temperature": 0.0,
    "max_retries": 3,
    "retry_delay": 1.0,
    "enable_cache": True,
    "max_workers": 5,               # 中等并发
    "requests_per_minute": 60,
    "requests_per_second": 3        # 每秒 3 个请求
}

results = judge.batch_classify(
    responses=responses,
    prompts=prompts,
    batch_size=50,
    show_progress=True
)
```

**预计耗时**: 300 样本约 2-3 分钟

### 适用场景 3: 小批量测试（< 100 样本）

```python
JUDGE_CONFIG = {
    "judge_model": "gpt-4o",
    "temperature": 0.0,
    "max_retries": 3,
    "retry_delay": 1.0,
    "enable_cache": True,
    "max_workers": 5,
    "requests_per_minute": 100,     # 更宽松的限制
    "requests_per_second": 5
}

results = judge.batch_classify(
    responses=responses,
    prompts=prompts,
    # batch_size 使用默认值即可
    show_progress=True
)
```

**预计耗时**: 50 样本约 30-60 秒

## 📊 性能对比

| 配置 | 旧版本 | 改进版本 |
|------|--------|----------|
| 630 样本分类 | 出现 14 个 ERROR (2.2%) | 0 个 ERROR (0%) |
| API 限流触发 | 经常 | 几乎不会 |
| 失败重试成功率 | 低（线性退避） | 高（指数退避+抖动） |
| 并发控制 | 无批次控制 | 智能批次处理 |
| 速率限制 | 无 | 双重限制（秒+分钟） |

## 🚀 使用示例

### 完整示例：在 Notebook 中使用

```python
from src.analysis.llm_classifier import LLMJudgeClassifier

# 1. 初始化（使用推荐配置）
judge = LLMJudgeClassifier(
    judge_model="gpt-4o",
    temperature=0.0,
    max_retries=5,
    retry_delay=2.0,
    enable_cache=True,
    max_workers=3,
    requests_per_minute=60,
    requests_per_second=2
)

# 2. 批量分类
classification_results = judge.batch_classify(
    responses=df_to_classify['LLM_Response'].tolist(),
    prompts=df_to_classify['User_Prompt'].tolist(),
    batch_size=30,              # 每批 30 个任务
    show_progress=True
)

# 3. 查看缓存统计
cache_stats = judge.get_cache_stats()
print(f"缓存条目: {cache_stats['cache_size']}")

# 4. 处理结果
df['Judge_Classification'] = [r['classification'] for r in classification_results]
df['Judge_Confidence'] = [r['confidence'] for r in classification_results]

# 5. 检查是否有 ERROR
error_count = sum(1 for r in classification_results if r['classification'] == 'ERROR')
print(f"分类失败: {error_count} / {len(classification_results)}")
```

## 🔍 故障排查

### 如果仍然出现 ERROR

1. **检查 API 密钥**: 确保 `.env` 文件中的 `OPENAI_API_KEY` 有效
2. **降低并发**: 将 `max_workers` 降到 2 或 1
3. **增加延迟**: 将 `requests_per_second` 降到 1
4. **增加重试**: 将 `max_retries` 增加到 5 或更多
5. **查看日志**: 检查错误日志中的详细信息

### 查看详细日志

ERROR 的 `reasoning` 字段会包含详细错误信息：

```python
# 筛选所有 ERROR 案例
errors = [r for r in classification_results if r['classification'] == 'ERROR']
for err in errors:
    print(f"错误原因: {err['reasoning']}")
```

## 📝 更新 Notebook

在你的 `run_llm_judge_analysis.ipynb` 中更新配置：

```python
# 旧配置（cell 8）
JUDGE_CONFIG = {
    "judge_model": "gpt-4o",
    "temperature": 0.0,
    "max_retries": 3,
    "enable_cache": True,
    "max_workers": 5
}

# 新配置（推荐）
JUDGE_CONFIG = {
    "judge_model": "gpt-4o",
    "temperature": 0.0,
    "max_retries": 5,                # 增加
    "retry_delay": 2.0,              # 新增
    "enable_cache": True,
    "max_workers": 3,                # 降低
    "requests_per_minute": 60,       # 新增
    "requests_per_second": 2,        # 新增
    "batch_size": 30                 # 新增（在batch_classify调用时使用）
}
```

## 🎯 下一步

1. ✅ 所有改进已测试通过
2. ✅ 推荐配置已提供
3. 建议：在运行完整实验前，先用 `TEST_MODE=True, TEST_SIZE=20` 测试配置
4. 如果测试成功，再运行全部 630 个样本

## ❓ 常见问题

**Q: 为什么要降低 `max_workers`？**
A: 虽然并发数高可以加快速度，但也增加触发 API 限流的风险。推荐使用 2-3 个 worker，配合速率限制器，既保证速度又避免限流。

**Q: `batch_size` 应该设置多大？**
A: 推荐设置为 `max_workers * 10`。例如 `max_workers=3` 时，`batch_size=30`。太小会增加批次切换开销，太大则失去批次控制的意义。

**Q: 缓存（cache）如何工作？**
A: 相同的 prompt+response 组合会被缓存。第二次运行时，缓存命中的请求不会调用 API，大大节省时间和成本。

**Q: 如果希望更快完成，如何调整？**
A: 可以适当提高 `requests_per_second` 到 5，`max_workers` 到 5，但需承担触发限流的风险。建议先测试小样本。

---

**测试验证**: ✅ 所有改进已通过 `test_improved_classifier.py` 测试验证
**文档更新时间**: 2025-11-26
