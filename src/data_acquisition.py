import configparser
import os
import subprocess
import glob
import pandas as pd


def main():
    config = configparser.ConfigParser()
    config.read('config.ini')

    proteomes_dir = config['paths']['proteomes']
    blast_db_dir = config['paths']['blast_databases']

    target_species_file = config['paths']['target_species_file']

    # Read target species from CSV
    try:
        target_species_df = pd.read_csv(target_species_file)
        species_tax_ids = target_species_df['tax_id'].astype(str).tolist()
    except FileNotFoundError:
        print("Error: input/target_species.csv not found. Please create it.")
        return

    for tax_id in species_tax_ids:
        proteome_file = f"{proteomes_dir}/{tax_id}.faa"
        if not os.path.exists(proteome_file):
            print(f"Downloading proteome for species {tax_id}")
            subprocess.run(["datasets", "download", "genome", "taxon", tax_id, "--annotated", "--include", "protein", "--filename", f"{proteomes_dir}/{tax_id}.zip"])
            subprocess.run(["unzip", "-o", f"{proteomes_dir}/{tax_id}.zip", "-d", proteomes_dir])
            # Find the protein.faa file using glob, as the path can vary
            protein_faa_files = glob.glob(f"{proteomes_dir}/ncbi_dataset/data/*/protein.faa")
            if protein_faa_files:
                os.rename(protein_faa_files[0], proteome_file)
            else:
                print(f"Error: protein.faa not found for species {tax_id} after unzipping.")
                continue # Skip to the next species if file not found
            subprocess.run(["rm", "-rf", f"{proteomes_dir}/ncbi_dataset", f"{proteomes_dir}/{tax_id}.zip"])

        db_name = f"{blast_db_dir}/{tax_id}"
        if not os.path.exists(f"{db_name}.psq"):
            print(f"Creating BLAST database for species {tax_id}")
            subprocess.run(["makeblastdb", "-in", proteome_file, "-dbtype", "prot", "-out", db_name])

if __name__ == "__main__":
    main()
