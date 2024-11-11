from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.style import WD_STYLE_TYPE

class ResumeFormatter:
    """Professional resume formatting"""
    
    @staticmethod
    def format_docx(doc: Document, content: str) -> Document:
        """Format resume content in Word document"""
        # Set professional styles
        styles = doc.styles
        style = styles.add_style('ResumeHeading', WD_STYLE_TYPE.PARAGRAPH)
        style.font.size = Pt(14)
        style.font.bold = True
        style.font.color.rgb = RGBColor(0x2F, 0x5A, 0x8B)
        
        # Format content
        sections = content.split('\n\n')
        for section in sections:
            paragraph = doc.add_paragraph(section)
            paragraph.style = 'ResumeHeading'
            
        return doc