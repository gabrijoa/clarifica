# clarifica/extractor.py
# Versão Final - Nenhuma alteração foi necessária na refatoração.

import pymupdf
import os
from typing import List, Dict, Any, Set

MIN_IMAGE_DIMENSION = 100

def extract_all_text_blocks(doc: pymupdf.Document) -> List[Dict[str, Any]]:
    """Extrai todos os blocos de texto do documento inteiro para pré-análise."""
    all_blocks = []
    for page in doc:
        # Usamos "dict" para obter a estrutura de blocos
        blocks = page.get_text("dict").get("blocks", [])
        # Filtramos para manter apenas blocos de texto (type == 0)
        text_blocks = [b for b in blocks if b.get("type") == 0]
        all_blocks.extend(text_blocks)
    return all_blocks

def extract_text_blocks_from_page(page: pymupdf.Page) -> List[Dict[str, Any]]:
    """Extrai todos os dados brutos de blocos de texto de uma única página."""
    blocks = page.get_text("dict").get("blocks", [])
    return [b for b in blocks if b.get("type") == 0]

def extract_and_save_images_from_page(page: pymupdf.Page, doc: pymupdf.Document, output_folder: str, saved_xrefs: Set[int]) -> List[Dict[str, Any]]:
    """
    Encontra todas as imagens relevantes em uma página, retorna seus metadados e
    salva o arquivo de imagem no disco apenas se for uma imagem nova e única.
    """
    image_info_list = []
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    for img in page.get_images(full=True):
        xref = img[0]
        
        # Extrai os metadados base da imagem
        base_image = doc.extract_image(xref)

        # Filtra imagens pequenas ou irrelevantes
        if not base_image or base_image.get("width", 0) < MIN_IMAGE_DIMENSION or base_image.get("height", 0) < MIN_IMAGE_DIMENSION:
            continue

        # Usa um nome de arquivo consistente e único baseado no xref da imagem
        image_ext = base_image["ext"]
        image_filename = f"image_{xref}.{image_ext}"
        image_path = os.path.join(output_folder, image_filename)

        # Responsabilidade 1: Salvar o arquivo no disco APENAS se for novo
        if xref not in saved_xrefs:
            image_bytes = base_image["image"]
            with open(image_path, "wb") as img_file:
                img_file.write(image_bytes)
            saved_xrefs.add(xref)

        # Responsabilidade 2: SEMPRE retornar os metadados para esta instância da imagem
        img_bbox = page.get_image_bbox(img)
        if img_bbox:
            image_info_list.append({
                "type": 1, # 1 significa um bloco de imagem
                "bbox": img_bbox,
                "path": image_path
            })
            
    return image_info_list