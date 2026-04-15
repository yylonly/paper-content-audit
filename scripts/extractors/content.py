"""内容提取器 - PDF 文本提取，支持中英文

这个模块只负责从PDF中提取原始文本。
语义分析（章节划分、贡献点提取等）由LLMExtractor处理。
"""

import sys
from typing import List, Dict, Optional


class ContentExtractor:
    """提取论文内容 - 纯PDF文本提取，不做语义分析"""

    def __init__(self, pdf_path: str = None, text: str = None):
        self.pdf_path = pdf_path
        self.text_input = text
        self.full_text = ""
        self.total_pages = 0
        self.average_chars = 0
        self.content_by_page = []
        self.extraction_method = None

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
        return pages

    def _extract_from_pdf(self) -> List[Dict]:
        """从PDF提取，优先使用pdfplumber（对中文支持好）"""
        try:
            import pdfplumber
            pages = self._extract_with_pdfplumber()
            if pages and len(pages) > 0:
                self.extraction_method = "pdfplumber"
                print(f"使用 pdfplumber 成功提取 {len(pages)} 页", file=sys.stderr)
                return pages
        except ImportError:
            pass

        try:
            import fitz
            pages = self._extract_with_pymupdf()
            if pages and len(pages) > 0:
                self.extraction_method = "PyMuPDF"
                print(f"使用 PyMuPDF 成功提取 {len(pages)} 页", file=sys.stderr)
                return pages
        except ImportError:
            pass

        try:
            from pypdf import PdfReader
            pages = self._extract_with_pypdf()
            if pages and len(pages) > 0:
                self.extraction_method = "pypdf"
                print(f"使用 pypdf 成功提取 {len(pages)} 页", file=sys.stderr)
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
        """清理文本，移除控制字符"""
        # 只移除控制字符，不做复杂的文本格式化
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            # 移除控制字符
            cleaned = ''.join(char for char in line if ord(char) >= 32 or char in '\n\t')
            cleaned_lines.append(cleaned.strip())
        # 移除空行
        text = '\n'.join(line for line in cleaned_lines if line)
        return text
