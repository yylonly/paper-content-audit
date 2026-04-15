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

    # 优先从引言(1.4.2 主要创新点)和结论(6.2 主要创新点)中提取编号贡献点
    innovation_section = intro_text + "\n" + conclusion_text

    # 提取"主要创新点"之后的内容
    innovation_section_match = re.search(
        r'本文的主要创新点概括如下[.\n]*(.*?)(?=\n\s*(?:1\.5|论文结构|本章小结|\n\d+\s+第一章|$))',
        innovation_section,
        re.DOTALL
    )

    # 如果找到 innovation section，直接使用其贡献
    found_innovation_section = False
    if innovation_section_match:
        innovation_section = innovation_section_match.group(1)
        found_innovation_section = True
        # 提取编号贡献点
        numbered_matches = re.findall(r'[（(]\d+[）)]\s*([^\n]{10,300}?)[。\n]', innovation_section)
        if numbered_matches:
            contribution_sentences.extend([m.strip() for m in numbered_matches if len(m.strip()) > 10])

        # "其一"、"其二"、"其三"、"其四"格式的贡献 - 中文论文
        yiqi_patterns = [
            r'其[一二三四五六七八九十]+[、\s]+([^其\n]{20,300}?)[。\n]',
        ]
        for pattern in yiqi_patterns:
            matches = re.findall(pattern, innovation_section)
            contribution_sentences.extend([m.strip() for m in matches if len(m.strip()) > 15])

    # Bullet point (•) 格式的贡献 - 支持跨行匹配 (英文论文)
    # 这个提取逻辑应该在if块外执行，因为无论中文还是英文论文都可能使用bullet格式
    bullet_patterns = [
        # 匹配 bullet + 内容（可能跨多行直到下一个bullet或空行）
        r'[•\-\*]\s*([^\n]+(?:\n(?!\s*[•\-\*])[^\n]*)*)',
    ]
    for pattern in bullet_patterns:
        matches = re.findall(pattern, innovation_section, re.MULTILINE)
        # 清理每条匹配：合并多行，移除换行符
        for m in matches:
            cleaned = ' '.join(m.split('\n')).strip()
            if len(cleaned) > 15:
                contribution_sentences.append(cleaned)

    # 如果没有找到贡献点，继续使用其他方法...
    if found_innovation_section and contribution_sentences:
        # 去重并清理
        unique_contributions = list(set(contribution_sentences))
        contribution_sentences = [c for c in unique_contributions if len(c) >= 15][:10]
        # 直接返回
        return {
            'contributions': contribution_sentences,
            'issues': [],
            'warnings': []
        }

    # 继续使用其他提取方法...
    for keyword in contribution_keywords_en:
        pattern = rf'[^.!?]*\b{keyword}\b[^.!?]*[.!?]'
        matches = re.findall(pattern, key_sections, re.IGNORECASE)
        contribution_sentences.extend(matches)

    # 中文关键词 - 在关键章节中查找
    for keyword in contribution_keywords_cn:
        pattern = rf'[^。！？]*[{re.escape(keyword)}][^。！？]*[。！？]?'
        matches = re.findall(pattern, key_sections)
        contribution_sentences.extend(matches)

    # 编号贡献点模式
    numbered_patterns = [
        r'[（(]\d+[）)]\s*([^\n]{10,300}?)[。\n]',
    ]
    for pattern in numbered_patterns:
        matches = re.findall(pattern, innovation_section)
        contribution_sentences.extend([m.strip() for m in matches if len(m.strip()) > 15])

    # "第一，" "第二，"格式的贡献
    first_second_patterns = [
        r'第[一二三四五六七八九十]+[、，]\s*([^\n]{20,300}?)[。\n]',
    ]
    for pattern in first_second_patterns:
        matches = re.findall(pattern, innovation_section)
        contribution_sentences.extend([m.strip() for m in matches if len(m.strip()) > 15])

    # 尝试从摘要中提取贡献点列表
    list_patterns = [
        r'[（(]\d+[）)]\s*(.+?)[。；;]',
        r'\d+[.、]\s*(.+?)[。；;]',
    ]
    for pattern in list_patterns:
        matches = re.findall(pattern, abstract_text)
        contribution_sentences.extend(matches)

    # English contribution patterns
    english_contribution_patterns = [
        r'(?:First|Secondly|Second)[,\s]+([^.!?]+[!.?])',
        r'(?:Third)[,\s]+([^.!?]+[!.?])',
        r'(?:Finally|Lastly|Last)[,\s]+([^.!?]+[!.?])',
    ]
    for pattern in english_contribution_patterns:
        matches = re.findall(pattern, abstract_text, re.IGNORECASE)
        contribution_sentences.extend(matches)

    # Structured contribution patterns in intro/conclusion
    structured_patterns = [
        r'本文[提出|贡献|主要]*(.+?)[。]',
        r'我们[提出|方法|贡献]*(.+?)[。]',
        r'创新点[：:]\s*(.+?)[。]',
        r'主要[贡献|创新]?[：:]\s*(.+?)[。]',
    ]
    for pattern in structured_patterns:
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

    # "其一"、"其二"等格式在摘要中
    yiqi_patterns = [
        r'其[一二三四五六七八九十]+[、]\s*([^其。]{20,200}?)[。]',
    ]
    for pattern in yiqi_patterns:
        matches = re.findall(pattern, abstract_text)
        contribution_sentences.extend([m.strip() for m in matches if len(m.strip()) > 15])

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
