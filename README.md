# Cross-Species Pathway Analysis Pipeline

Richard Shipman - 2025

This repository contains a simple, automated pipeline for comparing a human enzymatic pathway across hundreds of other species. The pipeline is designed to be straightforward, using Python, Bash, and standard command-line bioinformatics tools.

## Setup Instructions

Follow these steps to set up your environment and run the initial test of the pipeline.

### 1. Clone the Repository

If you haven't already, clone this repository to your local machine.```

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
    logs = logs/
    target_species_file = input/target_species.csv

    [settings]
    num_threads = 8
    query_file = input/human_glycosylation_pathway.fasta

    [blast_settings]
    # E-value cutoff for BLAST hits. Lower values are more stringent.
    evalue = 0.001
    # Maximum number of aligned sequences to keep.
    max_target_seqs = 10
    # Word size for BLAST search. Larger word sizes are faster but less sensitive.
    word_size = 3
    # Scoring matrix for BLAST. Common choices include BLOSUM62, PAM30, etc.
    matrix = BLOSUM62
    # Gap open penalty.
    gapopen = 11
    # Gap extension penalty.
    gapextend = 1
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

## Running with Docker

Alternatively, you can use the provided `Dockerfile` to run the pipeline in a containerized environment. This avoids the need to install dependencies on your local machine.

### 1. Build the Docker Image

From the root of the project directory, build the Docker image:

```bash
docker build -t cross-species-pipeline .
```

### 2. Run the Pipeline in a Docker Container

Once the image is built, you can run the pipeline using the following command:

```bash
docker run --rm -v $(pwd)/data:/app/data -v $(pwd)/results:/app/results -v $(pwd)/logs:/app/logs cross-species-pipeline
```

This command will:
*   Run the pipeline inside a container.
*   Mount the `data`, `results`, and `logs` directories from your local machine into the container, so that the output is saved to your project directory.
*   The `--rm` flag will automatically remove the container when the pipeline finishes.

## Methodology

### Why BLAST?

The core of this pipeline relies on the Basic Local Alignment Search Tool (BLAST) to identify homologous proteins across different species. BLAST is a cornerstone of bioinformatics, widely recognized for its ability to find regions of local similarity between sequences. This makes it an ideal choice for:

*   **Identifying Homologs:** By comparing the amino acid sequences of the human pathway proteins (the "query") against the entire proteome of a target species, we can identify proteins that are likely to have a shared evolutionary origin and potentially a similar function.
*   **Speed and Efficiency:** BLAST is highly optimized for searching large databases, making it feasible to analyze hundreds of species in a reasonable amount of time.
*   **Statistical Significance:** BLAST provides a statistical measure of the significance of a match (the E-value), which helps to distinguish between true homologs and random sequence similarity. A lower E-value indicates a more significant match.

The pipeline specifically uses `blastp`, which is designed for protein-protein comparisons. The results of the BLAST search provide the raw data for the subsequent analysis and report generation, allowing us to infer the presence or absence of the pathway of interest in the target species.

### Citation

Altschul, S.F., Gish, W., Miller, W., Myers, E.W., Lipman, D.J. (1990) “Basic local alignment search tool.” J. Mol. Biol. 215:403-410.

