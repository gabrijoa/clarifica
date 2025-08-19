# clarifica/extractor.py

import pymupdf
import os
from typing import List, Dict, Any, Set

MIN_IMAGE_DIMENSION = 100

def extract_all_text_blocks(doc: pymupdf.Document) -> List[Dict[str, Any]]:
    """Extracts all text blocks from the entire document for pre-analysis."""
    all_blocks = []
    for page in doc:
        blocks = page.get_text("dict").get("blocks", [])
        text_blocks = [b for b in blocks if b["type"] == 0]
        all_blocks.extend(text_blocks)
    return all_blocks

def extract_text_blocks_from_page(page: pymupdf.Page) -> List[Dict[str, Any]]:
    """Extracts all raw text block data from a single page."""
    blocks = page.get_text("dict").get("blocks", [])
    return [b for b in blocks if b["type"] == 0]

def extract_and_save_images_from_page(page: pymupdf.Page, doc: pymupdf.Document, output_folder: str, saved_xrefs: Set[int]) -> List[Dict[str, Any]]:
    """
    Finds all relevant images on a page, returns their metadata, and saves
    the image file to disk only if it's a new, unique image.
    """
    image_info_list = []
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    for img in page.get_images(full=True):
        xref = img[0]
        
        base_image = doc.extract_image(xref)

        # First, filter out small, irrelevant images
        if base_image.get("width", 0) < MIN_IMAGE_DIMENSION or base_image.get("height", 0) < MIN_IMAGE_DIMENSION:
            continue

        # Use a consistent, unique filename based on the image's xref ID
        image_ext = base_image["ext"]
        image_filename = f"image_{xref}.{image_ext}"
        image_path = os.path.join(output_folder, image_filename)

        # Responsibility 1: Save the file to disk ONLY if it's new
        if xref not in saved_xrefs:
            image_bytes = base_image["image"]
            with open(image_path, "wb") as img_file:
                img_file.write(image_bytes)
            saved_xrefs.add(xref)

        # Responsibility 2: ALWAYS return the metadata for this image instance
        img_bbox = page.get_image_bbox(img)
        if img_bbox:
            image_info_list.append({
                "type": 1, # 1 signifies an image block
                "bbox": img_bbox,
                "path": image_path
            })
            
    return image_info_list
