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
    genomes_dir = config['paths']['genomes']
    transcriptomes_dir = config['paths']['transcriptomes']

    download_genomes = config.getboolean('settings', 'download_genomes')
    download_transcriptomes = config.getboolean('settings', 'download_transcriptomes')

    # Create the directories if they don't exist
    os.makedirs(proteomes_dir, exist_ok=True)
    if download_genomes:
        os.makedirs(genomes_dir, exist_ok=True)
    if download_transcriptomes:
        os.makedirs(transcriptomes_dir, exist_ok=True)

    target_species_file = config['paths']['target_species_file']

    # Read target species from CSV
    try:
        target_species_df = pd.read_csv(target_species_file)
        species_tax_ids = target_species_df['tax_id'].astype(str).tolist()
    except FileNotFoundError:
        print(f"Error: {target_species_file} not found. Please create it.")
        return

    for tax_id in species_tax_ids:
        proteome_file = f"{proteomes_dir}/{tax_id}.faa"
        if not os.path.exists(proteome_file):
            print(f"Downloading proteome for species {tax_id}")
            subprocess.run([
                "datasets", "download", "genome", "taxon", tax_id,
                "--reference",
                "--annotated",
                "--include", "protein",
                "--filename", f"{proteomes_dir}/{tax_id}.zip"
            ])
            subprocess.run(["unzip", "-o", f"{proteomes_dir}/{tax_id}.zip", "-d", proteomes_dir])
            protein_faa_files = glob.glob(f"{proteomes_dir}/ncbi_dataset/data/*/protein.faa")
            if protein_faa_files:
                os.rename(protein_faa_files[0], proteome_file)
            else:
                print(f"Error: protein.faa not found for species {tax_id} after unzipping.")
            subprocess.run(["rm", "-rf", f"{proteomes_dir}/ncbi_dataset", f"{proteomes_dir}/{tax_id}.zip"])

        if download_genomes:
            genome_file = f"{genomes_dir}/{tax_id}.fna"
            if not os.path.exists(genome_file):
                print(f"Downloading genome for species {tax_id}")
                subprocess.run([
                    "datasets", "download", "genome", "taxon", tax_id,
                    "--reference",
                    "--include", "genome",
                    "--filename", f"{genomes_dir}/{tax_id}.zip"
                ])
                subprocess.run(["unzip", "-o", f"{genomes_dir}/{tax_id}.zip", "-d", genomes_dir])
                genome_fna_files = glob.glob(f"{genomes_dir}/ncbi_dataset/data/*/*.fna")
                if genome_fna_files:
                    os.rename(genome_fna_files[0], genome_file)
                else:
                    print(f"Error: genomic.fna not found for species {tax_id} after unzipping.")
                subprocess.run(["rm", "-rf", f"{genomes_dir}/ncbi_dataset", f"{genomes_dir}/{tax_id}.zip"])

        if download_transcriptomes:
            transcriptome_file = f"{transcriptomes_dir}/{tax_id}.rna.fna"
            if not os.path.exists(transcriptome_file):
                print(f"Downloading transcriptome for species {tax_id}")
                subprocess.run([
                    "datasets", "download", "genome", "taxon", tax_id,
                    "--reference",
                    "--include", "rna",
                    "--filename", f"{transcriptomes_dir}/{tax_id}.zip"
                ])
                subprocess.run(["unzip", "-o", f"{transcriptomes_dir}/{tax_id}.zip", "-d", transcriptomes_dir])
                transcriptome_fna_files = glob.glob(f"{transcriptomes_dir}/ncbi_dataset/data/*/*.fna")
                if transcriptome_fna_files:
                    os.rename(transcriptome_fna_files[0], transcriptome_file)
                else:
                    print(f"Error: rna.fna not found for species {tax_id} after unzipping.")
                subprocess.run(["rm", "-rf", f"{transcriptomes_dir}/ncbi_dataset", f"{transcriptomes_dir}/{tax_id}.zip"])

        db_name = f"{blast_db_dir}/{tax_id}"
        if not os.path.exists(f"{db_name}.psq"):
            print(f"Creating BLAST database for species {tax_id}")
            subprocess.run(["makeblastdb", "-in", proteome_file, "-dbtype", "prot", "-out", db_name])

if __name__ == "__main__":
    main()
