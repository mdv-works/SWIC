import os
import re

# --- Configuration ---
# Directory where your .srt files are located (from the previous download script)
SRT_DIRECTORY = "japanese_subtitles"

# Directory where the cleaned .txt files will be saved
OUTPUT_DIRECTORY = "cleaned_dialogues"
# ---------------------

def read_srt_file_with_fallback(filepath):
    """
    Reads a file attempting Shift JIS first, then UTF-8, to handle common 
    Japanese subtitle encodings and prevent UnicodeDecodeError.
    """
    encodings = ['shift_jis', 'utf-8']
    content = None
    
    for encoding in encodings:
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                content = f.read()
            print(f"  -> Successfully decoded with {encoding}")
            return content
        except UnicodeDecodeError:
            continue  # Try the next encoding
        except Exception as e:
            print(f"  -> ERROR reading file {os.path.basename(filepath)}: {e}")
            return None

    # If all primary encodings fail, issue a warning and skip
    print(f"  -> WARNING: Failed to decode {os.path.basename(filepath)} with common Japanese encodings. Skipping.")
    return None


def clean_srt_file(srt_filepath):
    """
    Reads an SRT file, strips timecodes and sequence numbers, and returns
    only the clean dialogue lines.
    """
    print(f"  -> Processing: {os.path.basename(srt_filepath)}")
    
    content = read_srt_file_with_fallback(srt_filepath)
    if content is None:
        return "" # Return empty string if reading failed

    # 1. Remove sequence numbers (e.g., '1', '2', '3')
    # This pattern matches one or more digits at the start of a line.
    content = re.sub(r'^\d+\n', '', content, flags=re.MULTILINE)

    # 2. Remove timecode lines (e.g., '00:00:00,000 --> 00:00:02,500')
    # This pattern is robust for standard SRT time formats.
    content = re.sub(r'\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}\n', '', content)
    
    # --- Post-Processing ---
    
    # Split into lines
    lines = content.split('\n')
    
    cleaned_lines = []
    for line in lines:
        # Strip whitespace from each line
        stripped_line = line.strip()
        
        # Only keep lines that are not empty
        if stripped_line:
            cleaned_lines.append(stripped_line)

    # Join the final list of clean lines with a single newline
    return '\n'.join(cleaned_lines)

def main():
    """Main function to iterate over all SRT files and clean them."""
    
    # Create the output directory
    os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)
    print(f"Output directory created: '{OUTPUT_DIRECTORY}'")

    if not os.path.exists(SRT_DIRECTORY):
        print(f"\nError: Source directory '{SRT_DIRECTORY}' not found.")
        print("Please ensure your downloaded .srt files are in this directory, or update the SRT_DIRECTORY variable.")
        return

    # List all files in the source directory
    all_files = os.listdir(SRT_DIRECTORY)
    
    srt_files = [f for f in all_files if f.lower().endswith('.srt')]
    
    if not srt_files:
        print(f"\nNo .srt files found in '{SRT_DIRECTORY}'.")
        return

    print(f"\nFound {len(srt_files)} .srt files to process.")

    for srt_filename in srt_files:
        srt_filepath = os.path.join(SRT_DIRECTORY, srt_filename)
        
        # Get the clean dialogue
        dialogue = clean_srt_file(srt_filepath)
        
        # Only write the file if we successfully read and cleaned the content
        if dialogue:
            # Define the output file name and path (changing .srt to .txt)
            base_name = os.path.splitext(srt_filename)[0]
            output_filename = f"{base_name}_dialogue.txt"
            output_filepath = os.path.join(OUTPUT_DIRECTORY, output_filename)
            
            # Write the clean dialogue to the new text file
            try:
                # Use UTF-8 for the output file to ensure it's easily readable everywhere
                with open(output_filepath, 'w', encoding='utf-8') as outfile:
                    outfile.write(dialogue)
                print(f"  -> Saved to: {output_filename}")
            except IOError as e:
                print(f"  -> ERROR writing file {output_filename}: {e}")

    print("\nProcessing complete.")

if __name__ == "__main__":
    main()
