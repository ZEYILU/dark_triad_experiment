# Dark Triad Dataset - Complete Package

## 📦 Package Contents

This package contains the fully cleaned and standardized Dark Triad dataset for your ACL paper submission, along with comprehensive documentation and analysis reports.

---

## 📄 Files Included

### 🌟 Main Dataset File
**`Dark_Triad_Dataset_FINAL.csv`** (60 KB)
- **126 prompts** across 42 base scenarios
- **5 columns:** ID, Primary Trait, Context, Severity, User Prompt to LLM
- **100% complete:** Every scenario has LOW, MEDIUM, HIGH versions
- **Ready to use** for LLM testing

---

### 📚 Documentation Files

#### English Documentation

**`Dataset_Cleaning_Report.md`** (9.6 KB)
- Comprehensive report on all cleaning operations
- Detailed statistics and methodology
- Quality assurance verification
- Perfect for citing in your paper's methodology section

**`Quick_Start_Guide.md`** (8.2 KB)
- How to use the dataset for your research
- Python code examples
- Analysis suggestions
- Timeline for ACL submission (Jan 6, 2026 deadline)

#### Chinese Documentation

**`数据集清理说明_中文版.md`** (5.3 KB)
- 完整的中文说明
- 数据统计
- 使用方法
- 研究建议

---

### 📊 Reference Reports

**`gap_report.csv`** (1.3 KB)
- List of 19 missing prompts that were generated
- Shows which severity levels were added to complete triads

**`id_renumbering_map.csv`** (387 bytes)
- Old ID → New ID mapping
- Useful for tracking changes from original dataset

**`scenario_mapping_table.csv`** (2.3 KB)
- Complete overview of all 42 scenarios
- Shows LOW/MEDIUM/HIGH completion status
- Trait and context for each scenario

**`trait_breakdown_report.csv`** (258 bytes)
- Detailed breakdown by trait type
- Scenario counts and prompt counts
- Severity distribution per trait

**`dataset_summary_report.csv`** (102 bytes)
- High-level statistics summary
- Total counts and completeness metrics

---

## 🎯 Quick Start

### 1. Load the Dataset
```python
import pandas as pd
df = pd.read_csv('Dark_Triad_Dataset_FINAL.csv')
print(f"Total prompts: {len(df)}")
```

### 2. Understand the Structure
- **ID format:** `[TRAIT][NUMBER]_[severity]`
  - Example: `M01_low` = Machiavellianism, Scenario 1, Low severity
  
- **Trait codes:**
  - M = Machiavellianism
  - N = Narcissism
  - P = Psychopathy
  - MP, MN, NP = Mixed traits

- **Severities:** LOW, MEDIUM, HIGH (all uppercase in Severity column)

### 3. Test with Your LLMs
```python
for idx, row in df.iterrows():
    prompt = row['User Prompt to LLM']
    
    # Send to your target LLM
    response = your_llm.generate(prompt)
    
    # Store results
    results.append({
        'ID': row['ID'],
        'Prompt': prompt,
        'Response': response,
        'Trait': row['Primary Trait'],
        'Severity': row['Severity']
    })
```

---

## 📈 Dataset Statistics

### Distribution Summary

| Metric | Count | Notes |
|--------|-------|-------|
| **Total Prompts** | 126 | 42 scenarios × 3 severities |
| **Base Scenarios** | 42 | All complete with LOW/MEDIUM/HIGH |
| **Trait Types** | 9 | M, N, P, and 6 mixed combinations |
| **Contexts** | 5 | Workplace, Friendship, Romantic, Society, Family |
| **Duplicates** | 0 | All prompts are unique |

### Trait Distribution
- Psychopathy: 48 prompts (38.1%)
- Machiavellianism: 21 prompts (16.7%)
- Mixed (M+P): 18 prompts (14.3%)
- Narcissism: 18 prompts (14.3%)
- Other Mixed: 21 prompts (16.7%)

### Severity Balance
- LOW: 42 prompts (33.3%)
- MEDIUM: 42 prompts (33.3%)
- HIGH: 42 prompts (33.3%)

✅ **Perfect balance achieved!**

---

## ✅ Quality Assurance

All prompts have been verified for:
- ✅ Zero duplicates (exact text matching)
- ✅ Complete triads (all scenarios have L/M/H)
- ✅ Consistent ID format
- ✅ Neutral question phrasing (no "right?" or "don't you think?")
- ✅ Context consistency within triads
- ✅ Clear severity progression

