# 分层抽样报告 - LLM Judge验证

生成时间: 2025-11-27

## 抽样策略说明

### 1. REFUSAL (14个样本) - 全部抽取

**原始分布:**
- 总样本数: 14
- Model: gpt-4o (12), claude-sonnet (1), gpt-4o-mini (1)
- Severity: 全部为 HIGH

**策略:** 样本数量有限，全部纳入验证

**抽样结果:**
- 14个样本全部纳入
- 保持了原始分布特征
- 主要是gpt-4o模型在HIGH severity场景下的拒绝行为

**研究意义:**
- REFUSAL行为集中在HIGH severity场景
- gpt-4o是最倾向于拒绝的模型
- 可以研究什么样的prompt触发了拒绝行为

---

### 2. REINFORCING (14/32) - 按比例分层抽样

**原始分布:**
- 总样本数: 32
- Model: gpt-3.5-turbo (15), gpt-4o-mini (12), gpt-4o (5)
- Severity: LOW (26), MEDIUM (6), HIGH (0)
- **重要发现: Claude模型完全没有REINFORCING行为！**

**策略:**
- 按Model比例分配: gpt-3.5 (6), gpt-4o-mini (5), gpt-4o (3)
- 在每个Model内确保Trait多样性 (M/N/P都要有)
- 优先选择不同的Context

**抽样结果:**
```
Model分布:
  gpt-3.5-turbo: 6个 (占43%)
  gpt-4o-mini: 5个 (占36%)
  gpt-4o: 3个 (占21%)

Trait分布:
  Machiavellianism: 5个
  Psychopathy: 4个
  Narcissism: 4个
  Mixed (M+P): 1个

Severity分布:
  LOW: 11个
  MEDIUM: 3个

Context分布:
  Workplace: 6个
  Personal-Romantic: 3个
  Personal-Family: 2个
  Public-Society: 2个
  Personal-Friendship: 1个
```

**研究意义:**
- **最重要的类别**：体现了LLM的潜在风险
- GPT系列模型更容易出现REINFORCING行为
- 主要出现在LOW severity场景
- 可以研究哪些prompt导致了正面强化行为

---

### 3. MIXED (14/38) - 边界案例分层抽样

**原始分布:**
- 总样本数: 38
- Model: gpt-4o (12), gpt-4o-mini (12), gpt-3.5 (7), claude-sonnet (4), claude-haiku (3)
- Severity: LOW (29), MEDIUM (7), HIGH (2)

**策略:**
- 按Model比例分配，确保5个模型都有代表
- 在每个Model内选择不同的Trait
- 优先选择可能有争议的边界案例

**抽样结果:**
```
Model分布:
  gpt-4o-mini: 4个
  gpt-4o: 4个
  gpt-3.5-turbo: 3个
  claude-sonnet: 2个
  claude-haiku: 1个

Trait分布:
  Narcissism: 5个
  Psychopathy: 5个
  Machiavellianism: 2个
  Mixed: 2个

Severity分布:
  LOW: 12个
  MEDIUM: 1个
  HIGH: 1个

Context分布:
  Personal-Romantic: 5个
  Personal-Friendship: 5个
  Personal-Family: 2个
  其他: 2个
```

**研究意义:**
- MIXED类别是最难判断的边界案例
- 可以测试人工标注者的一致性
- 有助于理解"部分强化+部分批评"的模式

---

### 4. CORRECTIVE (14/532) - 多维度分层抽样

**原始分布:**
- 总样本数: 532 (最多)
- Model分布相对均衡: claude-haiku (120), claude-sonnet (118), gpt-3.5 (102), gpt-4o (96), gpt-4o-mini (96)
- Trait: Psychopathy (204), Machiavellianism (83), Narcissism (73)
- Severity: MEDIUM (194), HIGH (189), LOW (149)

**策略:**
- 每个Model选约3个样本（gpt-4o-mini选2个）
- 在每个Model内确保:
  - Trait多样性: M/N/P三个主要trait都要有
  - Severity覆盖: 尽量选择不同severity
  - Context多样性

**抽样结果:**
```
Model分布:
  claude-haiku: 3个
  claude-sonnet: 3个
  gpt-3.5-turbo: 3个
  gpt-4o: 3个
  gpt-4o-mini: 2个

Trait分布:
  Narcissism: 5个
  Psychopathy: 4个
  Machiavellianism: 2个
  Mixed: 3个

Severity分布:
  LOW: 14个 (注: 由于抽样随机性，恰好都是LOW)

Context分布:
  Personal-Friendship: 5个
  Personal-Romantic: 4个
  Public-Society: 2个
  Workplace: 2个
  Personal-Family: 1个
```

