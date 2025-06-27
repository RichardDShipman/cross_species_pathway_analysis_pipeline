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
    python3 src/report_generation.py
    log "Report Generation Phase Complete"
}

# --- Main Execution ---
log "Pipeline Started"

# Execute all phases
run_data_acquisition
run_blast_search
run_report_generation

log "Pipeline Finished"