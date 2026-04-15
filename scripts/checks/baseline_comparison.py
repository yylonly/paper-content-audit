"""Baseline对比检查"""
import re
from typing import List, Dict


def check_baseline_comparison(content_by_page: List[Dict], full_text: str = "") -> Dict:
    """
    检查实验评估是否包含baseline方法对比

    Returns:
        Dict with keys: baselines_mentioned, comparison_quality, issues, warnings
    """
    baselines_mentioned = []
    comparison_quality = {}
    issues = []
    warnings = []

    text = full_text if full_text else "\n\n".join(p['text'] for p in content_by_page)

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
        r'(BERT|RoBERTa|ALBERT|DistilBERT)\b',
        r'(ResNet|VGG|Inception|DenseNet)\b',
        r'(LSTM|GRU|RNN|CNN)\b',
        r'(Transformer|GPT|BART|T5)\b',
        r'(Adam|SGD|RMSprop)\b',
        r'baseline\s*:?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        r'compared\s+to\s+:?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
    ]

    # 提取实验章节
    experiment_patterns = [
        r'(Experiment|Experiments|Experimental Results|Results|Evaluation)[\s:：\n](.+?)(?=\s*(Conclusion|Related\s+Work|Discussion|Limitations|\d+\.\s+[A-Z]))',
        r'(4|IV)\s+(Experiment|Experiments|Results|Evaluation).*?(?=\s*(Conclusion|Related|\d+\.))',
    ]

    experiment_section = ""
    for pattern in experiment_patterns:
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            experiment_section = match.group(0)
            break

    # 查找baseline提及
    for keyword in baseline_keywords:
        pattern = rf'[^.!?]*\b{keyword}\b[^.!?]*[.!?]'
        matches = re.findall(pattern, text, re.IGNORECASE)
        baselines_mentioned.extend([m.strip() for m in matches if len(m.strip()) > 20])

    # 查找具体baseline方法名
    specific_baselines = []
    for pattern in baseline_patterns:
        matches = re.findall(pattern, text)
        specific_baselines.extend(matches)

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
            't-test', 'paired', 'wilcoxon', 'mann-whitney'
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