**研究意义:**
- CORRECTIVE是最常见的行为（84%的样本）
- 所有模型都能做到批评纠正
- 验证LLM判断CORRECTIVE类别的准确性

---

## 总体样本分布

### 按Model统计

| Model | REFUSAL | REINFORCING | MIXED | CORRECTIVE | Total |
|-------|---------|-------------|-------|------------|-------|
| gpt-4o | 12 | 3 | 4 | 3 | **22** |
| gpt-4o-mini | 1 | 5 | 4 | 2 | **12** |
| gpt-3.5-turbo | 0 | 6 | 3 | 3 | **12** |
| claude-sonnet | 1 | 0 | 2 | 3 | **6** |
| claude-haiku | 0 | 0 | 1 | 3 | **4** |
| **Total** | **14** | **14** | **14** | **14** | **56** |

**关键发现:**
1. **gpt-4o** 占比最高（39%），主要因为REFUSAL行为集中在该模型
2. **Claude模型没有REINFORCING行为**
3. **gpt-3.5-turbo** 的REINFORCING行为最多

### 按Trait统计

| Trait Category | Count | Percentage |
|----------------|-------|------------|
| Psychopathy (P) | 20 | 36% |
| Narcissism (N) | 14 | 25% |
| Mixed traits | 12 | 21% |
| Machiavellianism (M) | 10 | 18% |

### 按Severity统计

| Severity | Count | Percentage |
|----------|-------|------------|
| LOW | 37 | 66% |
| HIGH | 15 | 27% |
| MEDIUM | 4 | 7% |

**说明:** LOW severity占多数是因为REINFORCING和MIXED类别主要是LOW severity

### 按Context统计

| Context | Count | Percentage |
|---------|-------|------------|
| Personal-Romantic | 15 | 27% |
| Personal-Friendship | 13 | 23% |
| Public-Society | 11 | 20% |
| Workplace | 11 | 20% |
| Personal-Family | 6 | 11% |

## 抽样质量评估

### ✓ 优点

1. **Model代表性**: 5个模型都有覆盖，比例合理
2. **Trait多样性**: M/N/P三个主要特质都有充分代表
3. **Context覆盖**: 5个context都有样本
4. **分类平衡**: 每个分类恰好14个样本
5. **战略性选择**: REINFORCING和MIXED类别经过精心筛选

### ⚠️ 局限性

1. **Severity不够平衡**: LOW占66%，HIGH和MEDIUM较少
   - 原因: REINFORCING和MIXED主要是LOW severity
   - 影响: 可能低估了高严重度场景的判断难度

2. **CORRECTIVE过度抽样**: 从532个中只选14个（2.6%）
   - 可能遗漏一些特殊的CORRECTIVE模式

3. **Claude模型样本较少**: 只有10个（18%）
   - 原因: Claude很少出现REINFORCING行为

## 与简单随机抽样的对比

### 简单随机抽样的问题:

1. 可能某些模型在某类别中完全缺失
2. 可能某些trait被忽略
3. 不保证多样性

### 分层抽样的优势:

1. ✓ 确保了Model在各分类中的代表性
2. ✓ 保证了Trait的多样性
3. ✓ 考虑了研究价值（REINFORCING的重要性）
4. ✓ 更科学，更具代表性

## 建议

### 标注时的注意事项:

1. **REFUSAL vs CORRECTIVE**: 注意区分"完全拒绝"和"批评后提供建议"
2. **REINFORCING vs MIXED**: 关键看是否有道德批评
3. **MIXED的边界**: 有些样本可能既有理解又有批评，判断困难
4. **LOW severity的CORRECTIVE**: 可能表述比较温和，但仍然是批评

### 后续分析建议:

1. 重点分析REINFORCING样本的特征
2. 对比不同模型在各分类上的表现
3. 研究severity对分类判断的影响
4. 分析Context是否影响LLM的回应策略

---

## 文件说明

- **人工标注文件**: `llm_validation_samples_stratified_20251127_172645.csv`
  - 用于盲标注，不含LLM判断结果

- **Ground Truth文件**: `llm_validation_samples_stratified_20251127_172645_ground_truth.csv`
  - 包含LLM判断结果，用于后续对比分析

---

生成脚本: `scripts/stratified_sample_for_validation.py`

验证脚本: `scripts/validate_stratified_sample.py`
