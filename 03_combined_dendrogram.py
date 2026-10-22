import os
import numpy as np
import pandas as pd
import scipy.cluster.hierarchy as sch
from scipy.spatial.distance import squareform
from scipy.cluster.hierarchy import fcluster
import matplotlib.pyplot as plt
import plotly.figure_factory as ff  # Missing import in PDF; ff is used below.

# Function to load the similarity matrix from a CSV file with strain labels
def load_similarity_matrix(file_path):
    matrix = pd.read_csv(file_path, index_col=0)
    print(f"Loaded matrix from {file_path}, shape: {matrix.shape}")
    return matrix

# Function to find common rows and columns between all matrices
def find_common_indices(*matrices):
    common_indices = set(matrices[0].index)
    for matrix in matrices[1:]:
        common_indices = common_indices.intersection(set(matrix.index))
    common_indices = sorted(list(common_indices))
    print(f"Common indices found: {len(common_indices)}")
    return common_indices

# Function to trim matrices to only include common rows and columns
def trim_matrices(common_indices, *matrices):
    trimmed_matrices = []
    for matrix in matrices:
        trimmed_matrix = matrix.loc[common_indices, common_indices]
        print(f"Trimmed matrix shape: {trimmed_matrix.shape}")
        trimmed_matrices.append(trimmed_matrix)
    return trimmed_matrices

# Function to combine multiple similarity matrices by averaging them
def combine_similarity_matrices(*matrices):
    matrix_arrays = [matrix.values for matrix in matrices]
    combined = np.mean(matrix_arrays, axis=0)
    combined_symmetric = (combined + combined.T) / 2
    return combined_symmetric

# Function to convert similarity matrix to distance matrix (1 - similarity)
def similarity_to_distance_matrix(similarity_matrix):
    distance_matrix = 1 - similarity_matrix
    np.fill_diagonal(distance_matrix, 0)
    return distance_matrix

pseudozernike_path = os.path.join('data', 'processed', 'similarity matrix for pseudozernike.csv')
experimental_path = os.path.join('data', 'processed', 'similarity matrix for experimental.csv')

# 1. Load matrices
pseudozernike_matrix = load_similarity_matrix(pseudozernike_path)
experimental_matrix = load_similarity_matrix(experimental_path)

# 3. Find common indices and trim the matrices accordingly
common_indices = find_common_indices(pseudozernike_matrix, experimental_matrix)
pseudozernike_matrix, experimental_matrix = trim_matrices(common_indices,
    pseudozernike_matrix, experimental_matrix)

# Combine the similarity matrices and convert to distance matrix
combined_similarity = combine_similarity_matrices(pseudozernike_matrix,
    experimental_matrix)
distance_matrix = similarity_to_distance_matrix(combined_similarity)

# 5. Get the original labels (full strain names) from one of the matrices
labels = pseudozernike_matrix.index.tolist()

# 6. Create an interactive dendrogram using Plotly.
fig = ff.create_dendrogram(
    distance_matrix,
    orientation='right',
    labels=labels,
    linkagefun=lambda x: sch.linkage(squareform(distance_matrix), method='average')
)
fig.update_layout(
    title="Full Main Dendrogram with Original Labels",
    height=20000, # Increase height (e.g. 12000 pixels) to allow vertical scrolling.
    width=1300, # Adjust width as needed.
    font=dict(size=12) # Font size set to 12 pt.
)

# 7. Save the dendrogram as an interactive HTML file.
output_html = os.path.join('outputs', 'full_main_dendrogram.html')
fig.write_html(output_html)
print(f"Full main dendrogram saved to: {output_html}")
