# clarifica/generator.py
# Versão Final - Responsável pela estilização e geração do PDF.

from typing import List, Any, Dict
import os

# Imports do ReportLab
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import gray
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4

# --- REGISTRO DE FONTES CUSTOMIZADAS ---
# (Esta parte permanece a mesma, você pode adicionar suas fontes aqui)
try:
    # Exemplo: pdfmetrics.registerFont(TTFont('MinhaFonte', 'fonts/MinhaFonte.ttf'))
    CUSTOM_FONTS_LOADED = True
except Exception as e:
    print(f"AVISO: Fontes customizadas não puderam ser carregadas. Usando fontes padrão. Erro: {e}")
    CUSTOM_FONTS_LOADED = False

def get_pdf_styles() -> Dict[str, ParagraphStyle]:
    """
    Cria e retorna um dicionário com todos os estilos de parágrafo para o PDF.
    Funciona como o "guia de estilo" do nosso documento.
    """
    styles = getSampleStyleSheet()
    
    # Define as fontes a serem usadas (padrão ou customizadas)
    body_font = 'Times-Roman' # Substitua por sua fonte se carregada
    heading_font = 'Helvetica-Bold' # Substitua por sua fonte se carregada
    
    # Título Principal (H1)
    styles.add(ParagraphStyle(name='H1', fontName=heading_font, fontSize=20, leading=24, spaceAfter=14))
    
    # Subtítulo (H2)
    styles.add(ParagraphStyle(name='H2', fontName=heading_font, fontSize=16, leading=20, spaceAfter=12))
    
    # Corpo de Texto (Body)
    styles.add(ParagraphStyle(name='Body', fontName=body_font, fontSize=12, leading=16, alignment=TA_JUSTIFY, spaceAfter=8))
    
    # Notas / Citações (Note)
    note_font = 'Times-Italic' # Substitua por sua fonte se carregada
    styles.add(ParagraphStyle(name='Note', fontName=note_font, fontSize=10, leading=14, textColor=gray, leftIndent=20, spaceAfter=6))
    
    return styles

def generate_pdf(story: List[Any], output_path: str):
    """
    Gera um PDF padrão A4 a partir de uma lista (story) de Flowables pré-construídos.
    """
    pdf_output_path = os.path.splitext(output_path)[0] + ".pdf"
    
    doc = SimpleDocTemplate(
        pdf_output_path,
        pagesize=A4,
        rightMargin=inch,
        leftMargin=inch,
        topMargin=inch,
        bottomMargin=inch
    )

    try:
        print("Fase 3: Gerando o PDF final...")
        doc.build(story)
        print(f"Processamento completo! Arquivo salvo em: {pdf_output_path}")
    except Exception as e:
        print(f"ERRO: Não foi possível gerar o PDF com ReportLab. Razão: {e}")