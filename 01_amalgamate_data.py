import os
import pandas as pd

# Define the path to the main folder
main_folder_path = os.path.join('data', 'raw')

# Function to get all CSV files from a subfolder
def get_csv_files(subfolder_path):
    csv_files = []
    for root, dirs, files in os.walk(subfolder_path):
        for file in files:
            if file.endswith('.csv'):
                csv_files.append(os.path.join(root, file))
    return csv_files

# Function to extract colony number from file path or filename
def extract_colony_id(file_path):
    file_name = os.path.basename(file_path)
    parts = file_name.split('colony')
    if len(parts) > 1:
        return parts[-1].strip().split('.')[0]
    else:
        return file_name.split('.')[0]

# Define lists for storing data
experimental_data = []
pseudo_zernike_data = []
zernike_data = []

# Iterate over the main subfolders
for folder_name in os.listdir(main_folder_path):
    folder_path = os.path.join(main_folder_path, folder_name)
    if os.path.isdir(folder_path):
        taxon = folder_name # Extract the Taxon from the folder name

        # Iterate over each subfolder like RM 4463, RM 4826, etc.
        for subfolder_name in os.listdir(folder_path):
            subfolder_path = os.path.join(folder_path, subfolder_name)
            if os.path.isdir(subfolder_path):
                strain_id = subfolder_name.split('(')[0].strip() # Extract the Strain ID

                # Get paths to Experimental, Pseudozernike, Zernike folders
                experimental_folder = os.path.join(subfolder_path, 'Experimental')
                pseudo_zernike_folder = os.path.join(subfolder_path, 'Pseudozernike')
                zernike_folder = os.path.join(subfolder_path, 'Zernike')

                # Get all CSV files for Experimental, Pseudozernike, Zernike data
                experimental_files = get_csv_files(experimental_folder)
                pseudo_zernike_files = get_csv_files(pseudo_zernike_folder)
                zernike_files = get_csv_files(zernike_folder)

                # Process each experimental file
                for file in experimental_files:
                    temp_df = pd.read_csv(file)

                    # Extract relevant columns: Column N (moment indices) and Y (moment values)
                    moments = temp_df['N'].astype(str).apply(lambda x: f"Experimental {x}").tolist() # Rename moments
                    moment_values = temp_df['Y'].tolist()

                    # Create a single row DataFrame for each colony
                    colony_df = pd.DataFrame([moment_values], columns=moments)
                    colony_df['Taxon'] = taxon
                    colony_df['Strain ID'] = strain_id
                    colony_df['Colony ID'] = extract_colony_id(file) # Extract colony info

                    # Append the DataFrame to experimental_data
                    experimental_data.append(colony_df)

                # Process each pseudo-Zernike file
                for file in pseudo_zernike_files:
                    temp_df = pd.read_csv(file)

                    # Extract relevant columns: Column N (moment indices) and Y (moment values)
                    moments = temp_df['N'].astype(str).apply(lambda x: f"PseudoZernike {x}").tolist()
                    moment_values = temp_df['Y'].tolist()

                    # Create a single row DataFrame for each colony
                    colony_df = pd.DataFrame([moment_values], columns=moments)
                    colony_df['Taxon'] = taxon
                    colony_df['Strain ID'] = strain_id
                    colony_df['Colony ID'] = extract_colony_id(file)

                    # Append the DataFrame to pseudo_zernike_data
                    pseudo_zernike_data.append(colony_df)

                # Process each Zernike file
                for file in zernike_files:
                    temp_df = pd.read_csv(file)

                    # Extract relevant columns: Column N (moment indices) and Y (moment values)
                    moments = temp_df['N'].astype(str).apply(lambda x: f"Zernike {x}").tolist()
                    moment_values = temp_df['Y'].tolist()

                    # Create a single row DataFrame for each colony
                    colony_df = pd.DataFrame([moment_values], columns=moments)
                    colony_df['Taxon'] = taxon
                    colony_df['Strain ID'] = strain_id
                    colony_df['Colony ID'] = extract_colony_id(file)

                    # Append the DataFrame to zernike_data
                    zernike_data.append(colony_df)

# Concatenate all the data for each category
experimental_df = pd.concat(experimental_data, ignore_index=True)
pseudo_zernike_df = pd.concat(pseudo_zernike_data, ignore_index=True)
zernike_df = pd.concat(zernike_data, ignore_index=True)

# Define the output path for the Excel file
output_excel_file_path = os.path.join('data', 'processed', 'Merged_Data_Corrected.xlsx')

# Write the data into separate sheets in an Excel file
with pd.ExcelWriter(output_excel_file_path, engine='xlsxwriter') as writer:
    # Write each DataFrame to a different sheet
    experimental_df.to_excel(writer, sheet_name='Experimental', index=False)
    zernike_df.to_excel(writer, sheet_name='Zernike Moments', index=False)
    pseudo_zernike_df.to_excel(writer, sheet_name='Pseudo-Zernike Moments', index=False)

print(f'Reorganized data has been saved to {output_excel_file_path}')
