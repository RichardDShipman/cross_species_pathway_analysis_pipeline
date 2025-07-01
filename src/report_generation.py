import configparser
import os
import subprocess
import pandas as pd
from datetime import datetime
import sys


def main():
    if len(sys.argv) != 2:
        print("Usage: python report_generation.py <tax_id>")
        sys.exit(1)

    tax_id = sys.argv[1]

    config = configparser.ConfigParser()
    config.read('config.ini')

    blast_results_dir = config['paths']['blast_results']
    output_dir = config['paths']['functional_annotations']
    num_threads = config['settings']['num_threads']
    query_file_path = config['settings']['query_file']

    target_species_file = config['paths']['target_species_file']

    # Read target species from CSV to get species name
    try:
        target_species_df = pd.read_csv(target_species_file)
        species_info = target_species_df[target_species_df['tax_id'].astype(str) == tax_id]
        if not species_info.empty:
            species_name = species_info.iloc[0]['species_name']
        else:
            species_name = f"Unknown Species ({tax_id})"
    except FileNotFoundError:
        print(f"Error: {target_species_file} not found. Please create it.")
        return

    # Read protein IDs from the query fasta file
    import re

    print(f"Current working directory: {os.getcwd()}")
    print(f"Query file path: {query_file_path}")
    print(f"Query file exists: {os.path.exists(query_file_path)}")

    query_proteins_info = []
    try:
        with open(query_file_path, 'r') as f:
            for line in f:
                if line.startswith('>'):
                    header = line.strip('>').strip()
                    qseqid = header.split(' ')[0]
                    accession_match = re.search(r'\|(.*?)\|', header)
                    accession = accession_match.group(1) if accession_match else 'N/A'
                    gene_name_match = re.search(r'GN=(.+?) PE=', header)
                    gene_name = gene_name_match.group(1) if gene_name_match else 'N/A'
                    parts = header.split('|')
                    description = 'N/A'
                    if len(parts) >= 3:
                        remaining_header = parts[2].strip()
                        first_space_index = remaining_header.find(' ')
                        if first_space_index != -1:
                            potential_description = remaining_header[first_space_index:].strip()
                            os_index = potential_description.find('OS=')
                            if os_index != -1:
                                description = potential_description[:os_index].strip()
                            else:
                                description = potential_description.strip()
                    query_proteins_info.append({
                        'qseqid': qseqid,
                        'accession': accession,
                        'description': description,
                        'gene_name': gene_name
                    })
    except FileNotFoundError:
        print(f"Error: {query_file_path} not found. Please check your config.ini.")
        return
    query_proteins_info.sort(key=lambda x: x['gene_name'])

    report_content = f"# Cross-Species Pathway Analysis Report for {species_name}\n\n"
    report_content += "This report summarizes the BLAST search results for pathway enzymes.\n\n"

    report_content += "## Run Parameters\n\n"
    report_content += f"- Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    report_content += f"- Species: {species_name} (Tax ID: {tax_id})\n"
    report_content += f"- Number of threads used for BLAST: {num_threads}\n"
    report_content += f"- Query File: {query_file_path}\n"
    report_content += "- BLAST program: blastp\n"
    report_content += "- BLAST output format: 6 std qlen slen (Query ID, Subject ID, % Identity, Alignment Length, Mismatches, Gap Opens, Query Start, Query End, Subject Start, Subject End, E-value, Bit Score, Query Length, Subject Length)\n\n"

    # Add BLAST parameters
    report_content += "### BLAST Parameters\n\n"
    report_content += f"- E-value cutoff: {config['blast_settings']['evalue']}\n"
    report_content += f"- Max target sequences: {config['blast_settings']['max_target_seqs']}\n"
    report_content += f"- Word size: {config['blast_settings']['word_size']}\n"
    report_content += f"- Scoring matrix: {config['blast_settings']['matrix']}\n"
    report_content += f"- Gap open penalty: {config['blast_settings']['gapopen']}\n"
    report_content += f"- Gap extension penalty: {config['blast_settings']['gapextend']}\n\n"

    report_content += f"## BLAST Results for {species_name} (Tax ID: {tax_id})\n\n"

    blast_file = f"{blast_results_dir}/{tax_id}_blast_results.tsv"

    full_blast_df = pd.DataFrame()
    if os.path.exists(blast_file):
        try:
            col_names = ['qseqid', 'sseqid', 'pident', 'length', 'mismatch', 'gapopen',
                         'qstart', 'qend', 'sstart', 'send', 'evalue', 'bitscore',
                         'qlen', 'slen']
            full_blast_df = pd.read_csv(blast_file, sep='\t', header=None, names=col_names)
        except pd.errors.EmptyDataError:
            report_content += "BLAST results file is empty or malformed.\n\n"

    for protein in query_proteins_info:
        report_content += f"### {protein['gene_name']} ({protein['accession']})\n\n"
        report_content += f"**Description:** {protein['description']}\n\n"

        if not full_blast_df.empty:
            # Filter BLAST results for the current query protein
            protein_blast_df = full_blast_df[full_blast_df['qseqid'] == protein['qseqid']]

            if not protein_blast_df.empty:
                report_content += "| Subject ID | % Identity | Alignment Length | E-value | Bit Score |\n"
                report_content += "|:-----------|:-----------|:-----------------|:--------|:----------|\n"
                for index, row in protein_blast_df.iterrows():
                    report_content += f"| {row['sseqid']} | {row['pident']:.2f} | {int(row['length'])} | {row['evalue']:.1e} | {int(row['bitscore'])} |\n"
                report_content += "\n"
            else:
                report_content += "No significant BLAST hits found for this protein.\n\n"
        else:
            report_content += "BLAST results file not found or was empty.\n\n"

    output_report_path = os.path.join(output_dir, f"pathway_analysis_report_{tax_id}.md")
    with open(output_report_path, "w") as f:
        f.write(report_content)
    print(f"Report generated for {species_name} at {output_report_path}")


if __name__ == "__main__":
    main()
