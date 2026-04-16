---
name: paper-content-audit
description: |
  论文内容审核工具。用于审核学术论文的主要贡献、方法创新性、实验评估，以及与baseline的详细对比。
  触发场景：用户提到"审核论文"、"论文评审"、"paper review"、"论文创新性"、"论文贡献"、"论文评估"、"review paper"、"audit paper"、"check paper quality"、"论文对比baseline"、"分析论文"等。
  Also triggers when user wants to verify paper contributions, method innovation, experimental evaluation against baselines, or assess methodological improvements over existing work.
  功能：使用LLM智能提取论文中的解决的问题、创新点、评估内容，生成纯中文HTML格式的完整审核报告。支持Claude Code终端直接LLM分析（无需额外API配置）。
  重要更新：分析现有方法问题时，必须给出具体参考文献，并判断是否为近3年内工作（2023-2026）和顶会顶刊。
  新增功能：检查评价指标、现有方法问题、创新点、贡献点是否超过3个，若超过则给出具体合并建议。
---

# Paper Content Audit Skill

学术论文内容审核工具，使用大模型智能分析论文的主要贡献、方法创新性、实验评估质量，以及与baseline的详细对比情况。

## 审核功能（三大核心部分）

### 追溯关系图
```
主要问题 ──→ 方法创新 ──→ 评估验证
    │              │              │
    │         解决什么问题      研究问题RQ
    │              │         数据集/指标
    │              │         结果/局限
    └──────── 方法层面分析 ────┘
```

### 审核功能矩阵

| 审核项 | 说明 | 追溯关系 |
|--------|------|----------|
| **一、主要问题分析** | 现有方法在什么情况下解决不好或解决不了，为什么不行 | 问题根源的深层原因分析 |
| **二、方法创新性** | 本文提出什么方法，如何在方法层面解决已有问题 | 创新点→问题的直接对应 |
| **三、评估验证** | 研究问题、数据集、指标、结果、局限性 | 创新效果的可量化验证 |
| 方法-创新对应 | 每个创新点是否在方法部分有详细描述 | 确保可追溯 |
| **方法vs Baseline对比** | 详细展示方法相对baseline的具体改进和性能指标 | 验证创新有效性 |
| Baseline对比 | 实验评估是否包含baseline方法对比 | 评估完整性 |
| 实验完整性 | 实验是否覆盖关键场景和消融实验 | 验证可靠性 |
| 增量改进识别 | 是否将增量改进误标为"novel" | 客观评估创新程度 |

## Background Task工作流

本skill采用**Background Task模式**，将审核流程拆分为四个独立后台Task并行/串行执行：

```
┌─────────────────────────────────────────────────────────────┐
│  Task 1: PDF文本提取 (Background)                           │
│  使用Python提取器从PDF中提取文本内容                          │
│  输出: 论文全文文本                                            │
│  状态: 自动后台执行，无需等待                                  │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  Task 2: 参考文献调研 (并行Agent执行)                        │
│  为每个现有方法单独启动Agent调研其参考文献                     │
│  输出: 各方法的参考文献信息（含顶会顶刊判断）                   │
│  状态: 多Agent并行执行，同时完成                              │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  Task 3: LLM综合分析 (Background)                          │
│  使用当前会话的LLM能力直接分析论文内容                         │
│  输入: 论文文本 + 参考文献调研结果                            │
│  输出: 结构化的审核数据(JSON格式)                              │
│  状态: 自动后台执行，无需等待                                  │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  Task 4: 报告生成 (Background)                             │
│  使用Python生成HTML格式的审核报告                            │
│  输出: HTML报告文件                                          │
│  状态: 自动后台执行，完成后通知用户                            │
└─────────────────────────────────────────────────────────────┘
```

**执行方式**: 使用`run_in_background=true`参数执行所有Task，用户无需等待完成

---

## 详细执行步骤

### Task 1: PDF文本提取 (Background)

**执行方式**: Python代码 (run_in_background)

**命令**:
```bash
python3 <skill_path>/scripts/paper_audit_script.py --step1 <pdf_path> [output_dir]
```

**说明**:
- 使用pdfplumber/PyMuPDF/pypdf提取PDF文本
- 按页分割，便于后续LLM分析
- 输出论文标题、页数、提取方法

**输出**:
- 论文文本内容（保存到临时文件）
- 文本路径用于下一步Task 2

---

### Task 2: 参考文献调研 (并行Agent执行)

**执行方式**: 使用多个Agent并行调研每个现有方法/问题的参考文献

