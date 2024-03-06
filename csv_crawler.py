import os
import pandas as pd
import json

def crawl_directory_for_csv(root_dir):
    csv_files = []
    valid_directories = set()

    for foldername, subfolders, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.csv') or filename.endswith('.CSV'):
                file_path = os.path.join(foldername, filename)

                try:
                    df = pd.read_csv(file_path)
                    if 'Time' in df.columns and len(df.columns) > 15:
                        csv_files.append(file_path)
                        valid_directories.add(os.path.abspath(foldername))
                        break  # Move on to the next directory
                except:
                    pass

    return csv_files, valid_directories

# Automatically detect the root directory as the current working directory
root_directory = r"C:/"
result, valid_directories = crawl_directory_for_csv(root_directory)

# Save the list of file paths to a JSON file
output_file_path = 'path_of_csvs.json'
with open(output_file_path, 'w') as json_file:
    json.dump(result, json_file)

print(f"List of CSV files meeting the conditions saved to {output_file_path}")

print("\nList of unique directories containing valid CSV files:")
for directory in valid_directories:
    print(directory)
