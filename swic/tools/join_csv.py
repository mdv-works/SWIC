import pandas as pd
import glob
import os
import csv 

# --- Configuration (Should match the previous script's output) ---
INPUT_FOLDER = 'converted_csvs'   # <--- Folder containing the individual CSVs
MASTER_CSV_FILE = 'combined_epub_data.csv' # <--- The final combined file name
# ----------------------------------------------------------------

def combine_csv_files(input_dir, output_file):
    """
    Finds all CSV files in a directory, combines them into one DataFrame,
    and saves the result to a master CSV file.
    """
    # 1. Check if the input directory exists
    if not os.path.exists(input_dir):
        print(f"❌ Error: Input folder '{input_dir}' not found.")
        print("Please run the batch conversion script first.")
        return

    # 2. Find all CSV files in the input folder
    search_path = os.path.join(input_dir, '*.csv')
    csv_files = glob.glob(search_path)
    
    if not csv_files:
        print(f"❌ No CSV files found in the '{input_dir}' folder.")
        return

    print(f"Found {len(csv_files)} CSV files to combine.")
    
    # 3. Read and combine all CSVs
    all_data = []
    
    for file_path in csv_files:
        try:
            # Read the CSV. The quoting is important because the content field 
            # contains newlines and commas.
            df = pd.read_csv(file_path, quoting=csv.QUOTE_ALL)
            
            # Add a column to identify the original book/file
            original_filename = os.path.basename(file_path)
            df['original_file'] = original_filename.replace('.csv', '.epub')
            
            all_data.append(df)
            print(f"  -> Added data from: {original_filename}")
            
        except Exception as e:
            print(f"  Error reading CSV file '{os.path.basename(file_path)}': {e}")
            
    if not all_data:
        print("No data was successfully read. Cannot create master file.")
        return

    # 4. Concatenate all DataFrames into one
    master_df = pd.concat(all_data, ignore_index=True)

    # 5. Save the master DataFrame to a new CSV file
    master_df.to_csv(output_file, index=False, quoting=csv.QUOTE_ALL)
    
    print("-" * 40)
    print(f"✨ Success! All data combined.")
    print(f"Total rows: {len(master_df)}")
    print(f"Master file saved as: {output_file}")


# --- Execution ---
if __name__ == "__main__":
    combine_csv_files(INPUT_FOLDER, MASTER_CSV_FILE)