**输入**: Task 1提取的论文文本路径

**执行步骤**:

对于论文中提到的每个现有方法/问题，**单独启动一个Agent**进行并行调研：

```
对于每个被分析的现有方法 M:
  Agent "<方法名>调研" 执行:
    1. 在论文的参考文献列表中查找该方法的原始论文
    2. 使用WebSearch验证论文信息(顶会/期刊、年份)
    3. 确定该方法所属的研究流派和技术路线
    4. 返回结构化的参考文献信息
```

**调研内容**:
- 论文全称、作者、发表年份
- 发表 venue（会议/期刊名称）
- venue 级别判断：
  - 顶会：NeurIPS, ICML, ICLR, ACL, EMNLP, NAACL, COLING, AAAI, IJCAI, ASE, ICSE, FSE, ISSTA, OOPSLA, PLDI, POPL, SIGIR, KDD, WWW, CHI, ICPC, SANER 等
  - 顶刊：IEEE TPAMI, IJCV, JMLR, ACM Computing Surveys, IEEE TNNLS, IEEE TKDE, IEEE TSE 等
  - CCF-A/B 列表中的会议和期刊
- 是否近3年内工作（当前年份2026，即2021年后发表）

**顶会顶刊判断标准**:
- CCF-A类会议/期刊 → 顶级
- CCF-B类会议/期刊 → 高水平
- CCF-C类或其他 → 一般
- 无法确认 → 待确认

**并行执行**: 多个方法的调研Agent同时启动，互不依赖

---

### Task 3: LLM综合分析 (Background)

**执行方式**: Background Task - 直接在后台执行，使用当前会话LLM能力

**输入**: Task 1提取的论文文本路径 + Task 2各方法的参考文献信息

**分析内容（按追溯关系组织）**:
1. **基本信息** - 论文标题、作者、学位、学校、学科专业
2. **一、主要问题分析** - 现有方法在什么情况下解决不好或解决不了，揭示方法层面的根本原因
3. **二、方法创新性** - 每个创新点 → 直接解决哪个问题，创新点与问题的对应关系
4. **三、评估验证** - 研究问题(RQ)、数据集、评价指标、评估结果、局限性
5. **Baseline对比** - 对比方法列表 + 性能指标
6. **方法vs Baseline详细对比** - 每个方法相对baseline的具体改进点和性能指标差值
7. **增量改进识别** - 区分novel vs incremental
8. **综合评价** - 优点 + 主要不足

**追溯关系要求**：
- 主要问题必须有对应的方法创新来解决
- 方法创新必须有对应的评估结果来验证
- 评估结果必须能追溯到具体解决了哪个问题

**输出格式（带追溯关系）**:
```json
{
  "paper_title": "论文标题",
  "basic_info": {
    "论文标题": "...",
    "作者": "...",
    "学位": "...",
    "学校": "...",
    "学科专业": "...",
    "审核时间": "YYYY-MM-DD"
  },

  "一_主要问题分析": [
    {
      "问题编号": "P1",
      "问题描述": "现有方法在XX情况下解决不好/解决不了",
      "现有方法表现": "具体失败案例或性能数据",
      "问题根源": "为什么现有方法不行——方法层面的根本原因分析",
      "对应创新点": ["I1"],
      "参考文献": [
        {
          "论文标题": "论文全称",
          "作者": "作者列表",
          "年份": YYYY,
          "venue": "会议/期刊名称",
          "venue级别": "CCF-A/CCF-B/CCF-C/其他",
          "是否近3年": true/false,
          "顶会顶刊判断": "顶级/高水平/一般/待确认"
        }
      ]
    }
  ],

  "二_方法创新性": [
    {
      "创新编号": "I1",
      "创新点": "创新点描述",
      "section": "对应章节",
      "details": "具体方法内容",
      "解决的问题": ["P1", "P2"],
      "创新类型": "原创性/组合性/适应性"
    }
  ],

  "三_评估验证": {
    "research_questions": [
      {"rq_id": "RQ1", "rq描述": "研究问题描述", "对应的创新点": ["I1"]}
    ],
    "datasets": [
      {"dataset_name": "数据集名", "size": "样本数", "description": "数据集描述"}
    ],
    "metrics": [
      {"metric_name": "指标名", "definition": "指标定义", "higher_better": true}
    ],
    "results": {
      "主实验结果": {...},
      "消融实验结果": {...},
      "关键发现": ["发现1", "发现2"]
    },
    "limitations": [
      {"limitation": "局限性描述", "acknowledged_by_paper": true}
    ]
  },

  "method_vs_baseline": [
    {
      "method_name": "本文方法",
      "baseline": "对比方法名",
      "improvements": ["具体改进点1", "具体改进点2"],
      "metrics": [
        {"metric": "ISR", "baseline_value": "43.8%", "proposed_value": "58.4%", "improvement": "+14.6%"}
      ]
    }
  ],

  "baseline_traceability": [
    {"baseline": "方法名", "对比的创新点": ["I1"], "metrics_improved": ["metric1"]}
  ],

  "incremental_improvements": [
    {"contribution": "贡献点", "assessment": "评估", "is_novel": true}
  ],

  "overall_scores": [
    {"dimension": "维度", "result": "✅/⚠️/❌"}
  ],

  "summary": {
    "strengths": ["优点1", "优点2"],
    "weaknesses": ["不足1", "不足2"],
    "traceability_check": {
      "problems_with_solutions": true,
      "solutions_with_evaluation": true,
      "evaluation_traces_to_problems": true
    }
  }
}
```

