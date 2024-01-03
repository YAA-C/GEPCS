import os
import pandas as pd

def concatenate_csv_files(input_folder, output_file):
    # Get a list of all CSV files in the input folder
    csv_files = [file for file in os.listdir(input_folder) if file.endswith('.csv')]

    # Check if there are any CSV files
    if not csv_files:
        print("No CSV files found in the input folder.")
        return

    # Initialize an empty list to store DataFrames
    dfs = []

    # Read the first CSV file to get the column names and dtypes
    first_csv = pd.read_csv(os.path.join(input_folder, csv_files[0]))
    columns = list(first_csv.columns)
    dtypes = first_csv.dtypes

    # Concatenate all CSV files
    for csv_file in csv_files:
        current_csv = pd.read_csv(os.path.join(input_folder, csv_file))
        dfs.append(current_csv)

    # Concatenate all DataFrames in the list
    result_df = pd.concat(dfs, ignore_index=True)

    # Remove rows with all values empty (horizontal empty rows)
    result_df = result_df.dropna(how='all')

    # Write the concatenated data to the output CSV file
    result_df.to_csv(output_file, index=False)
    print(f"Concatenation completed. Result saved to {output_file}")

    # Remove the original CSV files
    for csv_file in csv_files:
        os.remove(os.path.join(input_folder, csv_file))
        print(f"Deleted: {csv_file}")

    # Move the output CSV file to the input folder
    output_path = os.path.join(input_folder, output_file)
    os.replace(output_file, output_path)
    print(f"Moved {output_file} to {input_folder}")

# Get the current directory (should be 'csvConcat')
current_dir = os.getcwd()

# Get the parent directory
parent_dir = os.path.dirname(current_dir)

# Construct the path to the 'DemoFiles/csv' folder
demo_files_dir = os.path.join(parent_dir, 'DemoFiles', 'csv')

print(demo_files_dir)

output_file = 'output.csv'
concatenate_csv_files(demo_files_dir, output_file)