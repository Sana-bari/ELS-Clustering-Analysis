import os
import numpy as np
import pandas as pd
import scipy.cluster.hierarchy as sch
from scipy.spatial.distance import squareform
from scipy.cluster.hierarchy import fcluster
import matplotlib.pyplot as plt

# Function to load the similarity matrix from a CSV file with strain labels
def load_similarity_matrix(file_path):
    matrix = pd.read_csv(file_path, index_col=0)
    print(f"Loaded matrix from {file_path}, shape: {matrix.shape}")
    return matrix

# Function to filter Arcobacter strains based on the specified row ranges
def filter_arcobacter_by_row_range(matrix, start_row, end_row):
    arcobacter_matrix = matrix.iloc[start_row-1:end_row, start_row-1:end_row]
    arcobacter_labels = matrix.index[start_row-1:end_row]
    print(f"Filtered matrix for Arcobacter strains, new shape: {arcobacter_matrix.shape}")
    return arcobacter_matrix, arcobacter_labels

# Function to find and remove rows/columns that are not common between two matrices
def keep_common_rows_and_columns(matrix1, matrix2):
    common_indices = matrix1.index.intersection(matrix2.index)
    matrix1_common = matrix1.loc[common_indices, common_indices]
    matrix2_common = matrix2.loc[common_indices, common_indices]
    print(f"After removing uncommon rows/columns: Matrix 1 shape: {matrix1_common.shape}, Matrix 2 shape: {matrix2_common.shape}")
    return matrix1_common, matrix2_common

# Function to combine multiple similarity matrices by averaging them and enforce symmetry
def combine_similarity_matrices(*matrices):
    matrix_arrays = [matrix.values for matrix in matrices]
    combined = np.mean(matrix_arrays, axis=0)
    combined_symmetric = (combined + combined.T) / 2
    return combined_symmetric

# Function to convert similarity matrix to distance matrix (1 - similarity)
def similarity_to_distance_matrix(similarity_matrix):
    if similarity_matrix.shape[0] == 0:
        raise ValueError("The filtered similarity matrix is empty. No clustering can be performed.")
    distance_matrix = 1 - similarity_matrix
    np.fill_diagonal(distance_matrix, 0)
    return distance_matrix

# Function to generate dendrograms, calculate cophenetic coefficient, and save results
def generate_dendrogram_and_results(distance_matrix, labels, output_path, threshold):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    linkage_matrix = sch.linkage(squareform(distance_matrix), method='average')
    cluster_labels = fcluster(linkage_matrix, t=threshold, criterion='distance')
    plt.figure(figsize=(22, 10))
    dendrogram = sch.dendrogram(linkage_matrix, labels=labels, leaf_rotation=90,
        leaf_font_size=8, color_threshold=threshold)
    plt.title(f'Dendrogram at threshold {threshold}')
    plt.tight_layout()
    main_dendrogram_path = os.path.join(output_path,
        f'Arcobacters_only_dendrogram_threshold_{threshold}.png')
    plt.savefig(main_dendrogram_path, bbox_inches='tight')
    plt.show()
    print(f"Main dendrogram saved at {main_dendrogram_path}")
    return cluster_labels, dendrogram, linkage_matrix

# Function to generate and display sub-dendrograms with colors preserved from the main dendrogram
def generate_sub_dendrograms_with_colors_preserved(linkage_matrix, cluster_labels,
    dendrogram, labels, distance_matrix):
    original_colors = dendrogram['leaves_color_list']
    unique_clusters = np.unique(cluster_labels)[::-1]
    for i, cluster in enumerate(unique_clusters):
        cluster_indices = np.where(cluster_labels == cluster)[0]
        if len(cluster_indices) > 1:
            cluster_distance_matrix = distance_matrix[np.ix_(cluster_indices, cluster_indices)]
            cluster_linkage_matrix = sch.linkage(squareform(cluster_distance_matrix),
                method='average')
            cluster_labels_subset = [labels[i] for i in cluster_indices]
            cluster_colors = [original_colors[dendrogram['leaves'].index(i)] for i in cluster_indices]
            plt.figure(figsize=(18, 10))
            sch.dendrogram(
                cluster_linkage_matrix,
                labels=cluster_labels_subset,
                leaf_rotation=90,
                leaf_font_size=6,
                link_color_func=lambda x: cluster_colors[x % len(cluster_colors)]
            )
            plt.title(f'Sub-Dendrogram for Cluster {cluster}')
            plt.show()
            print(f"Displayed sub-dendrogram for cluster {cluster}.")

# Updated file paths
pseudozernike_path = os.path.join('data', 'processed', 'similarity matrix for pseudozernike.csv')
experimental_path = os.path.join('data', 'processed', 'similarity matrix for experimental.csv')

# Load similarity matrices
pseudozernike_matrix = load_similarity_matrix(pseudozernike_path)
experimental_matrix = load_similarity_matrix(experimental_path)

# Print initial shapes before any filtering
print(f"Initial pseudo-Zernike shape: {pseudozernike_matrix.shape}")
print(f"Initial experimental shape: {experimental_matrix.shape}")

# Step 1: Filter Arcobacter strains based on the provided row ranges
# Pseudozernike: Rows 1 to 527, Experimental: Rows 1 to 564 (before excluding RM 5557)
pseudozernike_matrix, pseudozernike_labels = filter_arcobacter_by_row_range(pseudozernike_matrix, 1, 527)
experimental_matrix, experimental_labels = filter_arcobacter_by_row_range(experimental_matrix, 1, 564)

# Step 3: Remove any rows/columns that are not common between the two matrices
pseudozernike_matrix, experimental_matrix = keep_common_rows_and_columns(pseudozernike_matrix, experimental_matrix)

# Combine similarity matrices and convert to distance matrix
combined_similarity = combine_similarity_matrices(pseudozernike_matrix,
    experimental_matrix)
distance_matrix = similarity_to_distance_matrix(combined_similarity)

# Set the output path to the desktop
output_path = os.path.join('outputs', 'aberrant colonies removed')

# Step 4: Generate the main dendrogram
labels = pseudozernike_labels # Use the Arcobacter labels for the dendrogram
threshold = 0.25
cluster_labels, dendrogram, linkage_matrix = generate_dendrogram_and_results(distance_matrix, labels, output_path, threshold)

# Step 5: Display sub-dendrograms for each cluster, preserving colors
generate_sub_dendrograms_with_colors_preserved(linkage_matrix, cluster_labels,
    dendrogram, labels, distance_matrix)
