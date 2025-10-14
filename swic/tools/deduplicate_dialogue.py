import os

INPUT_FILE = "all_dialogues_merged.csv"
OUTPUT_FILE = "all_dialogues_unique.csv"

def remove_duplicate_sentences():
    """
    Reads the merged dialogue file and filters out duplicate lines,
    preserving the order of the *first* occurrence of each unique line.
    """
    if not os.path.exists(INPUT_FILE):
        print(f"Error: Input file '{INPUT_FILE}' not found. Please run the merge script first.")
        return

    # Use an OrderedDict (or list + set combination) to preserve original order
    # while ensuring uniqueness. We'll use a set for simplicity and speed.
    unique_lines = set()
    output_lines = []
    
    line_count = 0
    unique_count = 0

    print(f"Starting deduplication of '{INPUT_FILE}'...")
    
    try:
        # Read the file
        with open(INPUT_FILE, 'r', encoding='utf-8') as infile:
            for line in infile:
                line_count += 1
                
                # Strip whitespace, including the newline character
                stripped_line = line.strip()
                
                # We want to skip empty lines, lines only containing filenames, 
                # and lines that are already in our unique set.

                # Check if the line is just the quoted filename (e.g., "file.txt")
                # and is not dialogue we want to deduplicate.
                is_filename_line = stripped_line.startswith('"') and stripped_line.endswith('"')

                if is_filename_line or not stripped_line:
                    # Keep the filename markers and blank lines in the output, but don't count them
                    # for dialogue deduplication.
                    output_lines.append(line)
                    continue

                # Deduplication check:
                if stripped_line not in unique_lines:
                    unique_lines.add(stripped_line)
                    output_lines.append(line) # Keep the original line (with its newline char)
                    unique_count += 1
                    
        # Write the unique lines to the new output file
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as outfile:
            outfile.writelines(output_lines)
            
        print(f"\n--- Operation Complete ---")
        print(f"Total lines read: {line_count}")
        print(f"Unique dialogue lines found: {unique_count}")
        print(f"Duplicates removed: {line_count - unique_count}")
        print(f"Output saved to: {OUTPUT_FILE}")

    except Exception as e:
        print(f"An error occurred during processing: {e}")

if __name__ == "__main__":
    remove_duplicate_sentences()
