# Yeast Transposon Pipeline - Quick Start Guide (for Sarah)

## Prerequisites

1. **Directory Structure**: Organize your sequencing data with a `fastq` subdirectory containing all forward (F) and reverse (R) FastQ files from Illumina sequencing.

2. **McClintock Installation**: Install McClintock in your home directory:
   ```bash
   cd ~
   git clone https://github.com/bergmanlab/mcclintock.git
   # Follow McClintock installation instructions
   ```

## Pipeline Workflow

I'm goin to use a made-up directory where my data lives as an example, called "/net/dunham/vol2/Leah/yEvo_mica/"

^within this directory is a "fastq" folder containing all f and r fastq's from the illumina sequencing run.

### 1. Run McClintock in Batches
Use the batch runner to process all your samples:
```bash
python3 tn_batch_runner.py /net/dunham/vol2/Leah/yEvo_mica/
```
This will submit jobs using `transposons_batch.sh` for each sample pair. This script should also run output_organizer.py automatically, so if that all ran properly, you will see a folder called "nonredundant_vcfs" in each sample directory when mcclintock is all done.

### 2. Collect VCFs
Gather all non-redundant VCF files into a single directory:
```bash
python3 collect_vcfs.py /net/dunham/vol2/Leah/yEvo_mica/transposons
```
Creates an `all_nonredundant_vcfs` directory with all VCF files.

### 3. Combine VCFs
Merge all VCF files into a single analysis file:
```bash
python3 combine_vcfs.py /net/dunham/vol2/Leah/yEvo_mica/transposons/
```
If you have an ancestor withing this project folder and would like to filter out ancestor transposons, you can add this optional argument:
```bash
python3 combine_vcfs.py /net/dunham/vol2/Leah/yEvo_mica/transposons/ -a YMD4612_pink_S1
```
Note: when designating the ancestor, you only need the prefix. Do not include "_R1_001...etc"


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
