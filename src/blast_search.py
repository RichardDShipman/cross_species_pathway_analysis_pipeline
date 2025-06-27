import configparser
import os
import subprocess
import pandas as pd

def main():
    config = configparser.ConfigParser()
    config.read('config.ini')

    proteomes_dir = config['paths']['proteomes']
    blast_db_dir = config['paths']['blast_databases']
    blast_results_dir = config['paths']['blast_results']

    target_species_file = config['paths']['target_species_file']

    # Read target species from CSV
    try:
        target_species_df = pd.read_csv(target_species_file)
        species_tax_ids = target_species_df['tax_id'].astype(str).tolist()
    except FileNotFoundError:
        print(f"Error: {target_species_file} not found. Please create it.")
        return

    query_file = config['settings']['query_file']

    # BLAST parameters
    evalue = config['blast_settings'].getfloat('evalue')
    max_target_seqs = config['blast_settings'].getint('max_target_seqs')
    word_size = config['blast_settings'].getint('word_size')
    matrix = config['blast_settings']['matrix']
    gapopen = config['blast_settings'].getint('gapopen')
    gapextend = config['blast_settings'].getint('gapextend')

    for tax_id in species_tax_ids:
        db_name = f"{blast_db_dir}/{tax_id}"
        output_file = f"{blast_results_dir}/{tax_id}_blast_results.tsv"

        if not os.path.exists(f"{db_name}.psq"):
            print(f"BLAST database for species {tax_id} not found. Skipping BLAST for this species.")
            continue

        print(f"Running BLAST for species {tax_id}")
        subprocess.run([
            "blastp",
            "-query", query_file,
            "-db", db_name,
            "-outfmt", "6 std qlen slen", # Standard output format plus query and subject lengths
            "-evalue", str(evalue),
            "-max_target_seqs", str(max_target_seqs),
            "-word_size", str(word_size),
            "-matrix", matrix,
            "-gapopen", str(gapopen),
            "-gapextend", str(gapextend),
            
            "-out", output_file
        ])

if __name__ == "__main__":
    main()
