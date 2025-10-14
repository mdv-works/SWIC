import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import csv
import os
import glob

# --- Configuration ---
INPUT_FOLDER = 'epubs_to_convert' # <--- Folder where your EPUB files are located
OUTPUT_FOLDER = 'converted_csvs'   # <--- Folder where the CSV files will be saved
CSV_FIELD_NAMES = ['title', 'content'] 
# ---------------------

def clean_html(html_content):
    """
    Parses HTML content, extracts text, and preserves all original whitespace 
    and line breaks using BeautifulSoup's get_text() method.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove unwanted elements that would clutter the text (e.g., styles, scripts, navigation)
    for unwanted in soup(['style', 'script', 'head', 'meta', 'nav']):
        unwanted.decompose()
        
    # Get all text. The 'separator=" "' argument ensures spaces are kept 
    # between elements, but the crucial part is NOT using text.split()
    text = soup.get_text(separator="\n", strip=False)
    
    # Clean up any residual non-breaking spaces and double-newlines 
    # that might result from HTML conversion, but KEEP single newlines.
    text = text.replace('\xa0', ' ') # Replace non-breaking spaces with standard space
    
    # Optional: Collapse excessive consecutive blank lines into just two (a paragraph break)
    while '\n\n\n' in text:
        text = text.replace('\n\n\n', '\n\n')

    # Remove leading/trailing whitespace from the entire block
    return text.strip()

def convert_single_epub_to_csv(epub_path, csv_path, fieldnames):
    """
    Reads a single EPUB file, extracts chapter content, and writes it to a CSV file.
    """
    try:
        print(f"  -> Processing: {os.path.basename(epub_path)}...")
        book = epub.read_epub(epub_path)
    except Exception as e:
        print(f"  Error reading EPUB file '{os.path.basename(epub_path)}': {e}")
        return

    chapters_data = []

    # Iterate through all document items (chapters, sections, etc.)
    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        
        raw_content = item.get_content()
        # Use the updated cleaning function that preserves spacing
        clean_text = clean_html(raw_content)

        # Use the item's file name as a rough title/identifier
        chapter_title = item.file_name.split('/')[-1] if item.file_name else 'Untitled Chapter'
        
        chapters_data.append({
            'title': chapter_title,
            # The 'content' field now contains the text with preserved newlines and spacing
            'content': clean_text 
        })

    # Write the extracted data to the CSV file
    try:
        # csv.DictWriter handles complex strings by quoting them, which is essential
        # when a field contains newlines or commas.
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            # We use quoting=csv.QUOTE_ALL to ensure multi-line fields are properly quoted
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore', quoting=csv.QUOTE_ALL)
            writer.writeheader()
            writer.writerows(chapters_data)
        
        print(f"  ✅ Saved {len(chapters_data)} chapters to: {os.path.basename(csv_path)}")

    except Exception as e:
        print(f"  Error writing to CSV for '{os.path.basename(epub_path)}': {e}")


def batch_convert_epubs(input_dir, output_dir, fieldnames):
    """
    Finds and converts all EPUBs in the input directory to CSV files 
    in the output directory.
    """
    # 1. Create the output folder if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    print(f"Output will be saved in: {output_dir}\n")

    # 2. Find all EPUB files in the input folder
    search_path = os.path.join(input_dir, '*.epub')
    epub_files = glob.glob(search_path)
    
    if not epub_files:
        print(f"❌ No EPUB files found in the '{input_dir}' folder. Please check the path and file extensions.")
        return

    print(f"Found {len(epub_files)} EPUB files to convert.")
    print("-" * 30)

    # 3. Loop through each file and convert it
    for epub_file_path in epub_files:
        # Create the output CSV file path
        base_name = os.path.basename(epub_file_path)
        csv_file_name = base_name.replace('.epub', '.csv')
        csv_file_path = os.path.join(output_dir, csv_file_name)
        
        # Call the single conversion function
        convert_single_epub_to_csv(epub_file_path, csv_file_path, fieldnames)
    
    print("-" * 30)
    print("✨ Batch conversion complete!")


# --- Execution ---
if __name__ == "__main__":
    # Ensure the input folder exists before running
    os.makedirs(INPUT_FOLDER, exist_ok=True)
    
    print(f"Place your EPUB files in the **'{INPUT_FOLDER}'** folder.")
    
    batch_convert_epubs(INPUT_FOLDER, OUTPUT_FOLDER, CSV_FIELD_NAMES)
