import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import markdown

def convert_md_to_pdf(md_file_path: str) -> str:
    """Convert markdown report to PDF."""
    
    try:
        # Read markdown file
        with open(md_file_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Convert markdown to HTML
        html_content = markdown.markdown(md_content)
        
        # Create PDF
        pdf_path = md_file_path.replace('.md', '.pdf')
        doc = SimpleDocTemplate(pdf_path, pagesize=letter)
        
        # Styles
        styles = getSampleStyleSheet()
        story = []
        
        # Add content
        for line in md_content.split('\n'):
            if line.strip():
                if line.startswith('#'):
                    # Header
                    level = len(line.split()[0])
                    text = line.replace('#', '').strip()
                    style = styles[f'Heading{min(level, 3)}']
                    story.append(Paragraph(text, style))
                    story.append(Spacer(1, 0.2*inch))
                else:
                    # Normal text
                    story.append(Paragraph(line, styles['Normal']))
                    story.append(Spacer(1, 0.1*inch))
        
        doc.build(story)
        print(f"PDF generated: {pdf_path}")
        return pdf_path
        
    except Exception as e:
        print(f"Error converting to PDF: {str(e)}")
        return None

def validate_env_variables() -> bool:
    """Check if required environment variables are set."""
    
    required_vars = ['OPENAI_API_KEY', 'TAVILY_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set them in your .env file")
        return False
    
    return True