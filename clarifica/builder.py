# clarifica/builder.py

import pymupdf
import statistics
import os
from typing import List, Dict, Any, Tuple, Set
from html import escape

# Imports do ReportLab
from reportlab.platypus import Paragraph, Image, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch

# Precisaremos do nosso extrator para obter os dados brutos da página
from . import extractor

# --- Função Principal de Construção ---

def build_page_story(
    page: pymupdf.Page,
    doc: pymupdf.Document, # Necessário para extrair dados da imagem
    image_folder: str, # Pasta para salvar/ler imagens
    saved_image_xrefs: Set[int], # Para não salvar imagens repetidas
    document_map: Dict[str, Any],
    styles: Dict[str, ParagraphStyle],
    frame_width: float,
    frame_height: float
) -> List[Any]:
    """
    Constrói uma lista de Flowables para uma única página, usando o mapa do documento
    para filtrar elementos repetitivos e classificar o conteúdo.
    """
    page_flowables = []

    # 1. Extrair todos os elementos da página (texto e imagens)
    #    Usaremos as funções do nosso módulo extrator.
    text_blocks = extractor.extract_text_blocks_from_page(page)
    image_blocks = extractor.extract_and_save_images_from_page(page, doc, image_folder, saved_image_xrefs)
    
    all_elements = text_blocks + image_blocks
    
    # 2. Ordenar os elementos de cima para baixo para garantir a ordem de leitura.
    all_elements.sort(key=lambda el: el.get('bbox', (0, 0, 0, 0))[1])

    # 3. Iterar sobre cada elemento e aplicar a lógica de construção.
    for element in all_elements:
        # Etapa A: Filtrar elementos de layout repetitivos
        element_bbox = element.get("bbox")
        if not element_bbox:
            continue

        element_signature = _create_signature_from_bbox(element_bbox)
        if element_signature in document_map["repeating_elements_bbboxes"]:
            continue # Pula este elemento, pois é um cabeçalho/rodapé/borda

        # Etapa B: Classificar e construir o Flowable
        
        # Se for uma IMAGEM...
        # Se for uma IMAGEM...
        if element.get("type") == 1: # Usamos o tipo definido no extractor
            img_path = element.get("path")
            if img_path and os.path.exists(img_path):
                try:
                    img = Image(img_path)
                    img_width, img_height = img.imageWidth, img.imageHeight

                    if img_width > 0 and img_height > 0:
                        # Lógica de redimensionamento robusta
                        ratio_w = frame_width / img_width
                        ratio_h = frame_height / img_height
                        scale_ratio = min(ratio_w, ratio_h)
                        
                        img.drawWidth = img_width * scale_ratio
                        img.drawHeight = img_height * scale_ratio
                        
                        page_flowables.append(img)
                        # Adiciona um pequeno espaço vertical após cada imagem
                        page_flowables.append(Spacer(1, 0.2 * inch))

                except Exception as e:
                    print(f"AVISO: Não foi possível processar a imagem {img_path}. Razão: {e}")
        elif element.get("type") == 0:
                # --- INÍCIO DO CÓDIGO QUE ESTAVA FALTANDO ---
                # 1. Juntar o texto de todos os spans do bloco em uma única string
                full_text = ""
                for line in element.get("lines", []):
                    for span in line.get("spans", []):
                        full_text += span.get("text", "")
                    # Adicionamos um espaço no final de cada linha para evitar
                    # que palavras de linhas diferentes se colem.
                    full_text += " "
                # --- FIM DO CÓDIGO QUE ESTAVA FALTANDO ---

                cleaned_text = " ".join(full_text.split())
                if not cleaned_text:
                    continue

                # "Escapamos" o texto para neutralizar caracteres como '<' e '>'
                escaped_text = escape(cleaned_text)

                # 2. Chamar nosso classificador para obter o nome do estilo
                style_name = _classify_text_block(element, document_map["body_font_size"])

                # 3. Obter o objeto de estilo do dicionário
                style = styles[style_name]

                # 4. Criar e adicionar o parágrafo, usando o texto escapado
                p = Paragraph(escaped_text, style)
                page_flowables.append(p)

    return page_flowables


# --- Funções Auxiliares (Implementação Interna) ---

def _create_signature_from_bbox(bbox: Tuple[float, float, float, float]) -> Tuple[int, int, int, int]:
    """
    Cria uma assinatura única a partir de um bbox, arredondando suas coordenadas.
    Esta função DEVE ser idêntica à usada no analyzer.py para consistência.
    """
    return tuple(round(coord) for coord in bbox)

def _classify_text_block(block: Dict[str, Any], body_font_size: float) -> str:
    """
    Analisa um bloco de texto e o classifica como 'H1', 'H2', 'Body', ou 'Note'
    com base no tamanho de sua fonte em relação ao corpo de texto principal.
    """
    # Se o bloco não tiver linhas ou spans, é um parágrafo normal.
    if not block.get("lines"):
        return "Body"

    # Coleta os tamanhos de fonte de todos os spans dentro do bloco
    span_sizes = [
        round(span.get("size", body_font_size), 2)
        for line in block.get("lines", [])
        for span in line.get("spans", [])
    ]
    if not span_sizes:
        return "Body"

    # Encontra o tamanho de fonte mais comum dentro do bloco
    try:
        block_font_size = statistics.mode(span_sizes)
    except statistics.StatisticsError:
        block_font_size = statistics.median(span_sizes)

    # Aplica as regras de classificação
    if block_font_size > body_font_size * 1.5:
        return "H1"
    if block_font_size > body_font_size * 1.2:
        return "H2"
    if block_font_size < body_font_size * 0.9:
        return "Note"
    
    return "Body"