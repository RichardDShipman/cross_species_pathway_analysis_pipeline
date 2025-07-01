# Use a Python 3.9 base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Install system-level dependencies
# - ncbi-blast+: For running BLAST searches
# - curl: For downloading the datasets tool
RUN apt-get update && apt-get install -y \
    ncbi-blast+ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Download and install the NCBI Datasets command-line tool
RUN curl -o datasets "https://s3.amazonaws.com/datasets-cli/v17.1.1/linux-amd64/datasets" && \
    chmod +x datasets && \
    mv datasets /usr/local/bin/

# Copy the project files into the container
COPY . .

# Create the directory structure required by the pipeline
RUN mkdir -p data/proteomes data/blast_databases data/blast_results results/functional_annotations logs

# Install Python dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make the pipeline execution script executable
RUN chmod +x run_pipeline.sh

# Set the default command to run the pipeline
CMD ["./run_pipeline.sh"]

