#!/bin/bash
#$ -pe serial 5
#$ -l mfree=16G
#$ -l h_rt=10:0:0

set -euo pipefail

# Find conda
if command -v conda >/dev/null 2>&1; then
    CONDA_EXE="$(command -v conda)"
elif [ -x "${HOME}/miniforge3/bin/conda" ]; then
    CONDA_EXE="${HOME}/miniforge3/bin/conda"
elif [ -x "${HOME}/mambaforge/bin/conda" ]; then
    CONDA_EXE="${HOME}/mambaforge/bin/conda"
elif [ -x "${HOME}/miniconda3/bin/conda" ]; then
    CONDA_EXE="${HOME}/miniconda3/bin/conda"
elif [ -x "${HOME}/conda/bin/conda" ]; then
    CONDA_EXE="${HOME}/conda/bin/conda"
else
    echo "ERROR: conda not found. Install Miniforge/Miniconda and make sure conda is available." >&2
    exit 1
fi

CONDA_BASE="$("$CONDA_EXE" info --base)"
source "${CONDA_BASE}/etc/profile.d/conda.sh"
conda activate mcclintock

# Optional diagnostics
echo "Using conda at: $CONDA_EXE"
echo "Conda base: $CONDA_BASE"
which conda || true
which mamba || true

FORWARD=$1
REVERSE=$2
NAME=$3
WORKDIR=$4
CURRENT_DIR=${SGE_O_WORKDIR}

mkdir ${NAME}
cd ${NAME}

# path to mcclintock
MCDIR=${HOME}/mcclintock

#activate the environment - these two lines allow it to be activated even in a job queueing system
# CONDA_BASE=$(conda info --base)
# source ${CONDA_BASE}/etc/profile.d/conda.sh
# conda activate mcclintock

#run mcclintock with your samples
python3 ${MCDIR}/mcclintock.py \
	-r ${MCDIR}/test/sacCer2.fasta \
	-c ${MCDIR}/test/sac_cer_TE_seqs.fasta \
	-g ${MCDIR}/test/reference_TE_locations.gff \
	-t ${MCDIR}/test/sac_cer_te_families.tsv \
	-1 ${FORWARD} \
	-2 ${REVERSE} \
	-p 5

# Run the organizer python script to get all non-redundant-non-reference site vcfs into one folder. 
python3 ${CURRENT_DIR}/yeast_transposon_pipeline/output_organizer.py ${WORKDIR}/transposons

conda deactivate
