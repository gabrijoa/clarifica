# clarifica/main.py

import os
import pymupdf

# Importa nossos módulos especialistas
from . import analyzer
from . import builder
from . import generator
from . import extractor

# Imports para cálculo de dimensões
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch

# --- CONFIGURATION ---
INPUT_FOLDER = "input_docs"
OUTPUT_FOLDER = "output_docs"
# Coloque o nome do arquivo que você quer processar aqui
FILE_NAME = "puer_aeternus.pdf" 
OUTPUT_FORMAT = "pdf"

def main():
    """
    Orquestra o fluxo de trabalho de refatoração de PDF em três fases:
    1. Análise: Entende a estrutura do documento.
    2. Construção: Reconstrói o conteúdo de forma limpa.
    3. Geração: Gera o PDF final.
    """
    # --- SETUP INICIAL ---
    input_file_path = os.path.join(INPUT_FOLDER, FILE_NAME)
    output_filename_base = os.path.splitext(FILE_NAME)[0]
    output_file_path = os.path.join(OUTPUT_FOLDER, f"{output_filename_base}_refatorado.{OUTPUT_FORMAT}")
    image_output_folder = os.path.join(OUTPUT_FOLDER, "images")

    if not os.path.exists(input_file_path):
        print(f"ERRO: Arquivo de entrada não encontrado em '{input_file_path}'")
        return
    
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
    if not os.path.exists(image_output_folder):
        os.makedirs(image_output_folder)

    try:
        doc = pymupdf.open(input_file_path)
    except Exception as e:
        print(f"ERRO: Falha ao abrir o arquivo PDF. Razão: {e}")
        return

    # --- FASE 1: ANÁLISE GLOBAL ---
    # O analyzer inspeciona o documento inteiro e nos devolve um
    # "mapa" com a inteligência necessária para a reconstrução.
    document_map = analyzer.analyze_document(doc)

    # --- SETUP PARA GERAÇÃO ---
    # Pegamos os estilos e as dimensões da página para passar ao builder.
    styles = generator.get_pdf_styles()
    page_width, page_height = A4
    margin = 1 * inch
    frame_width = page_width - (2 * margin)
    frame_height = page_height - (2 * margin)
    frame_padding = 12 
    usable_frame_width = frame_width - frame_padding
    usable_frame_height = frame_height - frame_padding

    # --- FASE 2: RECONSTRUÇÃO GUIADA ---
    print(f"Fase 2: Reconstruindo o conteúdo de {len(doc)} páginas...")
    full_story = []
    saved_image_xrefs = set() # Controla imagens já salvas no disco

    for page in doc:
        # O builder usa o mapa do analyzer para tomar decisões inteligentes
        # sobre quais elementos incluir e como estilizá-los.
        page_flowables = builder.build_page_story(
            page=page,
            doc=doc,
            image_folder=image_output_folder,
            saved_image_xrefs=saved_image_xrefs,
            document_map=document_map,
            styles=styles,
            frame_width=usable_frame_width,
            frame_height=usable_frame_height
        )
        full_story.extend(page_flowables)
    
    print("Reconstrução concluída.")
    doc.close()

    # --- FASE 3: GERAÇÃO ---
    # O generator pega a 'story' limpa e simplesmente a renderiza no PDF final.
    generator.generate_pdf(full_story, output_file_path)

if __name__ == "__main__":
    main()