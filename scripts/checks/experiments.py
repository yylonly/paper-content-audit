"""实验完整性检查"""
import re
from typing import List, Dict


def check_experiments(content_by_page: List[Dict], sections: Dict = None) -> Dict:
    """
    检查实验完整性：数据集、消融实验、实验覆盖度

    Args:
        content_by_page: 页面内容列表
        sections: 章节内容字典，包含 abstract, introduction, conclusion, method, experiment, full_text

    Returns:
        Dict with keys: datasets, ablation_studies, coverage, issues, warnings
    """
    datasets = []
    ablation_studies = []
    coverage = {}
    issues = []
    warnings = []

    # 获取各部分文本
    if sections and isinstance(sections, dict):
        experiment_section = sections.get('experiment', '')
        method_section = sections.get('method', '')
        full_text = sections.get('full_text', '')
        if not full_text:
            full_text = "\n\n".join(p['text'] for p in content_by_page) if content_by_page else ""
    else:
        full_text = sections if isinstance(sections, str) else "\n\n".join(p['text'] for p in content_by_page) if content_by_page else ""
        experiment_section = method_section = ""

    # 数据集模式 - 在实验章节中查找
    search_text = experiment_section if experiment_section else full_text

    dataset_patterns = [
        r'datasets?\s*:?\s*([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*(?:\s+\d+)?(?:,\s*)?)+',
        r'(?:trained|evaluated|tested)\s+(?:on|with)\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)',
        r'([A-Z][a-zA-Z0-9]+)\s+(?:dataset|corpus|benchmark)',
        r'(?:benchmark|benchmarks)\s*:?\s*([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)',
        # Chinese patterns
        r'样本[集合集]+\s*[：:]\s*([^\s，,]+)',
        r'实验对象\s*[：:]\s*([^\s，,]+)',
        r'数据集\s*[：:]\s*([^\s，,]+)',
    ]

    # 常见数据集关键词
    common_datasets = [
        'ImageNet', 'COCO', 'Pascal', 'MNIST', 'CIFAR', 'GLUE', 'SuperGLUE',
        'SQuAD', 'HotpotQA', 'WikiQA', 'MS MARCO', 'Natural Questions',
        'CoNLL', 'Penn Treebank', 'PTB', 'LAMBADA', 'Winograd',
        'Criteo', 'MovieLens', 'Netflix', 'Amazon', 'Yelp',
        'CelebA', 'LSUN', 'FFHQ', 'Celebrity', 'VoxCeleb',
        'UML', '类图', '顺序图', 'class diagram', 'sequence diagram',
        'D_C', 'D_S', 'D_class', 'D_seq',
    ]

    for pattern in dataset_patterns:
        matches = re.findall(pattern, search_text, re.IGNORECASE)
        datasets.extend(matches)

    # 检查常见数据集
    for dataset in common_datasets:
        if re.search(rf'\b{dataset}\b', search_text, re.IGNORECASE):
            datasets.append(dataset)

    # 去重
    datasets = list(set(datasets))[:10]

    # 消融实验模式 - 在实验章节中查找
    ablation_keywords = [
        'ablation', 'ablate', 'ablated', 'ablation study',
        'component-wise', 'component analysis', 'breakdown',
        'without', 'w/o', 'remove', 'removing',
        'variant', 'variants', 'ablate', 'ablation',
        '消融', '去掉', '去除', '移除', '无'
    ]

    ablation_patterns = [
        r'(?:ablation|ablate)[^.!?]*[.!?]',
        r'(?:w/o|without)\s+[a-z]+[^.!?]*[.!?]',
        r'variant\s+[a-z]+[^.!?]*[.!?]',
        r'(?:component|module)\s+(?:analysis|study)[^.!?]*[.!?]',
        r'消融实验[^.!?。]*[。]',
        r'去掉[^.!?。]*[。]',
        r'去除[^.!?。]*[。]',
    ]

    ablation_found = []
    for keyword in ablation_keywords:
        pattern = rf'[^.!?]*\b{keyword}\b[^.!?]*[.!?]'
        matches = re.findall(pattern, search_text, re.IGNORECASE)
        ablation_found.extend(matches)
    # Also check Chinese patterns directly
    for pattern in ablation_patterns:
        matches = re.findall(pattern, search_text)
        ablation_found.extend(matches)

    # 消融实验详情
    ablation_studies = list(set(ablation_found))[:5]

    # 评估实验覆盖度
    coverage = {
        'has_main_results': bool(re.search(r'(?:main|overall|final)\s+(?:result|performance)', search_text, re.IGNORECASE)),
        'has_ablation': len(ablation_studies) > 0,
        'has_dataset_variety': len(datasets) >= 2,
        'has_analysis': bool(re.search(r'(?:analysis|analysis of)', search_text, re.IGNORECASE)),
        'has_complexity': any(kw in search_text.lower() for kw in ['complexity', 'efficiency', 'speed', 'time', 'parameter']),
        'significance': bool(re.search(r'(?:p-value|significantly|statistical|t-test|paired)', search_text, re.IGNORECASE)),
    }

    # 检查缺失的实验
    if not datasets:
        issues.append(
            "❌ 未找到明确的数据集说明 / No clear dataset description found"
        )

    if len(datasets) == 1:
        warnings.append(
            "⚠️ 仅在单个数据集上评估，建议在多个数据集上验证 / Only evaluated on single dataset, recommend evaluating on multiple datasets"
        )

    if not ablation_studies:
        warnings.append(
            "⚠️ 未找到消融实验(Ablation Study)，无法验证各组件的贡献 / No ablation study found, cannot verify contribution of each component"
        )

    if not coverage['has_main_results']:
        warnings.append(
            "⚠️ 未找到明确的整体性能结果 / No clear main/overall performance results found"
        )

    if not coverage['has_analysis']:
        warnings.append(
            "⚠️ 缺乏深入的分析讨论 / Lacks in-depth analysis discussion"
        )

    if not coverage['has_complexity']:
        warnings.append(
            "⚠️ 缺乏效率/复杂度分析 / Lacks efficiency/complexity analysis"
        )

    return {
        'datasets': datasets,
        'ablation_studies': ablation_studies,
        'coverage': coverage,
        'issues': issues,
        'warnings': warnings
    }
