"""方法创新性验证"""
import re
from typing import List, Dict


def check_innovation(content_by_page: List[Dict], sections: Dict = None) -> Dict:
    """
    验证方法创新性：检查创新点是否有对应的方法描述

    Args:
        content_by_page: 页面内容列表
        sections: 章节内容字典，包含 abstract, introduction, conclusion, method, experiment, full_text

    Returns:
        Dict with keys: innovations, method_correspondence, issues, warnings
    """
    innovations = []
    method_correspondence = []
    issues = []
    warnings = []

    # 获取各部分文本
    if sections and isinstance(sections, dict):
        method_section = sections.get('method', '')
        abstract_text = sections.get('abstract', '')
        intro_text = sections.get('introduction', '')
        full_text = sections.get('full_text', '')
        if not full_text:
            full_text = "\n\n".join(p['text'] for p in content_by_page) if content_by_page else ""
    else:
        full_text = sections if isinstance(sections, str) else "\n\n".join(p['text'] for p in content_by_page) if content_by_page else ""
        method_section = ""
        abstract_text = intro_text = ""

    # 创新声明关键词
    innovation_keywords = [
        "novel", "new", "innovative", "original", "first", "propose", "introduce",
        "develop", "design", "present", "invent", "breakthrough", "advantage"
    ]

    # 方法章节关键词
    method_keywords = [
        "method", "methodology", "approach", "algorithm", "model", "framework",
        "architecture", "network", "framework", "system", "technique"
    ]

    # 如果没有提取到方法章节，尝试从全文中提取
    if not method_section:
        method_patterns = [
            r'(?:3\s+Method|Methodology|Our Method|Proposed Method|Proposed Approach)[\s:：\n](.+?)(?=\n\s*(?:Experiment|4\s+|$))',
            r'(?:第\s*3\s*章)[\s:：\n](.+?)(?=\n\s*(?:第\s*4\s*章|4\s+|$))',
        ]
        for pattern in method_patterns:
            match = re.search(pattern, full_text, re.DOTALL | re.IGNORECASE)
            if match:
                method_section = match.group(0)
                break

    # 重点从引言和方法章节中查找创新声明
    key_sections = intro_text + "\n" + method_section

    # 查找创新声明
    innovation_statements = []
    for keyword in innovation_keywords:
        pattern = rf'[^.!?]*\b{keyword}\b[^.!?]*[.!?]'
        matches = re.findall(pattern, key_sections, re.IGNORECASE)
        innovation_statements.extend([m.strip() for m in matches if len(m.strip()) > 40])

    # 去重
    unique_innovations = list(set(innovation_statements))
    innovations = unique_innovations[:10]

    # 检查每个创新是否在方法部分有对应描述
    for innovation in innovations:
        innovation_lower = innovation.lower()

        # 提取创新中的关键名词（如方法名、模型名）
        potential_names = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', innovation)
        has_method_support = False
        support_details = ""

        if method_section:
            # 检查方法章节是否包含这些名词
            for name in potential_names:
                if len(name) > 3 and name.lower() in method_section.lower():
                    has_method_support = True
                    support_details = f"在方法章节找到 '{name}'"
                    break

            # 检查方法章节是否有详细描述
            if len(method_section) > 200:
                has_method_support = True
                support_details = "方法章节包含详细描述"

        correspondence = {
            'innovation': innovation[:100] + "..." if len(innovation) > 100 else innovation,
            'has_method_support': has_method_support,
            'support_details': support_details if has_method_support else "未在方法章节找到对应描述",
            'status': '✅' if has_method_support else '❌'
        }
        method_correspondence.append(correspondence)

        if not has_method_support:
            issues.append(
                f"❌ 创新声明未在方法部分找到对应描述 / Innovation claim not supported by method section: "
                f"{innovation[:60]}..."
            )

    # 检查是否有增量改进被过度宣传
    incremental_patterns = [
        r'(?:improve|improved|improvement)\s+(?:by|with)\s+\d+[.%]',
        r'boost(?:ed|s)?\s+(?:by|with)?\s*\d+[.%]?',
    ]

    incremental_innovations = []
    for innov in innovations:
        if any(re.search(p, innov, re.IGNORECASE) for p in incremental_patterns):
            # 检查是否承认是增量改进
            if not any(word in innov.lower() for word in ['incremental', 'marginal', 'small', 'modest', 'partial']):
                incremental_innovations.append(innov)

    if incremental_innovations:
        warnings.append(
            f"⚠️ 发现 {len(incremental_innovations)} 处可能存在增量改进被过度宣传为重大创新 / "
            f"Found {len(incremental_innovations)} possible incremental improvements overstated as major innovations"
        )

    # 检查是否清楚说明与baseline的区别
    baseline_diff_keywords = [
        'different from', 'unlike', 'compared to', 'whereas', 'however',
        'baseline', 'existing method', 'previous work', 'traditional',
        '不同于', '相比', '对比', '现有方法', '传统方法'
    ]

    has_baseline_diff = any(
        kw in full_text.lower() for kw in baseline_diff_keywords
    )

    if not has_baseline_diff:
        warnings.append(
            "⚠️ 论文未清楚说明与现有baseline方法的区别 / Paper doesn't clearly explain differences from baseline methods"
        )

    return {
        'innovations': innovations,
        'method_correspondence': method_correspondence,
        'issues': issues,
        'warnings': warnings
    }
