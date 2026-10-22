# Dependencies:
# pip install pandas openpyxl umap-learn matplotlib seaborn
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from umap import UMAP
import os

# File paths
exp_path = os.path.join('data', 'processed', 'Experimental labels merged.csv')
pseudo_path = os.path.join('data', 'processed', 'Pseudozernike lables merged.csv')

# ORIGINAL PDF GAP: exp_df and pseudo_df are referenced without CSV-loading lines.
# ORIGINAL PDF GAP: exp_feats and pseudo_feats are referenced without definitions.
# Restore the actual lines from the original working script before execution.

# Rename first column to 'Taxon'
exp_df.rename(columns={exp_df.columns[0]: 'Taxon'}, inplace=True)
pseudo_df.rename(columns={pseudo_df.columns[0]: 'Taxon'}, inplace=True)

# Find common samples
exp_df['UID'] = exp_df['Taxon']
pseudo_df['UID'] = pseudo_df['Taxon']
common_uids = set(exp_df['UID']).intersection(pseudo_df['UID'])
exp_sub = exp_df[exp_df['UID'].isin(common_uids)].reset_index(drop=True)
pseudo_sub = pseudo_df[pseudo_df['UID'].isin(common_uids)].reset_index(drop=True)

# Combine features
combined = pd.concat([exp_feats, pseudo_feats], axis=1)
X = combined.select_dtypes(include=['number']).dropna()

# Get corresponding Taxon labels
idx = X.index
taxa = exp_sub.loc[idx, 'Taxon']

# Map genus
def map_genus(name):
    name = name.lower()
    if name.startswith('arcobacter') or name.startswith('a.'):
        return 'Arcobacter'
    if 'aeromonas' in name:
        return 'Aeromonas'
    if name.startswith('yersinia') or name.startswith('y.') or 'yersinia' in name:
        return 'Yersinia'
    if 'coli' in name or name.startswith('e.'):
        return 'E. coli'
    return 'Other'

genus = taxa.apply(map_genus)

# Filter only four target genera
mask = genus.isin(['Arcobacter', 'Aeromonas', 'Yersinia', 'E. coli'])
X_final = X.loc[mask]
genus_final = genus.loc[mask]
species_final = taxa.loc[mask]

# Run UMAP
reducer = UMAP(n_neighbors=15, min_dist=0.1, random_state=42)
embedding = reducer.fit_transform(X_final)

# Plot by genus
palette_g = {
    'Arcobacter': sns.color_palette("Set1")[0],
    'Aeromonas': sns.color_palette("Set1")[1],
    'Yersinia': sns.color_palette("Set1")[2],
    'E. coli': sns.color_palette("Set1")[3]
}
plt.figure(figsize=(10, 7))
sns.scatterplot(x=embedding[:, 0], y=embedding[:, 1], hue=genus_final,
    palette=palette_g, s=50, alpha=0.8)
plt.title('UMAP – Genus')
plt.xlabel('UMAP 1')
plt.ylabel('UMAP 2')
plt.tight_layout()
plt.savefig(os.path.join('outputs', 'umap_by_genus.png'), dpi=300)
plt.close()

# Plot by species
species_colors = sns.color_palette("tab20", n_colors=len(species_final.unique()))
palette_s = dict(zip(species_final.unique(), species_colors))
plt.figure(figsize=(10, 7))
sns.scatterplot(x=embedding[:, 0], y=embedding[:, 1], hue=species_final,
    palette=palette_s, s=50, alpha=0.8)
plt.title('UMAP – Species')
plt.xlabel('UMAP 1')
plt.ylabel('UMAP 2')
plt.tight_layout()
plt.savefig(os.path.join('outputs', 'umap_by_species.png'), dpi=300)
plt.close()
