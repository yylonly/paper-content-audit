"""贡献点提取与分析"""
import re
from typing import List, Dict


def check_contributions(content_by_page: List[Dict], full_text: str = "") -> Dict:
    """
    检查论文的主要贡献（中英文支持）

    Returns:
        Dict with keys: contributions, issues, warnings
    """
    contributions = []
    issues = []
    warnings = []

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

    # 从全文中提取贡献语句
    text = full_text if full_text else "\n\n".join(p['text'] for p in content_by_page)

    # 提取引言和结论中的贡献声明
    intro_pattern = r'1?\s*Introduction.*?(?=\s*2\s+[A-Z]|\s*Background|\s*Preliminaries|\s*Related\s+Work)'
    conclusion_pattern = r'(Conclusion|Conclusions|5?\s*Conclusion|总结|结论).*'

    intro_match = re.search(intro_pattern, text, re.DOTALL | re.IGNORECASE)
    conclusion_match = re.search(conclusion_pattern, text, re.DOTALL | re.IGNORECASE)

    intro_text = intro_match.group(0) if intro_match else ""
    conclusion_text = conclusion_match.group(0) if conclusion_match else ""

    # 在摘要中查找贡献
    abstract_pattern = r'Abstract[:：]?\s*(.+?)(?=\n\s*(Keywords|Introduction|1\.)|$)'
    abstract_match = re.search(abstract_pattern, text, re.DOTALL | re.IGNORECASE)
    abstract_text = abstract_match.group(1) if abstract_match else ""

    # 查找所有贡献语句
    contribution_sentences = []

    # 英文关键词
    for keyword in contribution_keywords_en:
        pattern = rf'[^.!?]*\b{keyword}\b[^.!?]*[.!?]'
        matches = re.findall(pattern, text, re.IGNORECASE)
        contribution_sentences.extend(matches)

    # 中文关键词 - 使用更宽松的匹配
    for keyword in contribution_keywords_cn:
        # 匹配包含关键词的行或句子
        pattern = rf'[^。！？]*[{re.escape(keyword)}][^。！？]*[。！？]?'
        matches = re.findall(pattern, text)
        contribution_sentences.extend(matches)

    # 尝试从摘要中提取贡献点列表
    # 常见模式：(1) ... (2) ... (3) ... 或 1. ... 2. ... 3. ...
    list_patterns = [
        r'[（(]\d+[）)]\s*(.+?)[。；;]',
        r'\d+[.、]\s*(.+?)[。；;]',
        r'(?:第一|第二|第三|首先|其次|最后)[^。]*[。]',
    ]
    for pattern in list_patterns:
        matches = re.findall(pattern, text)
        contribution_sentences.extend(matches)

    # 去重并清理
    unique_contributions = list(set(contribution_sentences))
    contributions = [c.strip() for c in unique_contributions if len(c.strip()) > 15][:10]

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
