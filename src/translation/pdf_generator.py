import re
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image, HRFlowable
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_RIGHT, TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib import colors

# --- 1. INTERNATIONAL STANDARD FONT REGISTRATION ---
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    FONT_DIR = os.path.join(project_root, "config", "fonts")
    
    # Path validation for NotoSans (Your specific project fonts)
    REGULAR_PATH = os.path.join(FONT_DIR, 'NotoSans-Regular.ttf')
    BOLD_PATH = os.path.join(FONT_DIR, 'NotoSans-Bold.ttf')

    if os.path.exists(REGULAR_PATH) and os.path.exists(BOLD_PATH):
        # We register NotoSans as 'Standard' and 'Standard-Bold' for internal use
        pdfmetrics.registerFont(TTFont('NotoSans', REGULAR_PATH))
        pdfmetrics.registerFont(TTFont('NotoSans-Bold', BOLD_PATH))
        
        DEFAULT_FONT = "NotoSans"
        DEFAULT_FONT_BOLD = "NotoSans-Bold"
        print(f"✅ Professional Typography Locked: NotoSans registered.")
    else:
        raise FileNotFoundError(f"NotoSans font files missing in {FONT_DIR}")

except Exception as e:
    print(f"⚠️ TYPOGRAPHY WARNING: Falling back to Helvetica. Error: {e}")
    DEFAULT_FONT = "Helvetica"
    DEFAULT_FONT_BOLD = "Helvetica-Bold"

# --- 2. ADVANCED TEXT SANITIZATION ---
def clean_markdown_for_pdf(text: str) -> str:
    """
    Cleans Markdown syntax and Unicode characters to meet International PDF standards.
    """
    if not text: return ""
    
    # Handle Unicode characters that crash PDF engines
    replacements = {
        '\u2013': '-', '\u2014': '-', # En/Em dashes
        '\u2018': "'", '\u2019': "'", # Smart quotes
        '\u201c': '"', '\u201d': '"', # Smart double quotes
        '\u2022': '•', '\u2026': '...', # Bullets and Ellipsis
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)

    # Convert Markdown Bold (**text**) to PDF Bold (<b>text</b>)
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    # Convert Markdown Italics (*text*) to PDF Italics (<i>text</i>)
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
    
    return text

# --- 3. PROFESSIONAL HEADER, FOOTER & WATERMARK ---
def add_background_elements(canvas, doc, title, language):
    canvas.saveState()
    w, h = doc.width, doc.height
    is_rtl = language in ['ar', 'he', 'fa', 'ur']
    
    # A. Header Branding
    canvas.setStrokeColor(colors.HexColor('#1E88E5'))
    canvas.setLineWidth(0.5)
    canvas.line(doc.leftMargin, h + doc.topMargin + 0.2*inch, w + doc.leftMargin, h + doc.topMargin + 0.2*inch)

    canvas.setFont(DEFAULT_FONT, 8)
    canvas.setFillColor(colors.grey)
    brand_tag = "AUTORESEARCH CREW PRO | 2025"
    if is_rtl:
        canvas.drawString(doc.leftMargin, h + doc.topMargin + 0.3*inch, brand_tag)
    else:
        canvas.drawRightString(w + doc.leftMargin, h + doc.topMargin + 0.3*inch, brand_tag)

    # B. Footer Page Numbers
    canvas.setFont(DEFAULT_FONT, 9)
    page_num = f"Internal Release: {title[:40]}... | Page {doc.page}"
    if is_rtl:
        canvas.drawString(doc.leftMargin, 0.5 * inch, page_num)
    else:
        canvas.drawRightString(w + doc.leftMargin, 0.5 * inch, page_num)
    
    canvas.restoreState()

