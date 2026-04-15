---
name: paper-content-audit
description: |
  论文内容审核工具。用于审核学术论文的主要贡献、方法创新性、实验评估，以及与baseline的详细对比。
  触发场景：用户提到"审核论文"、"论文评审"、"paper review"、"论文创新性"、"论文贡献"、"论文评估"、"review paper"、"audit paper"、"check paper quality"、"论文对比baseline"等。
  Also triggers when user wants to verify paper contributions, method innovation, experimental evaluation against baselines, or assess methodological improvements over existing work.
  功能：生成包含完整审核信息的中英双语HTML报告，支持中文PDF自动提取（pdfplumber/PyMuPDF/pypdf多库支持），包括主要贡献声明、创新点方法对应、Baseline对比、方法与Baseline详细对比、实验完整性评估、增量改进识别、综合评分和总结。
---

# Paper Content Audit Skill

学术论文内容审核工具，用于评估论文的主要贡献、方法创新性、实验评估质量，以及与baseline的详细对比情况。

## 审核功能

本skill执行以下审核项：

| 审核项 | 类型 | 说明 |
|--------|------|------|
| 主要贡献 | ✅/❌ | 论文贡献点是否明确、具体、可验证 |
| 方法创新性 | ✅/❌ | 创新点是否有对应的方法改进 |
| 方法-创新对应 | ⚠️ 警告 | 每个创新点是否在方法部分有详细描述 |
| 方法vs Baseline对比 | ✅ | 详细展示方法相对baseline的具体改进和性能指标 |
| Baseline对比 | ❌ 问题 | 实验评估是否包含baseline方法对比 |
| 实验完整性 | ⚠️ 警告 | 实验是否覆盖关键场景和消融实验 |
| 增量改进识别 | ⚠️ 警告 | 是否将增量改进误标为"novel" |
| 缺失对比 | ⚠️ 警告 | 是否有遗漏的对比方法或数据集 |

## 使用方法

### 快速开始

当用户提供PDF文件路径或论文文本时，执行：

```bash
python3 <skill_path>/scripts/paper_audit_script.py <pdf_path> [output_dir]
# 或
python3 <skill_path>/scripts/paper_audit_script.py --text "<论文文本>" [output_dir]
```

**参数说明:**
- `pdf_path`: 论文PDF文件路径
- `--text` 或 `-t`: 直接传入论文文本内容
- `output_dir`: 可选，报告输出目录（默认当前目录）

**示例:**
```bash
python3 paper_audit_script.py /path/to/paper.pdf
python3 paper_audit_script.py --text "论文全文内容..."
python3 paper_audit_script.py paper.pdf ./output
```

### 依赖要求

推荐安装多个PDF提取库以支持中英文PDF：

```bash
pip install pypdf pdfplumber PyMuPDF
```

**库说明：**
- `pdfplumber`：推荐首选，对中文支持较好
- `PyMuPDF` (fitz)：备选，对表格和图形提取较好
- `pypdf`：基础库，用于最终 fallback

### 自动化审核流程

1. **提取论文内容** - 使用pypdf读取PDF或解析文本
2. **分析贡献声明** - 从摘要、引言、结论中提取贡献点
3. **验证创新对应** - 检查每个贡献是否有方法支撑
4. **检查实验评估** - 验证baseline对比、实验完整性
5. **生成报告** - 输出结构化审核报告

### 输出报告

审核完成后生成**中英双语HTML格式**的结构化报告。

**报告内容:**
1. **基本信息** - 论文标题、作者、学位、学校、类型
2. **主要贡献评估** - 贡献点、方法支撑、评估结果表格
3. **方法创新性评估** - 创新点、方法章节、创新具体内容表格
4. **方法创新性与Baseline详细对比** - 每种方法相对baseline的具体改进和性能指标
5. **Baseline对比评估** - 对比方法列表、说明、论文位置
6. **实验完整性评估** - 实验类型、章节、说明表格
7. **增量改进识别** - 各贡献点的增量vs novel评估
8. **综合评分** - 各审核维度的评分结果表格
9. **总结** - 优点列表 + 主要不足列表

**报告格式:** HTML（可直接在浏览器中打开）
- 中英双语标题
- 表格化展示各项审核结果
- 颜色区分：绿色(✅通过)、红色(❌问题)、黄色(⚠️警告)
- info-box/warning-box/error-box 区分不同类型信息
- comparison-card 展示方法vs Baseline详细对比
- 响应式布局，支持移动端查看

## 报告数据结构

生成报告时使用 `full_audit_data` 参数据传递完整审核信息：

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
    'method_vs_baseline': [
        {
            'method_name': '方法名称',
            'baseline': '对比的baseline',
            'improvements': ['具体改进点1', '具体改进点2'],
            'metrics': ['性能指标1', '性能指标2']
        }
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
    }
}
```

## 脚本结构

```
scripts/
├── paper_audit_script.py   # 主入口
├── extractors/
│   └── content.py          # 内容提取
├── checks/
│   ├── contributions.py    # 贡献点提取与分析
│   ├── innovation.py        # 创新性验证
│   ├── baseline_comparison.py # Baseline对比检查
│   └── experiments.py       # 实验完整性检查
└── reports/
    └── generator.py         # 报告生成（支持full_audit_data参数）
```

## 审核规范参考

### 主要贡献评估标准

**好的贡献声明:**
- 明确说明解决了什么问题
- 指出相比现有方法的优势
- 贡献点具体、可验证

**差的贡献声明:**
- 只描述任务而没有解决方案
- 缺乏与现有工作的对比说明
- 贡献点过于宽泛或无法验证

### 方法创新性评估标准

每个创新点必须满足:
1. **方法层面** - 在方法部分有详细的算法/模型描述
2. **改进明确** - 清楚说明相比baseline的具体改进
3. **理论支撑** - 有理论分析或动机解释

### 方法vs Baseline对比评估标准

**必须包含:**
- 方法相对每个baseline的具体改进点
- 性能提升指标（数值对比）
- 改进百分比或绝对值

**建议包含:**
- 可视化的对比卡片（comparison-card）
- 消融实验结果

### Baseline对比评估标准

**必须包含:**
- 与至少一个主流baseline的方法对比
- 在标准数据集上的性能对比
- 统计显著性说明（如适用）

**建议包含:**
- 消融实验（Ablation Study）
- 与同类方法的公平对比
- 复杂度/效率对比

## 添加新审核项

如需添加新审核项，推荐在 `scripts/checks/` 下创建独立模块，遵循以下约定：

```python
# scripts/checks/my_check.py
from typing import List, Dict

def check_my_item(content: Dict, ...) -> Dict:
    """
    审核项说明

    Returns:
        Dict with keys: result, issues, warnings
    """
    issues = []
    warnings = []
    result = {}

    # 审核逻辑...

    return {
        'result': result,
        'issues': issues,
        'warnings': warnings
    }
```

然后在 `scripts/checks/__init__.py` 中导出，在 `paper_audit_script.py` 的 `run_full_audit()` 中调用即可。

## 注意事项

1. **文本提取限制**: PDF文本提取可能无法获取精确格式信息
2. **主观评估**: 创新性和贡献的评估具有一定主观性，仅供参考
3. **领域差异**: 不同领域对创新性和baseline的定义可能不同
4. **报告生成**: 推荐使用 `full_audit_data` 参数传入完整审核信息以获得最佳报告效果