**追溯关系检查要点**:
1. 每个主要问题(P)必须至少有一个对应创新点(I)
2. 每个创新点(I)必须至少有一个评估结果验证其效果
3. 每个评估结果必须能追溯到具体解决了哪个问题

---

## 贡献点数量约束检查（重要！）

**核心原则**：评价指标、现有方法问题、创新点、贡献点均不超过3个。超过3个会给读者造成认知负担，且难以形成聚焦的研究贡献。

### 数量约束规则

| 类型 | 最大数量 | 超过时的处理 |
|------|---------|-------------|
| 评价指标 | 3个 | 合并相关指标，说明主要衡量维度 |
| 现有方法问题 | 3个 | 合并根源相同或相关的问题 |
| 创新点 | 3个 | 合并方法层面高度相关的创新 |
| 贡献点 | 3个 | 提炼核心贡献，区分主次 |

### 合并建议格式

当发现超过3个时，在审核报告中明确给出：

```json
{
  "constraint_check": {
    "评价指标": {
      "count": 5,
      "exceeds": true,
      "建议合并": [
        {
          "original": ["指标A", "指标B"],
          "merged": "合并后的指标名",
          "reason": "合并原因说明"
        }
      ]
    },
    "现有方法问题": {
      "count": 4,
      "exceeds": true,
      "建议合并": [
        {
          "original": ["问题1", "问题2"],
          "merged": "合并后的问题描述",
          "reason": "两个问题根源相同，都是XX导致的"
        }
      ]
    },
    "创新点": {
      "count": 4,
      "exceeds": true,
      "建议合并": [
        {
          "original": ["创新点A", "创新点B"],
          "merged": "合并后的创新点",
          "reason": "两个创新点在方法层面高度相关，可作为整体贡献"
        }
      ]
    },
    "贡献点": {
      "count": 4,
      "exceeds": true,
      "建议合并": [
        {
          "original": ["贡献点1", "贡献点2"],
          "merged": "合并后的贡献",
          "reason": "这两点实质上是同一个贡献的不同侧面"
        }
      ]
    }
  }
}
```

### 合并建议的判断标准

**可以合并的情况**：
- 多个指标衡量同一维度（如准确率、召回率、F1都是分类任务指标）
- 多个问题有相同的根本原因
- 多个创新点在方法实现上相互依赖、不可分割
- 多个贡献点实质上是同一个贡献的不同表达

**不宜合并的情况**：
- 合并后丢失重要信息
- 被合并项之间实际上解决的问题不同
- 合并会导致贡献变得模糊、不聚焦

### 合并后的最终输出

审核报告的最终输出中，每个类别严格控制在3个以内：
- 评价指标：3个主要衡量维度（如效率、准确率、鲁棒性）
- 现有方法问题：3个核心瓶颈
- 创新点：3个方法层面的主要贡献
- 贡献点：3个可总结的核心贡献

### 输出示例

```json
{
  "final_contributions": {
    "评价指标": [
      {"维度": "效率", "具体指标": ["时间复杂度", "空间复杂度"]},
      {"维度": "准确率", "具体指标": ["Top-1准确率", "Top-5准确率"]},
      {"维度": "鲁棒性", "具体指标": ["对抗攻击准确率"]}
    ],
    "现有方法问题": [
      {"问题": "P1", "描述": "语义保持与几何优化的冲突"},
      {"问题": "P2", "描述": "评价体系未统一"},
      {"问题": "P3", "描述": "方法之间缺乏有效衔接"}
    ],
    "创新点": [
      {"编号": "I1", "描述": "统一建模框架"},
      {"编号": "I2", "描述": "差异化布局方法"},
      {"编号": "I3", "描述": "规则-LLM协同机制"}
    ],
    "贡献点": [
      "提出了统一的UML布局建模框架",
      "设计了差异化的类图和顺序图布局方法", 
      "建立了规则与大模型协同的布局策略机制"
    ]
  }
}
```

