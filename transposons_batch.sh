#!/bin/bash
#$ -pe serial 5
#$ -l mfree=8778M
#$ -l h_rt=10:0:0

FORWARD=$1
REVERSE=$2
NAME=$3

mkdir ${NAME}
cd ${NAME}

conda activate mcclintock
python3 /net/dunham/vol2/Leah/230127_FTevo/transposons/mcclintock/mcclintock.py \
	-r /net/dunham/vol2/Leah/230127_FTevo/transposons/mcclintock/test/sacCer2.fasta \
	-c /net/dunham/vol2/Leah/230127_FTevo/transposons/mcclintock/test/sac_cer_TE_seqs.fasta \
	-g /net/dunham/vol2/Leah/230127_FTevo/transposons/mcclintock/test/reference_TE_locations.gff \
	-t /net/dunham/vol2/Leah/230127_FTevo/transposons/mcclintock/test/sac_cer_te_families.tsv \
	-1 ${FORWARD} \
	-2 ${REVERSE} 

conda deactivate