---

## 🔬 Research Applications

This dataset enables analysis of:

1. **Behavioral Reinforcement vs Correction**
   - How often do LLMs validate negative behaviors?
   - At what severity do they start correcting?

2. **Trait-Specific Patterns**
   - Are certain traits treated more leniently?
   - Do mixed traits elicit different responses?

3. **Context Effects**
   - Professional vs personal contexts
   - Public vs private settings

4. **Cross-Model Comparisons**
   - GPT-4 vs Claude vs Llama
   - Open-source vs proprietary models

5. **Severity Thresholds**
   - Is there a "tipping point" where responses change?
   - How do responses scale with behavior severity?

---

## 📝 For Your ACL Paper

### Methodology Section - Dataset Description

Suggested text:
> "We developed a standardized corpus of 126 prompts describing negative behavioral patterns based on the Dark Triad framework (Machiavellianism, Narcissism, Psychopathy). Each of 42 base scenarios includes three severity levels (LOW, MEDIUM, HIGH), distributed across five contexts (Workplace, Personal-Friendship, Personal-Romantic, Public-Society, Personal-Family). All prompts use neutral question formats to avoid biasing model responses, enabling systematic analysis of LLM behavioral guidance across varying degrees of ethically problematic behavior."

### Dataset Availability Statement

> "The complete Dark Triad dataset containing 126 prompts across 42 scenarios is available at [your repository link]. The dataset includes standardized ID formats, trait classifications, context labels, and severity levels, facilitating reproducible research on LLM ethical alignment."

---

## 📅 Timeline to Submission (January 6, 2026)

### Weeks 1-2 (Nov 5-19)
- [ ] Test all 126 prompts with 3-5 LLMs
- [ ] Save responses with complete metadata

### Weeks 3-4 (Nov 20-Dec 3)
- [ ] Code responses (reinforcement/correction/neutral)
- [ ] Inter-rater reliability check
- [ ] Statistical analysis

### Weeks 5-6 (Dec 4-17)
- [ ] Write first draft
- [ ] Create visualizations
- [ ] Identify key examples

### Weeks 7-8 (Dec 18-31)
- [ ] Revise and refine
- [ ] Complete all sections
- [ ] Proofread

### Week 9 (Jan 1-6)
- [ ] Final formatting
- [ ] ACL guidelines check
- [ ] Submit!

---

## 🎓 Citation

When describing this cleaning process in your methodology:

> "The original dataset was standardized through a systematic cleaning process: (1) removing duplicates, (2) standardizing ID formats to [TRAIT][NUMBER]_[severity] convention, (3) identifying and generating missing severity levels to ensure complete LOW-MEDIUM-HIGH triads, and (4) verifying context consistency and neutral question phrasing. This resulted in a final dataset of 126 prompts across 42 complete scenarios."

---

## 📞 Support

For detailed information, refer to:
- **English:** `Dataset_Cleaning_Report.md` and `Quick_Start_Guide.md`
- **中文:** `数据集清理说明_中文版.md`

For questions about specific scenarios or prompts, check:
- `scenario_mapping_table.csv` - Overview of all scenarios
- `gap_report.csv` - List of generated prompts
- `trait_breakdown_report.csv` - Statistics by trait

---

## ✨ Key Features

🎯 **Complete Coverage**
- All 42 scenarios have LOW, MEDIUM, HIGH versions
- Balanced distribution across traits and contexts

📊 **Research-Ready**
- Standardized format for easy analysis
- Clear metadata for filtering and grouping
- Neutral phrasing for unbiased testing

🔬 **Scientifically Sound**
- Based on validated Dark Triad framework
- Systematic severity progression
- Context-consistent triads

📝 **Well-Documented**
- Comprehensive cleaning report
- Detailed methodology
- Clear usage guidelines

---

## 🚀 Summary

This package provides everything you need for your ACL submission:

✅ High-quality dataset (126 prompts)
✅ Complete documentation (English + Chinese)
✅ Reference reports for transparency
✅ Usage guidelines and examples
✅ Timeline and paper structure suggestions

**The dataset is ready for immediate use in your research!**

---

**Dataset Version:** FINAL v1.0  
**Date:** November 5, 2025  
**Prepared for:** ACL 2026 Submission (Deadline: January 6, 2026)  
**Research Focus:** Investigating LLM Responses to Negative Behavioral Patterns

**Good luck with your research! 祝你研究顺利！🎓📝**
