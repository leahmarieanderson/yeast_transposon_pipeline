#!/bin/bash
#$ -pe serial 5
#$ -l mfree=16G
#$ -l h_rt=10:0:0

FORWARD=$1
REVERSE=$2
NAME=$3
WORKDIR=$4

mkdir ${NAME}
cd ${NAME}

# path to mcclintock
MCDIR=/net/dunham/vol2/Zilong/updating_pipeline_2024/mcclintock

#activate the environment - these two lines allow it to be activated even in a job queueing system
CONDA_BASE=$(conda info --base)
source ${CONDA_BASE}/etc/profile.d/conda.sh
conda activate mcclintock

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
python3 ${WORKDIR}/yeast_transposon_pipeline/output_organizer.py ${WORKDIR}/transposons

conda deactivate
