#!/bin/bash

# Exit on error
set -e

# Get log directory from config.ini
LOG_DIR=$(grep '^logs' config.ini | sed 's/.*= *//')

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/pipeline.log"


# Function to log messages
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# --- Phase 1: Data Acquisition ---
run_data_acquisition() {
    log "Starting Data Acquisition Phase"
    python3 src/data_acquisition.py
    log "Data Acquisition Phase Complete"
}

# --- Phase 2: BLAST Search ---
run_blast_search() {
    log "Starting BLAST Search Phase"
    python3 src/blast_search.py
    log "BLAST Search Phase Complete"
}

# --- Phase 3: Report Generation ---
run_report_generation() {
    log "Starting Report Generation Phase"

    # Read target_species.csv and generate a report for each species
    if [ -f "input/target_species.csv" ]; then
        # Skip header row and read each tax_id
        tail -n +2 "input/target_species.csv" | while IFS=, read -r tax_id species_name;
        do
            if [ -n "$tax_id" ]; then
                log "Generating report for species $species_name (Tax ID: $tax_id)"
                python3 src/report_generation.py "$tax_id"
            fi
        done
    else
        log "Error: input/target_species.csv not found. Cannot generate reports."
    fi

    log "Report Generation Phase Complete"
}

# --- Main Execution ---
log "Pipeline Started"

# Execute all phases
run_data_acquisition
run_blast_search
run_report_generation

log "Pipeline Finished"