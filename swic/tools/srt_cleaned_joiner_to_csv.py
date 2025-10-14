import os

# --- Configuration ---
# Directory containing the cleaned .txt dialogue files (from the previous script)
INPUT_DIRECTORY = "cleaned_dialogues" 

# Name of the output single text file
OUTPUT_TEXT_FILE = "all_dialogues_merged.txt"
# ---------------------

def merge_text_files_to_single_document():
    """
    Reads all .txt files from the input directory and merges their contents 
    into a single .txt file. The format is: "filename" followed by the file's 
    entire content.
    """
    
    if not os.path.exists(INPUT_DIRECTORY):
        print(f"\nError: Input directory '{INPUT_DIRECTORY}' not found.")
        print("Please ensure your cleaned .txt files are in this directory.")
        return

    # 1. Prepare to write the single output text file
    # Encoding is set to 'utf-8' for universal compatibility.
    try:
        with open(OUTPUT_TEXT_FILE, 'w', encoding='utf-8') as outfile:
            
            print(f"Starting merge operation. Output file: {OUTPUT_TEXT_FILE}")
            
            # 2. Iterate through all .txt files in the input directory
            all_files = os.listdir(INPUT_DIRECTORY)
            txt_files = sorted([f for f in all_files if f.lower().endswith('.txt')])
            
            if not txt_files:
                print(f"No .txt files found in '{INPUT_DIRECTORY}'. Nothing to merge.")
                return

            print(f"Found {len(txt_files)} text files to process.")

            for filename in txt_files:
                filepath = os.path.join(INPUT_DIRECTORY, filename)
                
                print(f"  -> Processing: {filename}")
                
                # 3. Write the filename identifier
                # Format: "name of file"\n
                outfile.write(f'"{filename}"\n')
                
                # 4. Read the entire content of the text file
                # The cleaning script outputted UTF-8, so we read as UTF-8.
                try:
                    with open(filepath, 'r', encoding='utf-8') as txtfile:
                        content = txtfile.read()
                        
                        # 5. Write the content and a separator
                        outfile.write(content)
                        
                        # Add an extra newline to clearly separate the content 
                        # from the next file's name identifier
                        outfile.write('\n\n')

                except IOError as e:
                    print(f"  -> WARNING: Could not read file {filename}. Skipping. Error: {e}")
                except Exception as e:
                    print(f"  -> WARNING: An unexpected error occurred while processing {filename}. Skipping. Error: {e}")

        print("\nMerge complete! Single document generated successfully.")
        
    except IOError as e:
        print(f"\nFATAL ERROR: Could not open or write to the output text file: {e}")


if __name__ == "__main__":
    merge_text_files_to_single_document()