**关键字段说明 - method_vs_baseline**:
- `method_name`: 本文方法名称
- `baseline`: 对比的baseline方法名称
- `improvements`: 具体改进点列表（基于论文描述）
- `metrics`: 性能指标对比数组，每项包含:
  - `metric`: 指标名称（如ISR、VFS、CodeBLEU）
  - `baseline_value`: baseline方法的数值
  - `proposed_value`: 本文方法的数值
  - `improvement`: 相对提升（绝对值或百分比）

---

### Task 4: 报告生成 (Background)

**执行方式**: Python代码 (run_in_background)

**命令**:
```bash
python3 <skill_path>/scripts/paper_audit_script.py --step3 --llm-data '<json字符串>' [output_dir]
```

**说明**:
- 将Task 3的LLM分析结果传入
- 生成HTML格式的审核报告
- 报告包含参考文献的顶会顶刊判断和近3年分析

**输出报告**:

| 格式 | 文件名 | 说明 |
|------|--------|------|
| HTML统一报告 | `paper_audit_report_YYYYMMDD_HHMMSS.html` | 包含所有审核信息的完整报告（含参考文献分析） |

---

## 一键执行模式

如果用户希望一键完成审核，可以使用：

```bash
python3 <skill_path>/scripts/paper_audit_script.py <pdf_path> [output_dir]
```

这会自动执行Task 1 → Task 2 → Task 3，但：
- Task 2使用备用启发式提取（无并行Agent调研）
- Task 3使用简化分析（无LLM语义深度分析）
- 推荐使用Background Task串行模式以获得更完整的LLM分析质量

---

## 依赖要求

```bash
pip install pypdf pdfplumber PyMuPDF
```

**库说明：**
- `pdfplumber`：PDF文本提取，推荐首选，对中文支持较好
- `PyMuPDF` (fitz)：备选，对表格和图形提取较好
- `pypdf`：基础库，用于最终fallback

---

## CCF排名参考标准

### CCF-A类会议（顶级）
NeurIPS, ICML, ICLR, ACL, EMNLP, NAACL, COLING, AAAI, IJCAI, ASE, ICSE, FSE, ISSTA, OOPSLA, PLDI, POPL, SIGIR, KDD, WWW, CHI, ICPC, SANER

### CCF-A类期刊（顶级）
IEEE TPAMI, IJCV, JMLR, ACM Computing Surveys, IEEE TNNLS, IEEE TKDE, IEEE TSE

### CCF-B类会议（高水平）
NeurIPS (Workshops), ICLR (Workshops), ACL (Findings), EMNLP (Findings), NAACL (Findings), COLING, AAAI, IJCAI, ASE, ICSE (NIER), FSE (Ideas/Doctoral/Sandbox), ISSTA, OOPSLA, PLDI, POPL, SIGIR, KDD (Research), WWW (Research), CHI, ICPC, SANER, MSR, ESEC/FSE

### 常用顶会顶刊快速判断
- **软件工程**: ICSE, FSE, ASE, ISSTA, OOPSLA, PLDI, POPL → CCF-A
- **人工智能/机器学习**: NeurIPS, ICML, ICLR, AAAI, IJCAI → CCF-A
- **自然语言处理**: ACL, EMNLP, NAACL, COLING → CCF-A
- **数据挖掘/信息检索**: KDD, SIGIR, WWW → CCF-A
- **人机交互**: CHI → CCF-A

---

## 注意事项

1. **Background Task模式**: 四个Task全部使用run_in_background参数执行，完成后自动通知
2. **Task 2参考文献调研**: 使用多个Agent并行调研，每个现有方法单独一个Agent
3. **近3年判断**: 当前年份2026，即2023-2026年发表的工作为近3年内
4. **顶会顶刊判断**: 优先参考CCF列表，同时考虑Google Scholar h5-index等综合指标
5. **method_vs_baseline字段**: 审核报告的核心部分，必须包含每个方法与baseline的详细性能对比
6. **PDF提取限制**: PDF文本提取可能无法获取精确格式信息
7. **主观评估**: 创新性和贡献的评估具有一定主观性，仅供参考
