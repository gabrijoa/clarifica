# clarifica/core.py

import statistics
from typing import List, Dict, Any

def safe_body_size(text_blocks: List[Dict[str, Any]]) -> int:
    """Calculates the most common font size from a list of text blocks."""
    all_font_sizes = [
        round(s["size"])
        for b in text_blocks
        for l in b.get("lines", [])
        for s in l.get("spans", [])
    ]
    if not all_font_sizes:
        return 12
    try:
        return statistics.mode(all_font_sizes)
    except statistics.StatisticsError:
        return round(statistics.median(all_font_sizes))

def process_line_spans(line_spans: List[Dict[str, Any]]) -> str:
    """Processes spans from a line to handle formatting like superscripts."""
    spans_content = []
    for i, s in enumerate(line_spans):
        span_text = s.get("text", "")
        current_size = round(s.get("size", 0))
        is_citation = False
        if i > 0 and span_text.strip().isdigit():
            j = i - 1
            while j >= 0 and not line_spans[j].get("text", "").strip():
                j -= 1
            if j >= 0:
                previous_span = line_spans[j]
                if not previous_span.get("text", "").strip().isdigit():
                    if current_size < round(previous_span.get("size", 0)):
                        is_citation = True
        if is_citation:
            span_text = f"<sup>{span_text}</sup>"
        spans_content.append(span_text)
    return "".join(spans_content)

def process_page_elements(page_elements: List[Dict[str, Any]], body_font_size: int) -> List[Dict[str, str]]:
    """
    Analyzes a sorted list of elements from a single page and transforms
    them into a structured list of content elements.
    """
    structured_page = []
    for element in page_elements:
        if element.get("type") == 1:  # Image block
            structured_page.append({"type": "image", "path": element.get("path", "")})
            continue

        if element.get("type") == 0:  # Text block
            block_content = []
            block_font_sizes = []
            for l in element.get("lines", []):
                line_spans = l.get("spans", [])
                processed_line = process_line_spans(line_spans)
                block_content.append(processed_line)
                block_font_sizes.extend([round(s.get("size", 0)) for s in line_spans])

            if not any(s.strip() for s in block_content):
                continue
            
            full_block_text = "".join(block_content)
            
            try:
                block_font_size = statistics.mode(block_font_sizes)
            except statistics.StatisticsError:
                block_font_size = body_font_size

            cleaned_text = " ".join(full_block_text.replace("\n", " ").split())
            
            element_type = "paragraph"
            if block_font_size > body_font_size * 1.5:
                element_type = "h1"
            elif block_font_size > body_font_size * 1.2:
                element_type = "h2"
            elif block_font_size < body_font_size * 0.9:
                element_type = "note"
            
            structured_page.append({"type": element_type, "content": cleaned_text})

    return structured_page
