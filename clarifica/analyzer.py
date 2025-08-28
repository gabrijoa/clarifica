# clarifica/analyzer.py

import pymupdf
import statistics
from typing import List, Dict, Any, Set
from collections import Counter

# --- Funções Principais de Análise ---

def analyze_document(doc: pymupdf.Document) -> Dict[str, Any]:
    """
    Realiza uma análise global em todo o documento PDF para extrair
    características estruturais e de layout.
    """
    print("Iniciando Fase 1: Análise Global do Documento...")
    page_count = len(doc)

    # 1. Coletar metadados de texto para análise de fonte
    all_text_spans = _collect_all_text_spans(doc)
    
    # 2. Coletar metadados de posição de TODOS os elementos para análise de repetição
    all_element_bboxes = _collect_all_element_bboxes(doc)

    # 3. Realizar análises estatísticas sobre os metadados coletados
    body_font_size = _find_body_font_size(all_text_spans)
    repeating_elements = _find_repeating_elements(all_element_bboxes, page_count)

    print(f"Análise concluída. Fonte principal: {body_font_size:.2f}pt. Elementos repetitivos encontrados: {len(repeating_elements)}")

    # 4. Montar e retornar o "mapa do documento"
    document_map = {
        "body_font_size": body_font_size,
        "repeating_elements_bbboxes": repeating_elements
    }

    return document_map


def _collect_all_element_bboxes(doc: pymupdf.Document) -> List[tuple[float, float, float, float]]:
    """
    Percorre o documento para coletar os bounding boxes de todos os
    elementos: blocos de texto, imagens e desenhos.
    """
    all_bboxes = []
    for page in doc:
        # Extrai bboxes de blocos de texto
        text_blocks = page.get_text("blocks") # (x0, y0, x1, y1, "text", block_no, block_type)
        for block in text_blocks:
            all_bboxes.append(block[:4]) # Adiciona apenas a tupla (x0, y0, x1, y1)

        # Extrai bboxes de imagens
        for img in page.get_images(full=True):
            bbox = page.get_image_bbox(img)
            if bbox:
                all_bboxes.append(bbox)

        # Extrai bboxes de desenhos vetoriais
        drawings = page.get_drawings()
        for path in drawings:
            all_bboxes.append(path['rect']) # 'rect' é o bbox do desenho

    return all_bboxes

def _collect_all_text_spans(doc: pymupdf.Document) -> List[Dict[str, Any]]:
    """
    Percorre todo o documento para coletar os metadados de cada span de texto.

    Um "span" é o menor pedaço de texto com formatação uniforme (mesma fonte,
    tamanho, cor, etc.).

    Returns:
        Uma lista de dicionários, onde cada dicionário representa um span.
    """
    all_spans = []
    for page in doc:
        # Usamos 'rawdict' para obter o máximo de detalhes
        page_dict = page.get_text("rawdict")
        
        # Navegamos na estrutura aninhada: block -> line -> span
        for block in page_dict.get("blocks", []):
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    # Para manter nossa estrutura de dados limpa, criamos um
                    # novo dicionário apenas com as informações que nos interessam.
                    clean_span = {
                        "text": span.get("text"),
                        "size": round(span.get("size"), 2), # Arredondar para normalizar
                        "font": span.get("font"),
                        "bbox": span.get("bbox")
                    }
                    all_spans.append(clean_span)
    
    return all_spans

def _find_body_font_size(text_spans: List[Dict[str, Any]]) -> float:
    """
    Calcula o tamanho de fonte mais comum (moda) a partir de uma lista de spans.
    Se não houver uma moda única, retorna a mediana como uma estimativa robusta.

    Args:
        text_spans: A lista de todos os dicionários de span do documento.

    Returns:
        Um float representando o tamanho de fonte do corpo de texto principal.
    """
    # Caso extremo: se não houver texto no documento, retornamos um padrão razoável.
    if not text_spans:
        return 12.0

    # Criamos uma lista apenas com os tamanhos de fonte de cada span.
    sizes = [span["size"] for span in text_spans]

    try:
        # A melhor medida é a moda (o valor que mais se repete).
        return statistics.mode(sizes)
    except statistics.StatisticsError:
        # Se a moda falhar (ex: [10, 10, 12, 12]), não há um único valor mais
        # comum. A mediana (valor do meio) é uma alternativa muito mais
        # estável que a média, pois não é afetada por títulos gigantes.
        return statistics.median(sizes)

def _find_repeating_elements(all_bboxes: List[tuple], page_count: int, threshold: float = 0.8) -> Set[tuple[int, int, int, int]]:
    """
    Identifica "assinaturas" de elementos (baseadas em seus bboxes arredondados)
    que se repetem consistentemente ao longo do documento.

    Args:
        all_bboxes: Uma lista de todos os bboxes de elementos no documento.
        page_count: O número total de páginas no documento.
        threshold: A porcentagem de páginas em que um elemento deve aparecer
                   para ser considerado repetitivo (padrão: 80%).

    Returns:
        Um conjunto de "assinaturas" de bbox dos elementos repetitivos.
    """
    if not all_bboxes:
        return set()

    # 1. Criar assinaturas arredondando as coordenadas do bbox.
    #    Isso agrupa elementos que estão em posições ligeiramente diferentes.
    signatures = [tuple(round(coord) for coord in bbox) for bbox in all_bboxes]

    # 2. Contar a frequência de cada assinatura.
    bbox_counts = Counter(signatures)

    # 3. Determinar o limiar de repetição.
    repetition_limit = int(page_count * threshold)
    if repetition_limit < 2: # Um elemento deve aparecer em pelo menos 2 páginas
        repetition_limit = 2

    # 4. Criar um conjunto (set) com as assinaturas que excedem o limiar.
    repeating_elements = {
        signature for signature, count in bbox_counts.items()
        if count >= repetition_limit
    }

    return repeating_elements