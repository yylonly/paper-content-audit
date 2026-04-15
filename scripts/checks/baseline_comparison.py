"""Baseline对比检查"""
import re
from typing import List, Dict


def check_baseline_comparison(content_by_page: List[Dict], sections: Dict = None) -> Dict:
    """
    检查实验评估是否包含baseline方法对比

    Args:
        content_by_page: 页面内容列表
        sections: 章节内容字典，包含 abstract, introduction, conclusion, method, experiment, full_text

    Returns:
        Dict with keys: baselines_mentioned, comparison_quality, issues, warnings
    """
    baselines_mentioned = []
    comparison_quality = {}
    issues = []
    warnings = []

    # 获取各部分文本
    if sections and isinstance(sections, dict):
        experiment_section = sections.get('experiment', '')
        full_text = sections.get('full_text', '')
        if not full_text:
            full_text = "\n\n".join(p['text'] for p in content_by_page) if content_by_page else ""
    else:
        full_text = sections if isinstance(sections, str) else "\n\n".join(p['text'] for p in content_by_page) if content_by_page else ""
        experiment_section = ""

    # 常见的baseline方法关键词
    baseline_keywords = [
        "baseline", "baselines", "state-of-the-art", "sota",
        "previous method", "existing method", "traditional method",
        "conventional", "standard method", "classic",
        "compared with", "compare with", "compared to",
        "outperform", "outperforms", "surpass", "exceed",
        "vs.", "versus", "vs ", "against"
    ]

    # 常见的baseline方法名模式
    baseline_patterns = [
        # ML/CV models
        r'(BERT|RoBERTa|ALBERT|DistilBERT)\b',
        r'(ResNet|VGG|Inception|DenseNet)\b',
        r'(LSTM|GRU|RNN|CNN)\b',
        r'(Transformer|GPT|BART|T5)\b',
        r'(Adam|SGD|RMSprop)\b',
        # UML/Auto Layout tools
        r'\b(ELK|Graphviz|Visual\s+Paradigm|StarUML|PlantUML|UMLet|Umbrello)\b',
        # Generic method names in this paper
        r'\b(Rule|LLM|Hybrid|Default|Baseline|Traditional|Classical)\b',
        r'baseline\s*:?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        r'compared\s+to\s+:?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        # Chinese baseline references
        r'对比\s*([A-Za-z]+)',
        r'基准\s*([A-Za-z]+)',
    ]

    # 提取实验章节 - 如果sections中没有，尝试从全文中提取
    if not experiment_section:
        experiment_patterns = [
            r'(?:5\s+Experiment|Experimental Results|Results|Evaluation)[\s:：\n](.+?)(?=\n\s*(?:6\s+|Conclusion| Related|$))',
            r'(?:第\s*5\s*章)[\s:：\n](.+?)(?=\n\s*(?:第\s*6\s*章|6\s+|$))',
        ]
        for pattern in experiment_patterns:
            match = re.search(pattern, full_text, re.DOTALL | re.IGNORECASE)
            if match:
                experiment_section = match.group(0)
                break

    # 查找baseline提及 - 在实验章节中查找
    search_text = experiment_section if experiment_section else full_text

    for keyword in baseline_keywords:
        pattern = rf'[^.!?]*\b{keyword}\b[^.!?]*[.!?]'
        matches = re.findall(pattern, search_text, re.IGNORECASE)
        baselines_mentioned.extend([m.strip() for m in matches if len(m.strip()) > 20])

    # 查找具体baseline方法名 - 在全文中查找
    specific_baselines = []
    for pattern in baseline_patterns:
        matches = re.findall(pattern, full_text)
        specific_baselines.extend(matches)

    # Also look for Chinese baseline references
    chinese_baseline_patterns = [
        r'基准方法[：:\s]*([^\s，,]+)',
        r'baseline[：:\s]*([^\s，,]+)',
        r'对比方法[：:\s]*([^\s，,]+)',
        r'传统方法[：:\s]*([^\s，,]+)',
        r'已有方法[：:\s]*([^\s，,]+)',
    ]
    for pattern in chinese_baseline_patterns:
        matches = re.findall(pattern, full_text, re.IGNORECASE)
        specific_baselines.extend([m.strip() for m in matches if len(m.strip()) > 1])

    # Also extract method names from experiment section that appear in comparison context
    if experiment_section:
        # Find method names followed by numbers (likely performance metrics)
        method_metric_pattern = r'([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)\s*[=:]\s*\d+[\.\d]*'
        found_methods = re.findall(method_metric_pattern, experiment_section)
        specific_baselines.extend([m for m in found_methods if len(m) > 2])

        # Also look for table-like data (method names at start of lines)
        table_method_pattern = r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+\d'
        found_table_methods = re.findall(table_method_pattern, experiment_section, re.MULTILINE)
        specific_baselines.extend(found_table_methods)

    unique_baselines = list(set(specific_baselines))

    # 评估对比质量
    has_quantitative_comparison = False
    has_statistical_significance = False
    has_fair_comparison = False

    if experiment_section:
        # 检查是否有数值对比
        if re.search(r'\d+[.%]|\d+\.\d+', experiment_section):
            has_quantitative_comparison = True

        # 检查是否有统计显著性说明
        stat_keywords = [
            'p-value', 'significantly', 'statistical', 'confidence',
            't-test', 'paired', 'wilcoxon', 'mann-whitney', 'p值', '显著性'
        ]
        if any(kw in experiment_section.lower() for kw in stat_keywords):
            has_statistical_significance = True

        # 检查对比是否公平（相同数据集、相同设置）
        if all(kw in experiment_section.lower() for kw in ['same', 'dataset', 'setting']):
            has_fair_comparison = True
        elif 'standard benchmark' in experiment_section.lower():
            has_fair_comparison = True

    comparison_quality = {
        'has_quantitative_comparison': has_quantitative_comparison,
        'has_statistical_significance': has_statistical_significance,
        'has_fair_comparison': has_fair_comparison,
        'baselines_count': len(unique_baselines)
    }

    # 生成问题列表
    if not baselines_mentioned and not unique_baselines:
        issues.append(
            "❌ 论文未提及任何baseline方法进行对比 / Paper doesn't mention any baseline methods for comparison"
        )

    if baselines_mentioned and not has_quantitative_comparison:
        warnings.append(
            "⚠️ 论文提及baseline但缺乏定量对比数据 / Paper mentions baselines but lacks quantitative comparison data"
        )

    if unique_baselines and len(unique_baselines) < 2:
        warnings.append(
            f"⚠️ 仅与 {len(unique_baselines)} 个baseline对比，建议与更多方法对比 / Only compared with {len(unique_baselines)} baseline(s), recommend comparing with more methods"
        )

    if not has_statistical_significance:
        warnings.append(
            "⚠️ 实验结果缺乏统计显著性说明 / Experimental results lack statistical significance explanation"
        )

    if baselines_mentioned and not experiment_section:
        issues.append(
            "❌ 论文声称与baseline对比但未找到实验章节 / Paper claims baseline comparison but no experiment section found"
        )

    return {
        'baselines_mentioned': baselines_mentioned[:10],
        'unique_baselines': unique_baselines,
        'comparison_quality': comparison_quality,
        'issues': issues,
        'warnings': warnings
    }
