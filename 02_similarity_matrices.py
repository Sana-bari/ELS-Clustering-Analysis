#similarity matrices formation
import pandas as pd
import numpy as np
import os

# File path for the data
absolute_file_path = os.path.join('data', 'processed', 'Merged_Data_Corrected.xlsx')

# Load the Excel file
excel_data = pd.ExcelFile(absolute_file_path)

# Initialize a dictionary to store similarity matrices for each sheet
similarity_matrices = {}

# Iterate over the sheets
for sheet_name in excel_data.sheet_names:
    print(f"Processing sheet: {sheet_name}")

    # Read the sheet into a DataFrame
    data = excel_data.parse(sheet_name)

    # ORIGINAL PDF GAP: 'numerical_data' and 'labels' are used below but not defined.
    # Restore their definitions from the actual working script before executing.
    # Calculate the Pearson correlation matrix between rows (each colony with itself and every other colony)
    row_correlation_matrix = np.corrcoef(numerical_data)

    # Store the similarity matrix with labels
    similarity_matrices[sheet_name] = pd.DataFrame(
        row_correlation_matrix, index=labels, columns=labels
    )

    # Save the similarity matrix to a new Excel file using openpyxl engine
    output_file_path = os.path.join(
        os.path.dirname(absolute_file_path), f"{sheet_name}_Pearson_Similarity_Matrix.xlsx"
    )
    similarity_matrices[sheet_name].to_excel(output_file_path, engine='openpyxl')
    print(f"Saved similarity matrix for sheet: {sheet_name} to {output_file_path}")

print("Processing complete!")
