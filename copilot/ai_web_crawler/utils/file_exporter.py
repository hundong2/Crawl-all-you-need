"""파일 출력 유틸리티"""
import os
from pathlib import Path
from datetime import datetime
from typing import Optional


class FileExporter:
    """파일 내보내기 클래스"""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def save_markdown(self, content: str, filename: Optional[str] = None) -> str:
        """Markdown 파일 저장"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"crawled_content_{timestamp}.md"
        
        filepath = self.output_dir / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        return str(filepath)
    
    def save_html(self, content: str, filename: Optional[str] = None) -> str:
        """HTML 파일 저장"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"crawled_content_{timestamp}.html"
        
        # Markdown을 HTML로 변환
        try:
            import markdown
            html_content = markdown.markdown(content, extensions=['extra', 'codehilite'])
            
            # HTML 템플릿
            full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>크롤링 결과</title>
    <style>
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
        }}
        code {{
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
        }}
        pre {{
            background-color: #f4f4f4;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        h1, h2, h3 {{ color: #333; }}
        a {{ color: #0066cc; }}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""
            
            filepath = self.output_dir / filename
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(full_html)
            
            return str(filepath)
        except Exception as e:
            raise RuntimeError(f"HTML 변환 실패: {e}")
    
    def save_text(self, content: str, filename: Optional[str] = None) -> str:
        """텍스트 파일 저장"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"crawled_content_{timestamp}.txt"
        
        filepath = self.output_dir / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        return str(filepath)
    
    def convert_to_pdf(self, markdown_path: str) -> str:
        """Markdown을 PDF로 변환 (pypandoc 필요)"""
        try:
            import pypandoc
            
            pdf_path = markdown_path.replace(".md", ".pdf")
            pypandoc.convert_file(
                markdown_path,
                'pdf',
                outputfile=pdf_path,
                extra_args=['--pdf-engine=xelatex']
            )
            
            return pdf_path
        except Exception as e:
            raise RuntimeError(f"PDF 변환 실패: {e}. pandoc 설치 필요")


def create_exporter(output_dir: str = "output") -> FileExporter:
    """파일 내보내기 인스턴스 생성"""
    return FileExporter(output_dir)
