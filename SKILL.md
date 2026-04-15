---
name: paper-content-audit
description: |
  论文内容审核工具。用于审核学术论文的主要贡献、方法创新性、实验评估，以及与baseline的详细对比。
  触发场景：用户提到"审核论文"、"论文评审"、"paper review"、"论文创新性"、"论文贡献"、"论文评估"、"review paper"、"audit paper"、"check paper quality"、"论文对比baseline"、"分析论文"等。
  Also triggers when user wants to verify paper contributions, method innovation, experimental evaluation against baselines, or assess methodological improvements over existing work.
  功能：使用LLM智能提取论文中的解决的问题、创新点、评估内容，生成纯中文HTML格式的完整审核报告。支持Claude Code终端直接LLM分析（无需额外API配置）。
---

# Paper Content Audit Skill

学术论文内容审核工具，使用大模型智能分析论文的主要贡献、方法创新性、实验评估质量，以及与baseline的详细对比情况。

## 核心架构

```
PDF文件 ──> Python PDF提取器 ──> 论文文本
                                      │
                                      ▼
              ┌───────────────────────┴───────────────────────┐
              │                                               │
              ▼                                               ▼
      Claude Code终端直接分析                      备用启发式提取
      (当前会话LLM能力)                              (无API时启用)
              │                                               │
              ▼                                               ▼
                              结构化审核数据
                                      │
                                      ▼
                              HTML/Markdown/双语报告
```

## 审核功能

| 审核项 | 类型 | 说明 |
|--------|------|------|
| 解决的问题 | ✅ | 论文解决了什么问题，有什么创新 |
| 主要贡献 | ✅ | 贡献点是否明确、具体、可验证 |
| 方法创新性 | ✅ | 创新点是否有对应的方法改进 |
| 方法-创新对应 | ⚠️ 警告 | 每个创新点是否在方法部分有详细描述 |
| 方法vs Baseline对比 | ✅ | 详细展示方法相对baseline的具体改进和性能指标 |
| Baseline对比 | ❌ 问题 | 实验评估是否包含baseline方法对比 |
| 实验完整性 | ⚠️ 警告 | 实验是否覆盖关键场景和消融实验 |
| 增量改进识别 | ⚠️ 警告 | 是否将增量改进误标为"novel" |

## 使用方法

### 方法一：使用Claude Code终端直接分析（推荐，无需API配置）

当用户说"使用当前调用skill的claude code终端进行LLM提取"或类似表述时，直接使用当前会话的LLM能力进行分析：

1. 读取论文PDF或已提取的文本
2. 在当前Claude Code会话中直接使用LLM分析论文内容
3. 生成审核报告

### 方法二：使用Python脚本（需要Python环境）

```bash
# 设置API密钥（启用LLM功能，可选）
export ANTHROPIC_API_KEY="your-api-key"

# 运行审核
python3 <skill_path>/scripts/paper_audit_script.py <pdf_path> [output_dir]

# 或直接传入文本
python3 <skill_path>/scripts/paper_audit_script.py --text "<论文文本>" [output_dir]
```

**参数说明:**
- `pdf_path`: 论文PDF文件路径
- `--text` 或 `-t`: 直接传入论文文本内容
- `output_dir`: 可选，报告输出目录（默认当前目录）

**环境变量:**
- `ANTHROPIC_API_KEY`: Anthropic API密钥（可选，不设置时使用备用分析或Claude Code终端直接分析）

### 依赖要求

```bash
pip install pypdf pdfplumber PyMuPDF
```

**库说明：**
- `pdfplumber`：PDF文本提取，推荐首选，对中文支持较好
- `PyMuPDF` (fitz)：备选，对表格和图形提取较好
- `pypdf`：基础库，用于最终fallback
- `anthropic`：LLM API调用（可选，不安装则使用备用分析）

## 输出报告

审核完成后生成**四个格式**的结构化报告：

#### 1. Markdown报告 (`paper_audit_report_YYYY-MM-DD_HHMMSS.md`)
- 纯文本格式，便于复制和进一步编辑
- 包含所有审核项的完整内容

#### 2. HTML基础报告 (`paper_audit_report_YYYYMMDD_HHMMSS.html`)
- 快速概览审核结果
- 包含所有核心审核项的表格化展示

