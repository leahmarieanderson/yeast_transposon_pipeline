#!/bin/bash
#$ -pe serial 5
#$ -l mfree=16G
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

#run mcclintock with your samples
python3 /net/gs/vol1/home/leaha3/mcclintock/mcclintock.py \
	-r /net/gs/vol1/home/leaha3/mcclintock/test/sacCer2.fasta \
	-c /net/gs/vol1/home/leaha3/mcclintock/test/sac_cer_TE_seqs.fasta \
	-g /net/gs/vol1/home/leaha3/mcclintock/test/reference_TE_locations.gff \
	-t /net/gs/vol1/home/leaha3/mcclintock/test/sac_cer_te_families.tsv \
	-1 ${FORWARD} \
	-2 ${REVERSE} \
	#run all methods aside from relocate2, which causes problems since the ubuntu update on the cluster
    -m ngs_te_mapper,ngs_te_mapper2,relocate,temp,temp2,retroseq,popoolationte,popoolationte2,te-locate,teflon,coverage,trimgalore,map_reads,tebreak

conda deactivate
