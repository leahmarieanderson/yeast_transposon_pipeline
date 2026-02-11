# Yeast Transposon Pipeline - Quick Start Guide

## Prerequisites

1. **Directory Structure**: Organize your sequencing data with a `fastq` subdirectory containing all forward (F) and reverse (R) FastQ files from Illumina sequencing.

2. **McClintock Installation**: Install McClintock in your home directory:
   ```bash
   cd ~
   git clone https://github.com/bergmanlab/mcclintock.git
   # Follow McClintock installation instructions
   ```

## Pipeline Workflow

### 1. Run McClintock in Batches
Use the batch runner to process all your samples:
```bash
python3 tn_batch_runner.py
```
This will submit jobs using `transposons_batch.sh` for each sample pair.

### 2. Organize Outputs
After McClintock completes, organize the non-redundant VCF files:
```bash
python3 output_organizer.py /path/to/transposons
```
This creates `nonredundant_vcfs` folders in each sample directory.

### 3. Collect VCFs
Gather all non-redundant VCF files into a single directory:
```bash
python3 collect_vcfs.py /path/to/transposons
```
Creates an `all_nonredundant_vcfs` directory with all VCF files.

### 4. Combine VCFs
Merge all VCF files into a single analysis file:
```bash
python3 combine_vcfs.py /path/to/transposons/all_nonredundant_vcfs
```

## Expected Directory Structure

```
your_data/
├── fastq/
│   ├── sample1_R1_001.fastq.gz
│   ├── sample1_R2_001.fastq.gz
│   ├── sample2_R1_001.fastq.gz
│   └── sample2_R2_001.fastq.gz
└── transposons/ (created by pipeline)
    ├── sample1/
    │   └── nonredundant_vcfs/
    ├── sample2/
    │   └── nonredundant_vcfs/
    └── all_nonredundant_vcfs/
```

## Notes
- McClintock must be installed in `~/mcclintock` for the batch script to work without modification
- The pipeline expects paired-end Illumina data with `_R1_001` and `_R2_001` naming convention
- Processing runs on SGE cluster with 5 cores and 16G memory per job