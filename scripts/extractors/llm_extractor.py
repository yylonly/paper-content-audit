"""LLM驱动的论文内容提取器

使用大模型提取论文中的：
- 解决的问题 (Problem Solved)
- 创新点 (Innovation Points)
- 评估内容 (Evaluation Content)
- Baseline对比
- 实验完整性

不再使用正则表达式，而是通过LLM理解论文语义结构。
"""

import json
import sys
from typing import Dict, List, Optional


class LLMExtractor:
    """使用LLM提取论文关键内容"""

    def __init__(self, api_key: str = None, model: str = "claude-sonnet-4-20250514"):
        self.api_key = api_key
        self.model = model
        self.extracted_data = {}

    def extract_all(self, paper_text: str, paper_title: str = "") -> Dict:
        """
        使用LLM提取论文的所有关键信息

        Args:
            paper_text: 论文全文文本
            paper_title: 论文标题（可选）

        Returns:
            Dict: 包含 extracted_problems, extracted_innovations, extracted_evaluation 等
        """
        self.extracted_data = {
            'paper_title': paper_title,
            'extracted_problems': [],
            'extracted_innovations': [],
            'extracted_evaluation': {},
            'extracted_baselines': [],
            'extracted_experiments': [],
            'extracted_contributions': [],
        }

        # 分段提取以避免超出token限制
        if len(paper_text) > 50000:
            # 对长论文进行分段处理
            sections = self._split_paper_sections(paper_text)
            for section_name, section_text in sections.items():
                self._extract_from_section(section_name, section_text)
        else:
            self._extract_from_full_text(paper_text)

        return self.extracted_data

    def _split_paper_sections(self, paper_text: str) -> Dict[str, str]:
        """将论文分成多个部分以便处理"""
        lines = paper_text.split('\n')
        sections = {
            'abstract': '',
            'introduction': '',
            'method': '',
            'experiment': '',
            'conclusion': '',
            'other': ''
        }

        current_section = 'other'
        section_keywords = {
            'abstract': ['摘要', 'abstract'],
            'introduction': ['1.', '第一章', '引言', 'introduction', '1 '],
            'method': ['2.', '第二章', '方法', 'method', 'methodology', '3.', '第三章'],
            'experiment': ['4.', '第四章', '实验', 'experiment', 'evaluation', 'results', '5.', '第五章'],
            'conclusion': ['6.', '第六章', '总结', 'conclusion', 'conclusions', '展望', 'future work'],
        }

        for line in lines:
            line_lower = line.lower().strip()
            for section_name, keywords in section_keywords.items():
                if any(kw.lower() in line_lower for kw in keywords):
                    if line.strip().endswith(tuple(str(i) + '.' for i in range(1, 10))) or \
                       '第' in line and '章' in line:
                        current_section = section_name
                        break

            if len(line.strip()) > 10:
                sections[current_section] += line + '\n'

        return sections

    def _extract_from_section(self, section_name: str, section_text: str):
        """从单个章节提取信息"""
        if len(section_text) < 100:
            return

        if section_name == 'abstract':
            self._extract_from_abstract(section_text)
        elif section_name == 'introduction':
            self._extract_contributions_from_text(section_text)
        elif section_name == 'method':
            self._extract_innovations_from_text(section_text)
        elif section_name == 'experiment':
            self._extract_evaluation_from_text(section_text)

    def _extract_from_full_text(self, paper_text: str):
        """从完整文本提取信息（用于较短的论文）"""
        # 构建提示词让LLM提取
        prompt = self._build_extraction_prompt(paper_text)

        # 调用LLM API
        result = self._call_llm(prompt)

        if result:
            self._parse_llm_response(result)

    def _build_extraction_prompt(self, paper_text: str) -> str:
        """构建提取提示词"""
        return f"""你是一篇学术论文的内容分析专家。请仔细阅读以下论文内容，提取关键信息。

论文内容：
---
{paper_text[:40000]}  # 限制长度避免超出限制
---

请以JSON格式输出以下信息：

{{
    "paper_title": "论文标题（从内容中识别）",
    "problem_solved": [
        {{
            "problem": "具体解决的问题描述",
            "context": "问题背景或动机",
            "location": "在论文中出现的位置（摘要/引言/方法等）"
        }}
    ],
    "contributions": [
        {{
            "contribution": "主要贡献点描述",
            "type": "原创性/增量改进/整合",
            "evidence": "在论文中的具体表述"
        }}
    ],
    "innovations": [
        {{
            "innovation": "创新点描述",
            "method_section": "对应的方法章节描述",
            "novelty_type": "理论创新/方法创新/应用创新"
        }}
    ],
    "evaluation": {{
        "datasets": ["使用的数据集名称"],
        "metrics": ["使用的评估指标，如 accuracy, F1等"],
        "main_results": "主要实验结果概述",
        "baseline_methods": ["对比的baseline方法名称"],
        "statistical_significance": "是否有统计显著性分析（是/否）",
        "ablation_study": "是否有消融实验（是/否）"
    }},
    "experiments": [
        {{
            "type": "实验类型（主实验/消融实验/敏感性分析等）",
            "description": "实验描述",
            "findings": "主要发现"
        }}
    ],
    "strengths": ["论文的优点列表"],
    "weaknesses": ["论文的不足或改进建议列表"]
}}

请确保输出是合法的JSON格式，不要包含其他文字。"""

    def _call_llm(self, prompt: str) -> Optional[str]:
        """调用LLM API"""
        try:
            # 尝试使用Claude API
            import anthropic
        except ImportError:
            try:
                from anthropic import Anthropic
            except ImportError:
                print("错误: 需要安装 anthropic 库来使用LLM提取功能", file=sys.stderr)
                print("请运行: pip install anthropic", file=sys.stderr)
                return None

        api_key = self.api_key
        if not api_key:
            # 尝试从环境变量获取
            import os
            api_key = os.environ.get('ANTHROPIC_API_KEY')

        if not api_key:
            print("警告: 未设置ANTHROPIC_API_KEY环境变量，LLM提取功能不可用", file=sys.stderr)
            print("将使用简化的文本分析代替。", file=sys.stderr)
            return None

        try:
            client = Anthropic(api_key=api_key)
            response = client.messages.create(
                model=self.model,
                max_tokens=4096,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            return response.content[0].text
        except Exception as e:
            print(f"LLM API调用失败: {e}", file=sys.stderr)
            return None

    def _parse_llm_response(self, response: str):
        """解析LLM返回的JSON响应"""
        try:
            # 提取JSON部分
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                data = json.loads(json_str)

                self.extracted_data['paper_title'] = data.get('paper_title', '')
                self.extracted_data['extracted_problems'] = data.get('problem_solved', [])
                self.extracted_data['extracted_contributions'] = data.get('contributions', [])
                self.extracted_data['extracted_innovations'] = data.get('innovations', [])
                self.extracted_data['extracted_evaluation'] = data.get('evaluation', {})
                self.extracted_data['extracted_experiments'] = data.get('experiments', [])
                self.extracted_data['strengths'] = data.get('strengths', [])
                self.extracted_data['weaknesses'] = data.get('weaknesses', [])

        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}", file=sys.stderr)
            # 使用备用方案
            self._fallback_extraction(response)

    def _fallback_extraction(self, text: str):
        """备用提取方案（当LLM返回格式错误时）"""
        # 从文本中按行提取关键信息
        lines = text.split('\n')
        current_section = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 简单关键词检测
            lower = line.lower()
            if any(k in lower for k in ['problem', '问题', '挑战']):
                if len(line) > 20:
                    self.extracted_data['extracted_problems'].append({
                        'problem': line[:200],
                        'context': '',
                        'location': '待确认'
                    })
            elif any(k in lower for k in ['innovation', '创新', 'novel']):
                if len(line) > 20:
                    self.extracted_data['extracted_innovations'].append({
                        'innovation': line[:200],
                        'method_section': '',
                        'novelty_type': '待确认'
                    })

    def _extract_from_abstract(self, abstract_text: str):
        """从摘要提取关键信息"""
        prompt = f"""从以下论文摘要中提取关键信息：

摘要内容：
---
{abstract_text}
---

请以JSON格式输出：

{{
    "problem_solved": ["解决的问题描述"],
    "main_contributions": ["主要贡献点"],
    "methods_used": ["使用的方法"],
    "evaluation_summary": "评估结果概述"
}}

输出JSON："""

        result = self._call_llm(prompt)
        if result:
            self._parse_llm_response(result)

    def _extract_contributions_from_text(self, text: str):
        """从文本提取贡献点"""
        prompt = f"""从以下论文引言/方法章节中提取主要贡献和创新点：

内容：
---
{text[:15000]}
---

请以JSON格式输出：

{{
    "contributions": [
        {{
            "contribution": "贡献描述",
            "type": "原创性/增量改进/应用创新",
            "location": "出现位置"
        }}
    ],
    "innovations": [
        {{
            "innovation": "创新点描述",
            "section": "对应章节",
            "novelty_type": "理论/方法/应用"
        }}
    ]
}}

输出JSON："""

        result = self._call_llm(prompt)
        if result:
            try:
                json_start = result.find('{')
                json_end = result.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    data = json.loads(result[json_start:json_end])
                    if 'contributions' in data:
                        self.extracted_data['extracted_contributions'].extend(data['contributions'])
                    if 'innovations' in data:
                        self.extracted_data['extracted_innovations'].extend(data['innovations'])
            except:
                pass

    def _extract_innovations_from_text(self, text: str):
        """从方法章节提取创新点"""
        prompt = f"""从以下论文方法章节中提取创新点和对应的方法描述：

内容：
---
{text[:15000]}
---

请以JSON格式输出：

{{
    "innovations": [
        {{
            "innovation": "创新点描述",
            "method_description": "对应的方法描述",
            "novelty_type": "理论创新/方法创新/应用创新"
        }}
    ]
}}

输出JSON："""

        result = self._call_llm(prompt)
        if result:
            try:
                json_start = result.find('{')
                json_end = result.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    data = json.loads(result[json_start:json_end])
                    if 'innovations' in data:
                        self.extracted_data['extracted_innovations'].extend(data['innovations'])
            except:
                pass

    def _extract_evaluation_from_text(self, text: str):
        """从实验章节提取评估内容"""
        prompt = f"""从以下论文实验章节中提取评估详情：

内容：
---
{text[:15000]}
---

请以JSON格式输出：

{{
    "evaluation": {{
        "datasets": ["数据集名称"],
        "metrics": ["评估指标"],
        "baseline_methods": ["对比的baseline方法"],
        "main_results": "主要结果概述",
        "statistical_significance": "是/否",
        "ablation_study": "是/否",
        "sensitivity_analysis": "是/否"
    }},
    "experiments": [
        {{
            "type": "实验类型",
            "description": "实验描述",
            "findings": "主要发现"
        }}
    ]
}}

输出JSON："""

        result = self._call_llm(prompt)
        if result:
            try:
                json_start = result.find('{')
                json_end = result.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    data = json.loads(result[json_start:json_end])
                    if 'evaluation' in data:
                        self.extracted_data['extracted_evaluation'] = data['evaluation']
                    if 'experiments' in data:
                        self.extracted_data['extracted_experiments'] = data['experiments']
            except:
                pass

    def get_problems(self) -> List[Dict]:
        """获取提取的问题"""
        return self.extracted_data.get('extracted_problems', [])

    def get_innovations(self) -> List[Dict]:
        """获取提取的创新点"""
        return self.extracted_data.get('extracted_innovations', [])

    def get_evaluation(self) -> Dict:
        """获取提取的评估内容"""
        return self.extracted_data.get('extracted_evaluation', {})

    def get_contributions(self) -> List[Dict]:
        """获取提取的贡献点"""
        return self.extracted_data.get('extracted_contributions', [])

    def get_experiments(self) -> List[Dict]:
        """获取提取的实验"""
        return self.extracted_data.get('extracted_experiments', [])

    def get_full_data(self) -> Dict:
        """获取完整的提取数据"""
        return self.extracted_data


def extract_with_llm(paper_text: str, paper_title: str = "", api_key: str = None) -> Dict:
    """
    便捷函数：使用LLM提取论文关键信息

    Args:
        paper_text: 论文全文文本
        paper_title: 论文标题
        api_key: Anthropic API密钥（可选，从环境变量ANTHROPIC_API_KEY读取）

    Returns:
        Dict: 包含所有提取的信息
    """
    extractor = LLMExtractor(api_key=api_key)
    return extractor.extract_all(paper_text, paper_title)
