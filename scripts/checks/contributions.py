"""贡献点提取与分析"""
import re
from typing import List, Dict


def check_contributions(content_by_page: List[Dict], sections: Dict = None) -> Dict:
    """
    检查论文的主要贡献（中英文支持）

    Args:
        content_by_page: 页面内容列表
        sections: 章节内容字典，包含 abstract, introduction, conclusion, method, experiment, full_text

    Returns:
        Dict with keys: contributions, issues, warnings
    """
    contributions = []
    issues = []
    warnings = []

    # 获取各部分文本
    if sections and isinstance(sections, dict):
        abstract_text = sections.get('abstract', '')
        intro_text = sections.get('introduction', '')
        conclusion_text = sections.get('conclusion', '')
        method_text = sections.get('method', '')
        full_text = sections.get('full_text', '')
        if not full_text:
            full_text = "\n\n".join(p['text'] for p in content_by_page) if content_by_page else ""
    else:
        full_text = sections if isinstance(sections, str) else "\n\n".join(p['text'] for p in content_by_page) if content_by_page else ""
        abstract_text = intro_text = conclusion_text = method_text = ""

    # 提取贡献声明的关键词 - 中英文
    contribution_keywords_en = [
        "we propose", "we present", "we introduce", "we develop",
        "we propose a", "we present a", "we introduce a", "we develop a",
        "this paper proposes", "this paper presents", "this paper introduces",
        "this paper develops", "the main contribution",
        "our contributions are", "our main contributions",
        "we make the following contributions",
        "key contributions", "major contributions"
    ]

    contribution_keywords_cn = [
        "本文提出", "本文贡献", "本文方法", "本文主要",
        "我们提出", "我们贡献", "我们方法",
        "主要贡献", "核心贡献", "创新点",
        "提出一种", "提出一种新的", "提出了一种",
        "本文的贡献", "本文的主要工作"
    ]

    # 重点从摘要、引言、结论中提取
    key_sections = abstract_text + "\n" + intro_text + "\n" + conclusion_text

    # 查找所有贡献语句
    contribution_sentences = []

    # 英文关键词 - 在关键章节中查找
    for keyword in contribution_keywords_en:
        pattern = rf'[^.!?]*\b{keyword}\b[^.!?]*[.!?]'
        matches = re.findall(pattern, key_sections, re.IGNORECASE)
        contribution_sentences.extend(matches)

    # 中文关键词 - 在关键章节中查找
    for keyword in contribution_keywords_cn:
        pattern = rf'[^。！？]*[{re.escape(keyword)}][^。！？]*[。！？]?'
        matches = re.findall(pattern, key_sections)
        contribution_sentences.extend(matches)

    # 尝试从摘要中提取贡献点列表 (1) ... (2) ... (3) ...
    list_patterns = [
        r'[（(]\d+[）)]\s*(.+?)[。；;]',
        r'\d+[.、]\s*(.+?)[。；;]',
    ]
    for pattern in list_patterns:
        matches = re.findall(pattern, abstract_text)
        contribution_sentences.extend(matches)

    # English contribution patterns: First, ... Second, ... Third, ... Finally, ...
    english_contribution_patterns = [
        r'(?:First|Secondly|Second)[,\s]+([^.!?]+[!.?])',
        r'(?:Third)[,\s]+([^.!?]+[!.?])',
        r'(?:Finally|Lastly|Last)[,\s]+([^.!?]+[!.?])',
        r'(?:First|Secondly|Second|Third|Finally)[,\s]+([^.!?]+?(?=\n\s*(?:Second|Third|Finally|$)))',
    ]
    for pattern in english_contribution_patterns:
        matches = re.findall(pattern, abstract_text, re.IGNORECASE)
        contribution_sentences.extend(matches)

    # Also look for structured contribution patterns in intro/conclusion
    structured_patterns = [
        r'本文[提出|贡献|主要]*(.+?)[。]',
        r'我们[提出|方法|贡献]*(.+?)[。]',
        r'创新点[：:]\s*(.+?)[。]',
        r'主要[贡献|创新]?[：:]\s*(.+?)[。]',
    ]
    for pattern in structured_patterns:
        matches = re.findall(pattern, key_sections)
        contribution_sentences.extend(matches)

    # 去重并清理
    unique_contributions = list(set(contribution_sentences))

    # 过滤掉太短或者太长的，以及包含噪音关键词的
    noise_keywords = ['中图分类号', '论文编号', 'copyright', '©', 'permission', 'reserved', '表5', '表4', '表3', '北京航空航天大学']
    contributions = []
    for c in unique_contributions:
        c_clean = c.strip()
        # 跳过包含噪音关键词的
        if any(kw in c_clean.lower() for kw in noise_keywords):
            continue
        # 跳过太短或太长的
        if len(c_clean) < 20 or len(c_clean) > 300:
            continue
        # 跳过包含表格数据的（数字过多）
        if len(re.findall(r'\d+\.\d+|\d+/\d+', c_clean)) > 5:
            continue
        contributions.append(c_clean)

    contributions = contributions[:10]

    # 评估贡献质量
    if not contributions:
        issues.append("❌ 未找到明确的贡献声明 / No clear contribution statement found")
    else:
        # 检查贡献是否具体
        vague_contributions = []
        vague_en = ["improve performance", "better results", "outperform", "achieve good",
                    "state-of-the-art", "significantly", "substantially"]
        vague_cn = ["提高性能", "更好效果", "优于", "取得好", "显著", "大幅提升"]

        for c in contributions:
            c_lower = c.lower()
            has_vague = any(v in c_lower for v in vague_en) or any(v in c for v in vague_cn)
            if has_vague:
                # 检查是否有具体说明
                if not re.search(r'\d+[.%]|\d+x|compared to|baseline|method|相比|对比|提高|降低', c, re.IGNORECASE):
                    vague_contributions.append(c)

        if vague_contributions:
            warnings.append(
                f"⚠️ 部分贡献声明缺乏具体数据支撑 / Some contribution statements lack specific metrics: "
                f"发现 {len(vague_contributions)} 条模糊声明"
            )

        # 检查是否说明了与现有工作的区别
        comparative_en = ['different from', 'unlike', 'compared', 'baseline', 'previous', 'existing', 'traditional']
        comparative_cn = ['不同于', '相比', '对比', '现有方法', '传统方法', '已有方法']
        comparative_contributions = [c for c in contributions if
            any(word in c.lower() for word in comparative_en) or any(word in c for word in comparative_cn)]
        if len(comparative_contributions) < len(contributions) / 2:
            warnings.append(
                "⚠️ 多数贡献未说明与现有方法的区别 / Most contributions don't explain differences from existing methods"
            )

    return {
        'contributions': contributions,
        'issues': issues,
        'warnings': warnings
    }
