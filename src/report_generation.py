import configparser
import os
import subprocess
import pandas as pd
from datetime import datetime

def main():
    config = configparser.ConfigParser()
    config.read('config.ini')

    blast_results_dir = config['paths']['blast_results']
    output_dir = config['paths']['functional_annotations']
    num_threads = config['settings']['num_threads']

    # Read target species from CSV
    try:
        target_species_df = pd.read_csv('input/target_species.csv')
        species_tax_ids = target_species_df['tax_id'].astype(str).tolist()
        species_names = dict(zip(target_species_df['tax_id'].astype(str), target_species_df['species_name']))
    except FileNotFoundError:
        print("Error: input/target_species.csv not found. Please create it.")
        return

    # Read protein IDs from human_pathway_proteins.fasta
    query_proteins = []
    try:
        with open('input/human_pathway_proteins.fasta', 'r') as f:
            for line in f:
                if line.startswith('>'):
                    query_proteins.append(line.strip().split('|')[1] if '|' in line else line.strip()[1:])
    except FileNotFoundError:
        print("Error: input/human_pathway_proteins.fasta not found. Please create it.")
        return

    report_content = "# Cross-Species N-Glycosylation Pathway Analysis Report\n\n"
    report_content += "This report summarizes the BLAST search results for N-glycosylation pathway enzymes across selected eukaryotic species.\n\n"

    report_content += "## Run Parameters\n\n"
    report_content += f"- Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    report_content += f"- Number of threads used for BLAST: {num_threads}\n"
    report_content += "- BLAST program: blastp\n"
    report_content += "- BLAST output format: 6 std qlen slen (Query ID, Subject ID, % Identity, Alignment Length, Mismatches, Gap Opens, Query Start, Query End, Subject Start, Subject End, E-value, Bit Score, Query Length, Subject Length)\n\n"

    report_content += "## Query Proteins (Human N-Glycosylation Pathway - OST Complex Enzymes)\n\n"
    for protein_id in query_proteins:
        report_content += f"- {protein_id}\n"
    report_content += "\n"

    for tax_id in species_tax_ids:
        species_name = species_names.get(tax_id, f"Unknown Species ({tax_id})")
        blast_file = f"{blast_results_dir}/{tax_id}_blast_results.tsv"

        report_content += f"## {species_name} (Tax ID: {tax_id})\n\n"

        if os.path.exists(blast_file):
            try:
                # Define column names based on blast -outfmt 6 std
                col_names = ['qseqid', 'sseqid', 'pident', 'length', 'mismatch', 'gapopen', 
                             'qstart', 'qend', 'sstart', 'send', 'evalue', 'bitscore', 
                             'qlen', 'slen']
                blast_df = pd.read_csv(blast_file, sep='\t', header=None, names=col_names)
                
                if not blast_df.empty:
                    report_content += "| Query ID | Subject ID | % Identity | Alignment Length | Mismatches | Gap Opens | Query Start | Query End | Subject Start | Subject End | E-value | Bit Score | Query Length | Subject Length |\n"
                    report_content += "|:---------|:-----------|:-----------|:-----------------|:-----------|:----------|:------------|:----------|:--------------|:------------|:--------|:----------|:-------------|:---------------|\n"
                    for index, row in blast_df.iterrows():
                        report_content += f"| {row['qseqid']} | {row['sseqid']} | {row['pident']:.2f} | {int(row['length'])} | {int(row['mismatch'])} | {int(row['gapopen'])} | {int(row['qstart'])} | {int(row['qend'])} | {int(row['sstart'])} | {int(row['send'])} | {row['evalue']:.1e} | {int(row['bitscore'])} | {int(row['qlen'])} | {int(row['slen'])} |\n"
                    report_content += "\n"
                else:
                    report_content += "No significant BLAST hits found.\n\n"
            except pd.errors.EmptyDataError:
                report_content += "BLAST results file is empty or malformed.\n\n"
        else:
            report_content += "BLAST results file not found.\n\n"

    output_report_path = os.path.join(output_dir, "pathway_analysis_report.md")
    with open(output_report_path, "w") as f:
        f.write(report_content)
    print(f"Report generated at {output_report_path}")

if __name__ == "__main__":
    main()
