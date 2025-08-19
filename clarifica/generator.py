# clarifica/generator.py

from typing import List, Dict, Any
import os
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import gray
from reportlab.lib.enums import TA_JUSTIFY
from PIL import Image as PILImage

# --- As funções de Markdown permanecem para flexibilidade e depuração ---
def generate_markdown_file(structured_doc: List[Dict[str, str]], output_path: str):
    # ... (Esta função permanece a mesma, não é mostrada por brevidade)
    pass

# --- Nova Geração de PDF com Controlo de Canvas ---

def _on_page_draw_images(canvas, doc):
    """
    Função de callback que é chamada para cada página.
    Desenha as imagens para a página atual "no fundo" antes do texto ser renderizado.
    """
    page_number = canvas.getPageNumber() - 1  # Os números de página são baseados em 1
    if page_number < len(doc.page_data):
        page_info = doc.page_data[page_number]
        for img_info in page_info:
            if img_info['type'] == 'image':
                path = img_info.get("path")
                bbox = img_info.get("bbox")
                
                if not (path and bbox and os.path.exists(path)):
                    continue

                try:
                    # Converte as coordenadas do PyMuPDF (origem no topo esquerdo) para as do ReportLab (origem no fundo esquerdo)
                    page_height = doc.height + doc.topMargin + doc.bottomMargin
                    x0, y0, x1, y1 = bbox
                    
                    # A coordenada y do ReportLab é medida a partir do fundo da página
                    rl_y = page_height - y1
                    width = x1 - x0
                    height = y1 - y0
                    
                    canvas.drawImage(path, x0, rl_y, width=width, height=height, preserveAspectRatio=True, anchor='c')
                except Exception as e:
                    print(f"WARNING: Could not draw image {path} on page {page_number + 1}. Reason: {e}")

def generate_pdf(document_by_pages: List[List[Dict[str, Any]]], output_path: str):
    """
    Gera um PDF usando uma abordagem de duas passagens:
    1. As imagens são desenhadas diretamente no canvas da página.
    2. O texto flui para as molduras da página.
    """
    pdf_output_path = os.path.splitext(output_path)[0] + ".pdf"
    doc = BaseDocTemplate(pdf_output_path,
                          rightMargin=inch,
                          leftMargin=inch,
                          topMargin=inch,
                          bottomMargin=inch)

    # Anexa os nossos dados por página ao objeto do documento para que a função onPage os possa aceder
    doc.page_data = document_by_pages

    # Cria uma moldura que cobre a página inteira para o texto fluir
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='normal')
    
    # Cria um PageTemplate que usa a nossa função de desenho personalizada
    template = PageTemplate(id='main_template', frames=[frame], onPage=_on_page_draw_images)
    doc.addPageTemplates([template])

    # A "story" agora conterá apenas os elementos de texto
    story = []
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='H1', fontSize=18, leading=22, spaceAfter=12, fontName='Helvetica-Bold'))
    styles.add(ParagraphStyle(name='H2', fontSize=14, leading=18, spaceAfter=10, fontName='Helvetica-Bold'))
    styles.add(ParagraphStyle(name='Body', fontSize=11, leading=15, fontName='Times-Roman', alignment=TA_JUSTIFY))
    styles.add(ParagraphStyle(name='Note', fontSize=9, leading=12, fontName='Times-Italic', textColor=gray, leftIndent=20))

    # Itera através de cada página e adiciona apenas os elementos de texto à story
    for page_num, page_content in enumerate(document_by_pages):
        for element in page_content:
            el_type = element.get("type")
            if el_type != 'image':
                content = element.get("content", "")
                content = content.replace("<sup>", "<super>").replace("</sup>", "</super>")

                if el_type == "h1":
                    p = Paragraph(content, styles['H1'])
                    story.append(p)
                elif el_type == "h2":
                    p = Paragraph(content, styles['H2'])
                    story.append(p)
                elif el_type == "note":
                    p = Paragraph(content, styles['Note'])
                    story.append(p)
                elif el_type == "paragraph":
                    p = Paragraph(content, styles['Body'])
                    story.append(p)
                    story.append(Spacer(1, 0.1 * inch))
        
        # Adiciona uma quebra de página após processar o texto de cada página
        if page_num < len(document_by_pages) - 1:
            story.append(PageBreak())

    try:
        print("Starting PDF generation with ReportLab (Canvas method)...")
        doc.build(story)
        print(f"Processing complete! PDF file saved to: {pdf_output_path}")
    except Exception as e:
        print(f"ERROR: Could not generate PDF with ReportLab. Reason: {e}")