#### 3. HTML补充报告 (`paper_audit_supplementary_report_YYYY-MM-DD_HHMMSS.html`)
- 详细的完整审核内容
- 包含LLM提取的完整信息：
  - **基本信息** - 论文标题、作者、学位、学校、类型
  - **问题解决** - 论文解决的问题和创新点
  - **主要贡献评估** - 贡献点、方法支撑、评估结果表格
  - **方法创新性评估** - 创新点、方法章节、创新具体内容表格
  - **Baseline对比评估** - 对比方法列表、说明、论文位置
  - **实验完整性评估** - 实验类型、章节、说明表格
  - **增量改进识别** - 各贡献点的增量vs novel评估
  - **综合评分** - 各审核维度的评分结果
  - **总结** - 优点列表 + 主要不足列表

#### 4. 中英双语Markdown报告 (`论文内容审核报告_中英双语_YYYY-MM-DD_HHMMSS.md`)
- 中英双语对照格式
- 包含所有审核项的双语内容
- 便于向国际评审展示论文审核结果

## 无LLM时的增强提取

当未设置`ANTHROPIC_API_KEY`时，skill会按以下优先级启用分析：

1. **优先**：使用Claude Code终端直接分析（当前会话LLM能力）
2. **其次**：使用增强的启发式提取：
   - 从摘要和引言提取研究问题
   - 从主要贡献章节提取贡献点
   - 从创新点章节提取创新点
   - 从实验章节提取Baseline方法
   - 自动识别实验类型（总体对比、显著性分析、消融实验、敏感性分析等）
   - 提取评估指标和数据规模信息

**建议**：虽然无LLM模式也能生成报告，但设置API密钥或使用Claude Code终端直接分析可获得更精确的语义分析结果。

## 脚本结构

```
scripts/
├── paper_audit_script.py   # 主入口
├── extractors/
│   ├── content.py          # Python PDF文本提取
│   └── llm_extractor.py    # LLM智能内容提取
└── reports/
    └── generator.py         # 报告生成（支持HTML/Markdown/双语）
```

### extractors/content.py
纯Python实现的PDF文本提取器，支持：
- pdfplumber（首选，对中文支持好）
- PyMuPDF（备选）
- pypdf（最终fallback）

### extractors/llm_extractor.py
LLM驱动的论文内容提取器，通过Anthropic API分析论文语义：
- `extract_with_llm()` - 主提取函数
- `LLMExtractor` - 提取器类
- 分段处理长论文避免token限制

### reports/generator.py
报告生成器，生成四种格式：
- HTML基础报告
- HTML补充报告（含完整审核项）
- Markdown报告
- 中英双语Markdown报告

## 报告数据结构

```python
full_audit_data = {
    'paper_title': '论文标题',
    'basic_info': {
        '论文标题': '...',
        '作者': '...',
        '学位': '...',
        '学校': '...',
        '类型': '...',
        '审核时间': 'YYYY-MM-DD'
    },
    'contributions': [
        {'point': '贡献点描述', 'method': '方法支撑', 'evaluation': '✅/❌ 评估结果'}
    ],
    'method_innovations': [
        {'innovation': '创新点', 'section': '章节', 'details': '具体内容', 'status': '✅/❌'}
    ],
    'baselines': [
        {'name': 'baseline名称', 'description': '说明', 'section': '论文位置'}
    ],
    'experiments': [
        {'type': '实验类型', 'section': '章节', 'description': '说明'}
    ],
    'incremental_improvements': [
        {'contribution': '贡献点', 'assessment': '评估'}
    ],
    'overall_scores': [
        {'dimension': '审核维度', 'result': '✅/⚠️/❌ 结果'}
    ],
    'summary': {
        'strengths': ['优点1', '优点2'],
        'weaknesses': ['不足1', '不足2']
    },
    'llm_evaluation': {
        # LLM原始评估数据
        'datasets': [],
        'metrics': [],
        'baseline_methods': [],
        'statistical_significance': '是/否',
        'ablation_study': '是/否'
    }
}
```

## 注意事项

1. **API密钥**: 设置`ANTHROPIC_API_KEY`环境变量可启用LLM智能提取功能
2. **Claude Code终端**: 当前会话的LLM能力可以直接用于分析论文，无需额外配置
3. **文本提取限制**: PDF文本提取可能无法获取精确格式信息
4. **主观评估**: 创新性和贡献的评估具有一定主观性，仅供参考
5. **报告生成**: 使用`full_audit_data`参数传入完整审核信息以获得最佳报告效果