# --- 4. MAIN PDF GENERATOR ---
def generate_multilingual_pdf(content: str, output_path: str, title: str, language: str = 'en') -> str:
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            leftMargin=0.9*inch, rightMargin=0.9*inch,
            topMargin=1.2*inch, bottomMargin=1.2*inch
        )
        
        is_rtl = language in ['ar', 'he', 'fa', 'ur']
        
        # Define Professional Styles using NotoSans
        styles = {
            'Title': ParagraphStyle('Title', fontName=DEFAULT_FONT_BOLD, fontSize=28, 
                                    textColor=colors.HexColor('#0D47A1'), alignment=TA_CENTER, 
                                    spaceAfter=30, leading=34),
            'Meta': ParagraphStyle('Meta', fontName=DEFAULT_FONT, fontSize=11, 
                                   textColor=colors.HexColor('#546E7A'), alignment=TA_CENTER, spaceAfter=6),
            'h1': ParagraphStyle('h1', fontName=DEFAULT_FONT_BOLD, fontSize=20, 
                                 textColor=colors.HexColor('#1565C0'), spaceBefore=20, spaceAfter=10, 
                                 alignment=TA_RIGHT if is_rtl else TA_LEFT, leading=24),
            'h2': ParagraphStyle('h2', fontName=DEFAULT_FONT_BOLD, fontSize=15, 
                                 textColor=colors.HexColor('#37474F'), spaceBefore=16, spaceAfter=8, 
                                 alignment=TA_RIGHT if is_rtl else TA_LEFT, leading=18),
            'Body': ParagraphStyle('Body', fontName=DEFAULT_FONT, fontSize=10.5, leading=15, 
                                   alignment=TA_RIGHT if is_rtl else TA_JUSTIFY, spaceAfter=12),
            'Bullet': ParagraphStyle('Bullet', fontName=DEFAULT_FONT, fontSize=10.5, leading=15, 
                                     leftIndent=20, bulletIndent=10, spaceAfter=8,
                                     alignment=TA_RIGHT if is_rtl else TA_LEFT)
        }

        story = []
        
        # --- PAGE 1: INTERNATIONAL COVER PAGE ---
        story.append(Spacer(1, 2.5*inch))
        story.append(Paragraph("AutoResearch Crew Pro", styles['Meta']))
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph(clean_markdown_for_pdf(title.upper()), styles['Title']))
        story.append(HRFlowable(width="40%", thickness=1.5, color=colors.HexColor('#1E88E5'), spaceAfter=20))
        story.append(Paragraph("STRATEGIC INTELLIGENCE REPORT", styles['Meta']))
        story.append(Spacer(1, 1.5*inch))
        story.append(Paragraph(f"<b>Generation Date:</b> {datetime.now().strftime('%B %d, %Y')}", styles['Meta']))
        story.append(Paragraph(f"<b>Standard:</b> ISO-2025-AI-COMPLIANT", styles['Meta']))
        story.append(Paragraph(f"<b>Language:</b> {language.upper()}", styles['Meta']))
        story.append(PageBreak())

        # --- CONTENT PROCESSING ---
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                story.append(Spacer(1, 0.1*inch))
                continue
            
            # Sanitize and apply bold/italic logic
            clean_line = clean_markdown_for_pdf(line)
            
            if line.startswith('# '):
                story.append(Paragraph(clean_line[2:], styles['h1']))
            elif line.startswith('## '):
                story.append(Paragraph(clean_line[3:], styles['h2']))
            elif line.startswith('### '):
                story.append(Paragraph(clean_line[4:], styles['h2']))
            elif line.startswith(('* ', '- ', '• ')):
                # Auto-remove bullet chars from text since Paragraph handle it
                bullet_text = clean_line[2:]
                story.append(Paragraph(bullet_text, styles['Bullet'], bulletText='•'))
            else:
                story.append(Paragraph(clean_line, styles['Body']))

        # Build final document with dynamic backgrounds
        doc.build(story, 
                  onFirstPage=lambda c, d: add_background_elements(c, d, title, language),
                  onLaterPages=lambda c, d: add_background_elements(c, d, title, language))
        
        return output_path

    except Exception as e:
        print(f"❌ PDF Critical Failure: {e}")
        return None