import os
import pandas as pd

def concatenate_csv_files(input_folder: str, output_file: str):
    # Get a list of all CSV files in the input folder
    csv_files: list = [file for file in os.listdir(input_folder) if file.endswith('.csv')]

    # Check if there are any CSV files
    if not csv_files:
        print("No CSV files found in the input folder.")
        return

    # Initialize an empty list to store DataFrames
    dfs: list = []

    # Concatenate all CSV files
    print("Reading CSV Files...")
    for csv_file in csv_files:
        current_csv = pd.read_csv(os.path.join(input_folder, csv_file))
        dfs.append(current_csv)

    # Concatenate all DataFrames in the list
    print("Starting Concatenation...")
    result_df: pd.DataFrame = pd.concat(dfs, ignore_index=True)

    # Write the concatenated data to the output CSV file
    output_path: str = os.path.join(input_folder, output_file)
    result_df.to_csv(output_path, index=False)
    print(f"Concatenation completed. Result saved to {output_path}")

    # Remove the original CSV files
    for csv_file in csv_files:
        os.remove(os.path.join(input_folder, csv_file))
        print(f"Deleted: {csv_file}")