# clarifica/generator.py

from typing import List, Dict
import os
import pypandoc

def _build_markdown_string(structured_doc: List[Dict[str, str]], output_path: str, use_absolute_paths: bool = False) -> str:
    """
    Internal helper to build a Markdown string from the structured document.
    Can use either relative or absolute paths for images.
    """
    markdown_content = []
    output_dir = os.path.dirname(output_path)
    
    for element in structured_doc:
        el_type = element.get("type")
        
        if el_type in ["h1", "h2", "note", "paragraph"]:
            content = element.get("content", "")
            if el_type == "h1":
                markdown_content.append(f"# {content}\n")
            elif el_type == "h2":
                markdown_content.append(f"## {content}\n")
            elif el_type == "note":
                markdown_content.append(f"> *{content}*\n")
            elif el_type == "paragraph":
                markdown_content.append(f"{content}\n")
        
        elif el_type == "image":
            image_path = element.get("path", "")
            if image_path:
                if use_absolute_paths:
                    # Use the full, unambiguous path for Pandoc PDF generation
                    markdown_image_path = os.path.abspath(image_path).replace("\\", "/")
                else:
                    # Use a relative path for portable Markdown files
                    relative_image_path = os.path.relpath(image_path, output_dir)
                    markdown_image_path = relative_image_path.replace("\\", "/")
                
                markdown_content.append(f"![Image]({markdown_image_path})\n")

    return "\n".join(markdown_content)

def generate_markdown_file(structured_doc: List[Dict[str, str]], output_path: str):
    """
    Generates a Markdown file using relative image paths for portability.
    """
    full_markdown = _build_markdown_string(structured_doc, output_path, use_absolute_paths=False)
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(full_markdown)
        print(f"Processing complete! Markdown file saved to: {output_path}")
    except Exception as e:
        print(f"ERROR: Could not save the .md file. Reason: {e}")

def generate_pdf(structured_doc: List[Dict[str, str]], output_path: str):
    """
    Generates a PDF file using absolute image paths to ensure Pandoc finds them.
    """
    pdf_output_path = os.path.splitext(output_path)[0] + ".pdf"
    
    # --- FIX: We now tell the builder to use absolute paths for PDF generation ---
    markdown_string = _build_markdown_string(structured_doc, pdf_output_path, use_absolute_paths=True)
    
    try:
        print("Starting PDF generation with Pandoc...")
        pypandoc.convert_text(
            markdown_string,
            to='pdf',
            format='md',
            outputfile=pdf_output_path,
            extra_args=['--pdf-engine=xelatex']
        )
        print(f"Processing complete! PDF file saved to: {pdf_output_path}")
    except Exception as e:
        print(f"ERROR: Could not generate PDF. Is Pandoc and LaTeX installed? Reason: {e}")
