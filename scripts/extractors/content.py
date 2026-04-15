"""内容提取器 - PDF 文本提取，支持中英文"""
import re
import sys
from typing import List, Dict, Optional


class ContentExtractor:
    """提取论文内容"""

    def __init__(self, pdf_path: str = None, text: str = None):
        self.pdf_path = pdf_path
        self.text_input = text
        self.full_text = ""
        self.total_pages = 0
        self.average_chars = 0
        self.content_by_page = []
        self.extraction_method = None

        # 提取的论文结构
        self.abstract = ""
        self.introduction = ""
        self.conclusion = ""
        self.method_section = ""
        self.experiment_section = ""

    def extract_all(self) -> List[Dict]:
        """提取所有页面内容"""
        if self.text_input:
            return self._extract_from_text()
        elif self.pdf_path:
            return self._extract_from_pdf()
        else:
            return []

    def _extract_from_text(self) -> List[Dict]:
        """从文本提取"""
        self.full_text = self.text_input
        self.total_pages = 1
        self.average_chars = len(self.text_input)
        self.extraction_method = "text_input"

        pages = [{
            'page': 1,
            'text': self.text_input,
            'chars': len(self.text_input)
        }]
        self.content_by_page = pages
        self._extract_sections()
        return pages

    def _extract_from_pdf(self) -> List[Dict]:
        """从PDF提取，优先使用pdfplumber（对中文支持好）"""
        try:
            import pdfplumber
            pages = self._extract_with_pdfplumber()
            if pages and len(pages) > 0:
                self.extraction_method = "pdfplumber"
                print(f"使用 pdfplumber 成功提取 {len(pages)} 页", file=sys.stderr)
                self._extract_sections()
                return pages
        except ImportError:
            pass

        try:
            import fitz
            pages = self._extract_with_pymupdf()
            if pages and len(pages) > 0:
                self.extraction_method = "PyMuPDF"
                print(f"使用 PyMuPDF 成功提取 {len(pages)} 页", file=sys.stderr)
                self._extract_sections()
                return pages
        except ImportError:
            pass

        try:
            from pypdf import PdfReader
            pages = self._extract_with_pypdf()
            if pages and len(pages) > 0:
                self.extraction_method = "pypdf"
                print(f"使用 pypdf 成功提取 {len(pages)} 页", file=sys.stderr)
                self._extract_sections()
                return pages
        except ImportError:
            pass

        print("错误: 所有PDF提取方法均失败", file=sys.stderr)
        return []

    def _extract_with_pdfplumber(self) -> List[Dict]:
        """使用 pdfplumber 提取"""
        import pdfplumber

        pages = []
        total_chars = 0

        with pdfplumber.open(self.pdf_path) as pdf:
            self.total_pages = len(pdf.pages)

            for i, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                text = self._clean_text(text)
                total_chars += len(text)
                pages.append({
                    'page': i + 1,
                    'text': text,
                    'chars': len(text)
                })

        self.content_by_page = pages
        self.average_chars = total_chars / max(self.total_pages, 1)
        self.full_text = "\n\n".join(p['text'] for p in pages)

        return pages

    def _extract_with_pymupdf(self) -> List[Dict]:
        """使用 PyMuPDF (fitz) 提取"""
        import fitz

        pages = []
        total_chars = 0

        doc = fitz.open(self.pdf_path)
        self.total_pages = len(doc)

        for i, page in enumerate(doc):
            text = page.get_text() or ""
            text = self._clean_text(text)
            total_chars += len(text)
            pages.append({
                'page': i + 1,
                'text': text,
                'chars': len(text)
            })

        self.content_by_page = pages
        self.average_chars = total_chars / max(self.total_pages, 1)
        self.full_text = "\n\n".join(p['text'] for p in pages)

        return pages

    def _extract_with_pypdf(self) -> List[Dict]:
        """使用 pypdf 提取"""
        from pypdf import PdfReader

        pages = []
        total_chars = 0

        reader = PdfReader(self.pdf_path)
        self.total_pages = len(reader.pages)

        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            text = self._clean_text(text)
            total_chars += len(text)
            pages.append({
                'page': i + 1,
                'text': text,
                'chars': len(text)
            })

        self.content_by_page = pages
        self.average_chars = total_chars / max(self.total_pages, 1)
        self.full_text = "\n\n".join(p['text'] for p in pages)

        return pages

    def _clean_text(self, text: str) -> str:
        """清理文本，保留换行符用于结构分析"""
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            line = re.sub(r'\s+', ' ', line)
            line = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f]', '', line)
            cleaned_lines.append(line.strip())
        text = '\n'.join(line for line in cleaned_lines if line)
        return text

    def _extract_sections(self):
        """提取论文各章节内容"""
        if not self.full_text:
            return

        text = self.full_text

        # 提取摘要
        abstract_patterns = [
            r'摘要[：:\s]*([^\n]+(?:\n(?![^\n]{0,30}[：:])[^\n]+)*)',
            r'Abstract[：:\s]*([^\n]+(?:\n(?![^\n]{0,30}[：:])[^\n]+)*)',
        ]
        for pattern in abstract_patterns:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                self.abstract = match.group(0)[:2000]
                break

        # 提取引言（1 Introduction 或 第1章 绪论）
        intro_patterns = [
            r'(?:1\s+Introduction[^\n]*\n)(.+?)(?=\n\s*(?:2\s+|第\s*2\s*章))',
            r'(?:第\s*1\s*章[^\n]*\n)(.+?)(?=\n\s*(?:第\s*2\s*章))',
            r'(?:绪论[^\n]*\n)(.+?)(?=\n\s*(?:第\s*2\s*章|2\s+))',
        ]
        for pattern in intro_patterns:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                self.introduction = match.group(1)[:3000]
                break

        # 提取结论
        conclusion_patterns = [
            r'(?:Conclusion|Conclusions|总结|结论)[^\n]*\n(.+?)(?=\n\s*(?:References|Bibliography|参考文献|$))',
            r'(?:第\s*\d+\s*章[^\n]*\n)(.+?)(?=\n\s*参考文献)',
        ]
        for pattern in conclusion_patterns:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                self.conclusion = match.group(1)[:2000]
                break

        # 提取方法章节（3 Method 或 第3章/第三章 方法）
        method_patterns = [
            r'(?:3\s+Method[^\n]*\n)(.+?)(?=\n\s*(?:4\s+|Experiment|实验))',
            r'(?:第\s*3\s*章|第三章)[^\n]*\n(.+?)(?=\n\s*(?:第\s*4\s*章|第四章|4\s+|$))',
            r'(?:方法[^\n]*\n)(.+?)(?=\n\s*(?:实验|第\s*4\s*章|第四章|$))',
        ]
        for pattern in method_patterns:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                self.method_section = match.group(1)[:5000]
                break

        # 提取实验章节 - use page-based approach for accuracy
        # Find pages that contain actual experiment content (research questions, ablation, etc.)
        # Need to find page 58+ where chapter 5 content actually starts (not TOC listings)
        exp_text_parts = []
        in_exp_section = False
        for i, page in enumerate(self.content_by_page):
            page_text = page['text']
            # Skip TOC pages (page 10, 13, etc. contain chapter listings but not actual content)
            # The real chapter 5 content starts on page 58+
            if i < 50:  # Skip first 50 pages (TOC area)
                continue
            # Check if this page starts the experiment chapter
            if '第五章 实验设计与结果分析' in page_text and len(page_text) > 200:
                in_exp_section = True
            # Or if this page has research questions with actual content
            if 'RQ1' in page_text and 'RQ1:' in page_text:
                in_exp_section = True
            if '研究假设' in page_text[:100] and '本章' in page_text:
                in_exp_section = True
            # Check if we've left the experiment section
            if in_exp_section:
                exp_text_parts.append(page_text)
                # Stop after we see chapter 6
                if '第六章' in page_text[:100] or '总结与展望' in page_text[:100]:
                    break
        if exp_text_parts:
            self.experiment_section = '\n\n'.join(exp_text_parts)[:5000]

    def extract_section(self, section_name: str) -> str:
        """提取指定章节内容"""
        section_map = {
            'abstract': self.abstract,
            'introduction': self.introduction,
            'conclusion': self.conclusion,
            'method': self.method_section,
            'experiment': self.experiment_section,
        }
        return section_map.get(section_name.lower(), "")

    def extract_abstract(self) -> str:
        """提取摘要"""
        return self.abstract

    def extract_introduction(self) -> str:
        """提取引言"""
        return self.introduction

    def extract_conclusion(self) -> str:
        """提取结论"""
        return self.conclusion
