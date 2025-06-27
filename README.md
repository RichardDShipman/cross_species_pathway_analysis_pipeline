# Cross-Species Pathway Analysis Pipeline

This repository contains a simple, automated pipeline for comparing a human enzymatic pathway across hundreds of other species. The pipeline is designed to be straightforward, using Python, Bash, and standard command-line bioinformatics tools.

## Setup Instructions

Follow these steps to set up your environment and run the initial test of the pipeline.

### 1. Clone the Repository

If you haven't already, clone this repository to your local machine:

```bash
git clone <repository_url> # Replace with the actual repository URL
cd cross_species_analysis_pipeline/
```

### 2. Install Required Command-Line Tools

This pipeline depends on two core bioinformatics tools from NCBI: `NCBI Datasets` and `NCBI BLAST+`. Ensure they are installed and available in your system's PATH.

*   **NCBI Datasets:** Used for downloading genomic and proteomic data.
    *   **Installation:** The `datasets` command-line tool can be installed by downloading the appropriate binary for your operating system from the [NCBI Datasets Installation Guide](https://www.ncbi.nlm.nih.gov/datasets/docs/v2/download-and-install/).
    *   **Example (macOS/Linux):**
        ```bash
        # Download the datasets tool
        # For macOS:
        curl -o datasets "https://s3.amazonaws.com/datasets-cli/v17.1.1/mac/datasets"
        # For Linux:
        # curl -o datasets "https://s3.amazonaws.com/datasets-cli/v17.1.1/linux-amd64/datasets"

        # Make it executable
        chmod +x datasets

        # Move it to a directory in your PATH (e.g., ~/.local/bin or /usr/local/bin)
        mkdir -p ~/.local/bin
        mv datasets ~/.local/bin/
        # Ensure ~/.local/bin is in your PATH. Add the following to your shell's rc file (e.g., ~/.bashrc, ~/.zshrc):
        # export PATH="$HOME/.local/bin:$PATH"
        # source ~/.bashrc # or ~/.zshrc
        ```

*   **NCBI BLAST+:** Used for running sequence similarity searches.
    *   **Installation:** Download the appropriate executables from the [NCBI BLAST+ Installation Guide](https://www.ncbi.nlm.nih.gov/books/NBK279690/). Follow the instructions to add the BLAST+ executables to your system's PATH.

### 3. Create the Project Directory Structure

The pipeline uses a predefined folder structure for data and results. Create these directories using the following command:

```bash
mkdir -p data/proteomes data/blast_databases data/blast_results results/functional_annotations results/pathway_wikipedia logs
```

### 4. Set Up the Python Environment

The project's Python dependencies are listed in `requirements.txt`. It is recommended to use a virtual environment.

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 5. Review Configuration and Input Files

*   **`config.ini`:** All key parameters for the pipeline are stored in `config.ini`. Review its contents to understand the configured paths and settings.

    ```ini
    [paths]
    proteomes = data/proteomes/
    blast_databases = data/blast_databases/
    blast_results = data/blast_results/
    functional_annotations = results/functional_annotations/
    pathway_wikipedia = results/pathway_wikipedia/
    logs = logs/

    [settings]
    num_threads = 4
    ```

*   **`input/target_species.csv`:** This file specifies the eukaryotic species for cross-species analysis. It contains `tax_id` and `species_name`.

    ```csv
    tax_id,species_name
    9606,Homo sapiens
    4932,Saccharomyces cerevisiae
    3702,Arabidopsis thaliana
    ```

*   **`input/human_pathway_proteins.fasta`:** This file contains the protein sequences for the human N-linked glycosylation pathway enzymes (specifically, the OST complex enzymes) that will be used as queries for BLAST searches.

### 6. Run the Pipeline

To execute the entire pipeline, run the main pipeline script:

```bash
bash run_pipeline.sh
```

**Pipeline Phases:**

1.  **Data Acquisition:** Downloads proteome data for the species listed in `input/target_species.csv` and creates local BLAST databases.
2.  **BLAST Search:** Performs BLAST searches using the protein sequences in `input/human_pathway_proteins.fasta` against the generated proteome databases.
3.  **Report Generation:** Processes the BLAST results and generates a human-readable report in Markdown format, saved to `results/functional_annotations/pathway_analysis_report.md`.

**Expected Outcome:**

*   `data/proteomes/` will contain `.faa` files for each species.
*   `data/blast_databases/` will contain the corresponding BLAST database files.
*   `data/blast_results/` will contain `.tsv` files with raw BLAST results for each species.
*   `results/functional_annotations/pathway_analysis_report.md` will contain a summary of the BLAST results.
*   `logs/pipeline.log` will contain a detailed log of the pipeline execution.
