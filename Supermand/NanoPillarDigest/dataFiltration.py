import pandas as pd
import os
import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt
import time


# --- Helper: Statistical summary ---
def statistical_summary(long_df):
    """Print and plot key stats after filtering."""
    print("\n📊 Statistical Summary After Filtering")

    total_peptides = long_df['GravySequence'].nunique()
    total_samples = long_df['Sample'].nunique()
    nonzero_peptides = long_df.groupby('GravySequence')['Intensity'].apply(lambda x: (x > 0).any()).sum()
    nonzero_samples = long_df.groupby('Sample')['Intensity'].apply(lambda x: (x > 0).any()).sum()

    print(f"✅ Total peptides: {total_peptides}")
    print(f"✅ Total samples (replicates): {total_samples}")
    print(f"✅ Peptides kept (with at least 1 nonzero intensity): {nonzero_peptides}")
    print(f"✅ Samples kept (with at least 1 nonzero intensity): {nonzero_samples}")

    plt.figure(figsize=(8, 5))
    plt.hist(long_df['Intensity'], bins=50)
    plt.xlabel('Intensity')
    plt.ylabel('Frequency')
    plt.title('Distribution of Intensities After Filtering')
    plt.yscale('log')
    plt.grid(True)
    plt.show()


# --- Main Script ---

# Start tkinter hidden window
root = tk.Tk()
root.withdraw()

# Select input file
input_file = filedialog.askopenfilename(
    title="Select merged input CSV",
    filetypes=[("CSV Files", "*.csv")]
)
if not input_file:
    raise ValueError("No input file selected!")

# Select output folder
output_folder = filedialog.askdirectory(
    title="Select folder to save output"
)
if not output_folder:
    raise ValueError("No output folder selected!")

# Load file
print(f"📂 Loading: {input_file}")
start = time.time()
df = pd.read_csv(input_file)
print(f"✅ File loaded ({df.shape[0]} rows, {df.shape[1]} columns) in {time.time() - start:.2f} seconds.")

# Preprocessing: melt wide to long
print("🔄 Reshaping wide to long format...")
id_vars = ['GravySequence', 'GravyScore', 'Precursor.Charge']
value_vars = [col for col in df.columns if col not in id_vars]

long_df = df.melt(id_vars=id_vars, value_vars=value_vars,
                  var_name='Sample', value_name='Intensity')

# Parse sample metadata
print("🔄 Parsing sample metadata...")
sample_split = long_df['Sample'].str.extract(
    r'(?P<Load>\d+p\d+)_(?P<Amount>\d+pg)_(?P<Extraction>ACN|NoACN)\.(?P<Replicate>\d+)'
)

long_df = pd.concat([long_df, sample_split], axis=1)
long_df['Position'] = long_df['Load'] + '_' + long_df['Amount']
# Keep Sample column for now!
# No drop of 'Sample' column

# Make Intensity numeric
long_df['Intensity'] = pd.to_numeric(long_df['Intensity'], errors='coerce').fillna(0)

# Step 1: Drop fully missing peptides
print("🔄 Dropping peptides missing across all samples...")
peptides_with_signal = long_df.groupby('GravySequence')['Intensity'].apply(lambda x: (x > 0).any())
peptides_to_keep = peptides_with_signal[peptides_with_signal].index
long_df = long_df[long_df['GravySequence'].isin(peptides_to_keep)]

# Step 2: Drop empty replicates
print("🔄 Dropping sample replicates missing all peptides...")
samples_with_signal = long_df.groupby('Sample')['Intensity'].apply(lambda x: (x > 0).any())
samples_to_keep = samples_with_signal[samples_with_signal].index
long_df = long_df[long_df['Sample'].isin(samples_to_keep)]

# Final statistics
statistical_summary(long_df)

# Save output
output_filename = os.path.join(output_folder, "Filtered_LongFormat.csv")
long_df.to_csv(output_filename, index=False)
print(f"\n✅ Output saved to: {output_filename}")
