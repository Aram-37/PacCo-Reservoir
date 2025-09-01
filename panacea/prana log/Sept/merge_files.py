import os
import glob

def merge_files_and_summaries(folder_path, output_file):
    # Summaries of PDF patents (without disclosing critical content)
    pdf_summaries = """
    Summary of ORBITHAL_Interactive Spherical Transformer Patent Explorer.pdf:
    This document outlines a patent application for an interactive spherical transformer system that integrates a physical spherical transformer apparatus with an artificial intelligence controller using a spherical transformer architecture. It focuses on dynamic control for energy transfer optimization through geometric homology between physical and computational domains.

    Summary of Andapdf.pdf:
    This patent application describes the Anda Engine, a cognitive computing system for multi-dimensional truth alignment using layered processing including Sentient Pattern Linguistics, Fractal Truth Recognition, and oscillatory cycles to achieve stabilized meta-cognition and reduce computational complexity.
    """

    # Find all .md and .txt files
    md_files = glob.glob(os.path.join(folder_path, '*.md'))
    txt_files = glob.glob(os.path.join(folder_path, '*.txt'))
    all_files = md_files + txt_files

    # Sort files alphabetically for consistent order
    all_files.sort()

    with open(output_file, 'w', encoding='utf-8') as outfile:
        # Write PDF summaries first
        outfile.write("=== PDF Summaries ===\n")
        outfile.write(pdf_summaries)
        outfile.write("\n\n=== Merged Content from .md and .txt Files ===\n\n")

        for file_path in all_files:
            file_name = os.path.basename(file_path)
            outfile.write(f"=== Content from {file_name} ===\n")
            try:
                with open(file_path, 'r', encoding='utf-8') as infile:
                    content = infile.read()
                    outfile.write(content)
                    outfile.write("\n\n")
            except Exception as e:
                outfile.write(f"Error reading {file_name}: {str(e)}\n\n")

if __name__ == "__main__":
    folder_path = "/Users/sunghkim37/Library/CloudStorage/GoogleDrive-britkenko@gmail.com/My Drive/PACO/ESP/panacea_chunks/untitled folder"
    output_file = "merged_content.txt"
    merge_files_and_summaries(folder_path, output_file)
    print(f"Merged content saved to {output_file}")
