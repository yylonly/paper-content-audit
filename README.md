# Paper Content Audit Tool / 论文内容审核工具

A Claude Code skill for auditing academic papers, evaluating main contributions, methodological innovation, experimental evaluation, and detailed comparison with baselines.

一个用于审核学术论文的Claude Code工具，主要贡献评估、方法创新性、实验评估以及与baseline的详细对比。

## Features / 功能特点

| Feature | Description | 说明 |
|---------|-------------|------|
| 贡献点评估 | Extract and evaluate main contributions | 提取并评估论文主要贡献 |
| 创新点识别 | Identify method innovations | 识别方法创新点 |
| Baseline对比 | Compare with existing methods | 与现有方法对比 |
| 实验完整性 | Verify experiment coverage | 验证实验完整性 |
| 增量改进识别 | Distinguish novel vs incremental | 区分创新与增量改进 |
| 多格式报告 | HTML/Markdown/bilingual reports | 多格式报告输出 |

## Installation / 安装

This is a Claude Code skill. Install it by placing the `paper-content-audit` folder in your Claude Code skills directory.

这是Claude Code技能。将其放入Claude Code的skills目录即可使用。

```bash
# Clone or copy to your skills directory
# 克隆或复制到skills目录
```

## Quick Start / 快速开始

### Claude Code Terminal Direct Analysis (Recommended) / Claude Code终端直接分析（推荐）

当你在Claude Code中时，直接说：
- "使用当前终端分析这篇论文"
- "用Claude Code终端直接分析"
- "Analyze this paper using the current terminal session"

The skill will use Claude Code's built-in LLM capabilities to analyze the paper directly without needing any additional API configuration.

该技能将直接使用Claude Code内置的LLM能力分析论文，无需额外API配置。

### Using the Python Script / 使用Python脚本

```bash
# Navigate to the skill directory
cd /path/to/paper-content-audit

# Run with PDF file
python3 scripts/paper_audit_script.py /path/to/paper.pdf

# Run with text content
python3 scripts/paper_audit_script.py --text "论文全文内容..."

# Run with API key for LLM enhancement
export ANTHROPIC_API_KEY="your-api-key"
python3 scripts/paper_audit_script.py paper.pdf
```

## Usage Scenarios / 使用场景

| Chinese | English |
|---------|---------|
| 审核论文 | Audit paper |
| 论文评审 | Paper review |
| 分析论文创新点 | Analyze paper innovations |
| 检查论文贡献 | Check paper contributions |
| 论文质量评估 | Paper quality assessment |
| 对比baseline | Compare with baselines |
| 验证实验完整性 | Verify experiment completeness |

## Output / 输出

The skill generates **4 report formats**:

技能生成**4种报告格式**：

1. **Markdown报告** - `paper_audit_report_YYYY-MM-DD_HHMMSS.md`
2. **HTML基础报告** - `paper_audit_report_YYYYMMDD_HHMMSS.html`
3. **HTML补充报告** - `paper_audit_supplementary_report_YYYY-MM-DD_HHMMSS.html`
4. **中英双语报告** - `论文内容审核报告_中英双语_YYYY-MM-DD_HHMMSS.md`

## Report Contents / 报告内容

| Section | Description | 说明 |
|---------|-------------|------|
| 基本信息 | Title, authors, degree, institution | 标题、作者、学位、学校 |
| 主要贡献 | Contribution points with evaluation | 贡献点及评估 |
| 方法创新性 | Innovation points with method support | 创新点及方法支撑 |
| Baseline对比 | Comparison with existing methods | 与现有方法对比 |
| 实验完整性 | Experiment coverage analysis | 实验覆盖分析 |
| 增量改进 | Novel vs incremental assessment | 创新与增量评估 |
| 综合评分 | Overall scores by dimension | 各维度综合评分 |
| 总结 | Strengths and weaknesses | 优点与不足 |

## Dependencies / 依赖

```bash
pip install pypdf pdfplumber PyMuPDF
```

Optional for LLM extraction:
```bash
pip install anthropic
export ANTHROPIC_API_KEY="your-key"
```

## Project Structure / 项目结构

```
paper-content-audit/
├── SKILL.md                 # Skill definition
├── README.md                # This file
├── scripts/
│   ├── paper_audit_script.py    # Main entry
│   ├── extractors/
│   │   ├── content.py           # PDF extraction
│   │   └── llm_extractor.py     # LLM extraction
│   └── reports/
│       └── generator.py         # Report generation
```

## Examples / 示例

### Example 1: Audit a PDF file

```bash
python3 scripts/paper_audit_script.py /path/to/paper.pdf
```

### Example 2: Audit with text content

```bash
python3 scripts/paper_audit_script.py --text "论文摘要和内容..."
```

### Example 3: Specify output directory

```bash
python3 scripts/paper_audit_script.py paper.pdf ./output
```

## Notes / 注意事项

1. **Chinese Support**: Optimized for Chinese academic papers
2. **LLM Analysis**: Claude Code terminal can analyze directly without API key
3. **Fallback**: Enhanced heuristic extraction when LLM unavailable
4. **Report Language**: Reports can be generated in Chinese, English, or bilingual

---

## 许可证 / License

MIT License

## 作者 / Author

Claude Code Skill

## 更新日志 / Changelog

### v2.0 (2026-04-15)
- 添加Claude Code终端直接LLM分析功能
- 添加中英双语报告生成
- 增强备用启发式提取算法
- 更新SKILL.md描述

### v1.0 (2026-04-14)
- 初始版本
- 支持PDF文本提取
- 支持HTML/Markdown报告生成
