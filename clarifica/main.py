# clarifica/main.py

import os
import pymupdf
from . import extractor
from . import core
from . import generator

# --- CONFIGURATION ---
INPUT_FOLDER = "input_docs"
OUTPUT_FOLDER = "output_docs"
FILE_NAME = "puer_aeternus.pdf"
OUTPUT_FORMAT = "pdf"

def main():
    """
    Orquestra o fluxo de trabalho do PDF, processando o documento página por página.
    """
    # 1. Configuração de caminhos
    input_file_path = os.path.join(INPUT_FOLDER, FILE_NAME)
    output_filename_base = os.path.splitext(FILE_NAME)[0]
    output_file_path = os.path.join(OUTPUT_FOLDER, f"{output_filename_base}.{OUTPUT_FORMAT}")
    image_output_folder = os.path.join(OUTPUT_FOLDER, "images")

    if not os.path.exists(input_file_path):
        print(f"ERROR: Input file not found at '{input_file_path}'")
        return
    
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    try:
        doc = pymupdf.open(input_file_path)
    except Exception as e:
        print(f"ERROR: Failed to open PDF file. Reason: {e}")
        return

    # --- Pré-Análise ---
    print("--- Analyzing font sizes across document ---")
    all_text_blocks = extractor.extract_all_text_blocks(doc)
    body_font_size = core.safe_body_size(all_text_blocks)
    print(f"Identified body text font size: {body_font_size}")

    # --- Loop de Processamento Principal: Página por Página ---
    document_by_pages = []
    saved_image_xrefs = set()

    print(f"--- Processing {len(doc)} pages ---")
    for page in doc:
        page_text_blocks = extractor.extract_text_blocks_from_page(page)
        page_image_blocks = extractor.extract_and_save_images_from_page(
            page, doc, image_output_folder, saved_image_xrefs
        )
        
        page_elements = page_text_blocks + page_image_blocks
        page_elements.sort(key=lambda el: el.get('bbox', (0, 0, 0, 0))[1])

        structured_page_content = core.process_page_elements(page_elements, body_font_size)
        
        # Adiciona a lista de elementos desta página à estrutura do documento principal
        document_by_pages.append(structured_page_content)

    doc.close()

    # --- Etapa de Geração ---
    print(f"--- Starting Generation (Format: {OUTPUT_FORMAT.upper()}) ---")
    if OUTPUT_FORMAT.lower() == "pdf":
        generator.generate_pdf(document_by_pages, output_file_path)
    else:
        # A geração de Markdown precisaria de ser ajustada para lidar com a nova estrutura de dados
        print("Markdown generation is not fully supported with the new page-by-page structure yet.")

if __name__ == "__main__":
    main()
