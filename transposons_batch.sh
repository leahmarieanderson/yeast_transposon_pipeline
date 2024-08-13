#!/bin/bash
#$ -pe serial 5
#$ -l mfree=8778M
#$ -l h_rt=10:0:0

FORWARD=$1
REVERSE=$2
NAME=$3

mkdir ${NAME}
cd ${NAME}

#activate the environment - these two lines allow it to be activated even in a job queueing system
CONDA_BASE=$(conda info --base)
source ${CONDA_BASE}/etc/profile.d/conda.sh
conda activate mcclintock

#debugging: check active environment and paths
echo "Active environment: $(conda info | grep 'active environment')"


#run mcclintock with your samples
#python3 /net/gs/vol1/home/leaha3/mcclintock/mcclintock.py \
#	-r /net/gs/vol1/home/leaha3/mcclintock/test/sacCer2.fasta \
#	-c /net/gs/vol1/home/leaha3/mcclintock/test/sac_cer_TE_seqs.fasta \
#	-g /net/gs/vol1/home/leaha3/mcclintock/test/reference_TE_locations.gff \
#	-t /net/gs/vol1/home/leaha3/mcclintock/test/sac_cer_te_families.tsv \
#	-1 ${FORWARD} \
#	-2 ${REVERSE} 

conda deactivate
