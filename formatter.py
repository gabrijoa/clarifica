# Step 1: Import necessary libraries
import pymupdf  # Using the official library name as requested
import os
import statistics

# --- CONFIGURATION ---
# Path to the folder containing input documents
INPUT_FOLDER = "input_docs"
# Path to the folder where output documents will be saved
OUTPUT_FOLDER = "output_docs"
# Name of the file to be processed
FILE_NAME = "puer_aeternus.pdf"  # <-- CHANGE THIS TO YOUR PDF FILE NAME

# --- MAIN LOGIC ---

def analyze_and_structure_text():
    """
    Main function that reads a PDF, analyzes its structure based on font sizes,
    and saves it as a structured Markdown (.md) file.
    """
    # Ensure the output folder exists
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    # Construct full paths for input and output files
    input_file_path = os.path.join(INPUT_FOLDER, FILE_NAME)
    output_filename = FILE_NAME.replace(".pdf", ".md") # Output will be Markdown
    output_file_path = os.path.join(OUTPUT_FOLDER, output_filename)

    if not os.path.exists(input_file_path):
        print(f"ERROR: The file '{input_file_path}' was not found.")
        return

    print(f"Starting to process file: {FILE_NAME}")

    try:
        doc = pymupdf.open(input_file_path)
    except Exception as e:
        print(f"ERROR: Failed to process the PDF file. Reason: {e}")
        return

    # --- STEP 2: EXTRACT STRUCTURED TEXT AND IDENTIFY BODY FONT SIZE ---
    
    all_font_sizes = []
    # First pass: iterate through pages to find the most common font size (body text)
    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if b["type"] == 0:  # 0 indicates a text block
                for l in b["lines"]:
                    for s in l["spans"]:
                        all_font_sizes.append(round(s["size"]))
    
    if not all_font_sizes:
        print("ERROR: No text found in the document.")
        return
        
    # The mode is the most frequently occurring value, likely our body text size
    body_font_size = statistics.mode(all_font_sizes)
    print(f"Identified body text font size: {body_font_size}")

    # --- STEP 3: REBUILD THE DOCUMENT WITH HIERARCHY ---

    structured_text = ""
    for page in doc:
        # This time, we extract text block by block to analyze it
        blocks = page.get_text("blocks")
        for b in blocks:
            # We only care about text blocks (type 0)
            if b[6] == 0:
                # b[4] contains the text of the block
                block_text = b[4]
                
                # Heuristic to find the font size of this block
                # We open the page again to get detailed span info for this block
                page_dict = page.get_text("dict")
                span_size = body_font_size # Default to body size
                # This is a bit complex, but we need to find the specific span for this block text
                # For simplicity, we'll just check the first span of the first line of the block
                try:
                    first_line = page.get_text("dict")['blocks'][blocks.index(b)]['lines'][0]['spans'][0]
                    span_size = round(first_line['size'])
                except (IndexError, KeyError):
                    pass # Ignore blocks without text or spans

                # Clean up the text within the block
                cleaned_block_text = block_text.replace("-\n", "").replace("\n", " ").strip()
                cleaned_block_text = " ".join(cleaned_block_text.split())

                # Simple heuristic: if font size is > 1.5x body, it's a main header (H1)
                # If it's > 1.2x body, it's a sub-header (H2)
                if span_size > body_font_size * 1.5:
                    structured_text += f"# {cleaned_block_text}\n\n"
                elif span_size > body_font_size * 1.2:
                    structured_text += f"## {cleaned_block_text}\n\n"
                else:
                    # Otherwise, it's a normal paragraph
                    structured_text += f"{cleaned_block_text}\n\n"

    # --- STEP 4: SAVE THE STRUCTURED MARKDOWN FILE ---
    try:
        with open(output_file_path, "w", encoding="utf-8") as f_out:
            f_out.write(structured_text)
        print(f"Processing complete! Structured text saved to: {output_file_path}")
    except Exception as e:
        print(f"ERROR: Could not save the output file. Reason: {e}")

    doc.close()

# This ensures the main function runs only when the script is executed directly
if __name__ == "__main__":
    analyze_and_structure_text()
