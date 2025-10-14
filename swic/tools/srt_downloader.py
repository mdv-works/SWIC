import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin
from zipfile import ZipFile
import io
# import rarfile # Uncomment this if you install the rarfile library

BASE_URL = "https://kitsunekko.net/subtitles/japanese/"
DOWNLOAD_DIR = "japanese_subtitles"

def setup_directory():
    """Create the main download directory if it doesn't exist."""
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    print(f"Subtitles will be saved in the '{DOWNLOAD_DIR}' directory.")

def get_html_content(url):
    """Fetches the HTML content of a given URL."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def find_all_links(html_content, base_url):
    """Parses HTML and finds all absolute links to show pages."""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # *** IMPORTANT: Adjust the selector below! ***
    # This is a general guess. You might need to check the website's source
    # code to find the correct CSS selector or tag structure for the show links.
    # E.g., if links have a specific class, use: soup.find_all('a', class_='show-link')
    links = soup.find_all('a') 
    
    show_urls = []
    for link in links:
        href = link.get('href')
        if href and not href.startswith('#'):
            full_url = urljoin(base_url, href)
            # Filter out external links or links that aren't for shows/files
            if full_url.startswith(BASE_URL) and full_url != BASE_URL:
                show_urls.append(full_url)
                
    # Use a set to handle duplicates and convert back to a list
    return sorted(list(set(show_urls)))

def process_archive(file_content, filename):
    """Extracts .srt files from a zip archive."""
    extracted_count = 0
    try:
        # Check if it's a ZIP file
        if filename.endswith('.zip'):
            with ZipFile(io.BytesIO(file_content)) as z:
                # Get a list of all .srt files inside the zip
                srt_files = [name for name in z.namelist() if name.lower().endswith('.srt')]
                
                # Extract all .srt files
                for srt_file in srt_files:
                    target_path = os.path.join(DOWNLOAD_DIR, os.path.basename(srt_file))
                    
                    # Prevent overwriting files with the same name from different archives
                    counter = 1
                    original_target_path = target_path
                    while os.path.exists(target_path):
                        name, ext = os.path.splitext(original_target_path)
                        target_path = f"{name}_{counter}{ext}"
                        counter += 1
                        
                    with open(target_path, 'wb') as f:
                        f.write(z.read(srt_file))
                    extracted_count += 1
            print(f"  -> Extracted {extracted_count} .srt file(s) from {filename}")
            
        # Check if it's a RAR file (Requires 'rarfile' library)
        elif filename.endswith('.rar'):
            # try:
            #     # Note: rarfile requires the 'unrar' utility installed on your system
            #     # If you don't need .rar support, you can remove this block.
            #     with rarfile.RarFile(io.BytesIO(file_content)) as r:
            #         # ... (similar extraction logic for rarfile)
            # except Exception as e:
            #     print(f"  -> WARNING: Failed to extract RAR file {filename}. Ensure 'unrar' is installed. Error: {e}")
            print(f"  -> WARNING: RAR file detected ({filename}). Skipping extraction (requires 'rarfile' and 'unrar').")

        else:
            print(f"  -> WARNING: Unknown archive format for {filename}. Skipping.")
            
    except Exception as e:
        print(f"  -> ERROR during extraction of {filename}: {e}")

def main():
    setup_directory()
    print("Starting crawl on main page...")
    
    # 1. Get the list of all individual show/series pages
    main_page_html = get_html_content(BASE_URL)
    if not main_page_html:
        return

    # In a typical index, these are links to pages like /A/, /B/, /C/, etc. or direct show pages.
    all_pages_to_visit = find_all_links(main_page_html, BASE_URL)
    
    if not all_pages_to_visit:
        print("Could not find any links on the main page. Check the HTML selector in find_all_links().")
        return
    
    print(f"Found {len(all_pages_to_visit)} show/index pages to process.")
    
    # 2. Iterate through all found pages (show pages)
    for i, page_url in enumerate(all_pages_to_visit):
        print(f"\n[{i+1}/{len(all_pages_to_visit)}] Processing: {page_url}")
        
        show_page_html = get_html_content(page_url)
        if not show_page_html:
            continue
            
        show_soup = BeautifulSoup(show_page_html, 'html.parser')
        
        # 3. Find all archive links on the show page
        # Typically links ending in .zip or .rar
        archive_links = show_soup.find_all('a', href=lambda href: href and (href.endswith('.zip') or href.endswith('.rar')))
        
        if not archive_links:
            print("  -> No archive links found on this page.")
            continue

        print(f"  -> Found {len(archive_links)} archive(s) to download.")
        
        # 4. Download and process each archive
        for link in archive_links:
            archive_relative_url = link.get('href')
            archive_url = urljoin(page_url, archive_relative_url)
            filename = os.path.basename(archive_url)
            
            print(f"  -> Downloading {filename}...")

            try:
                # Stream the download to handle large files
                with requests.get(archive_url, stream=True, timeout=30) as r:
                    r.raise_for_status()
                    
                    # Read the entire file content into memory buffer (for zip/rar handler)
                    file_content = r.content 
                    
                process_archive(file_content, filename)

            except requests.exceptions.RequestException as e:
                print(f"  -> ERROR downloading {filename}: {e}")

if __name__ == "__main__":
    main()