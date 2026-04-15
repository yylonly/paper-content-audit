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

        # 将文本按段落分割
        pages = [{
            'page': 1,
            'text': self.text_input,
            'chars': len(self.text_input)
        }]
        self.content_by_page = pages
        return pages

    def _extract_from_pdf(self) -> List[Dict]:
        """从PDF提取，尝试多种库"""
        # 尝试不同的PDF提取库
        extraction_methods = [
            ("pdfplumber", self._extract_with_pdfplumber),
            ("PyMuPDF", self._extract_with_pymupdf),
            ("pypdf", self._extract_with_pypdf),
        ]

        for method_name, extractor_func in extraction_methods:
            try:
                pages = extractor_func()
                if pages and len(pages) > 0:
                    # 检查提取质量
                    total_chars = sum(p['chars'] for p in pages)
                    if total_chars > 100:  # 确保提取到足够内容
                        self.extraction_method = method_name
                        print(f"使用 {method_name} 成功提取 {len(pages)} 页", file=sys.stderr)
                        return pages
            except Exception as e:
                print(f"{method_name} 提取失败: {e}", file=sys.stderr)
                continue

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
        import fitz  # PyMuPDF

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
        # 只移除多余的空格，但保留换行符
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            # 移除行内多余空格
            line = re.sub(r'\s+', ' ', line)
            # 移除特殊控制字符
            line = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f]', '', line)
            cleaned_lines.append(line.strip())
        # 用换行符连接，移除空行
        text = '\n'.join(line for line in cleaned_lines if line)
        return text

    def extract_section(self, section_name: str) -> str:
        """提取指定章节内容"""
        if not self.full_text:
            return ""

        # 常见的章节标题模式
        patterns = [
            rf'{section_name}[\s:：]*\n(.+?)(?=\n[A-Z][a-z]+\s+\d|$\n\n|\n\d+\.)',
            rf'{section_name}[\s:：]*\n(.+?)(?=\nReferences|\nBibliography|\n\n\d+\.)',
        ]

        for pattern in patterns:
            match = re.search(pattern, self.full_text, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return ""

    def extract_abstract(self) -> str:
        """提取摘要"""
        return self.extract_section("Abstract")

    def extract_introduction(self) -> str:
        """提取引言"""
        return self.extract_section("Introduction")

    def extract_conclusion(self) -> str:
        """提取结论"""
        return self.extract_section("Conclusion")
