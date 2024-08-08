import os
import sys

arg_list = []

for arg in sys.argv:
	arg_list.append(arg)

working_directory = arg_list[1]

#make the sample list, only forward reads
os.system("ls " + working_directory + "/fastq/*R1_001.fastq.gz > sample_list.txt") 

forward_read_list = open("sample_list.txt", "r")

#iterate through the sample list; run transposon pipeline
for fastq in forward_read_list:
	fastq = fastq.strip()
	fastq_prefix = fastq[:-15]
	path_names = fastq.split("/")
	job_name = path_names[-1][:-20]
	os.system(
		f"qsub -N {job_name} -wd {working_directory}/transposons "
		f"-o {working_directory}/outputs -e {working_directory}/errors "
		f"transposons_batch.sh {fastq} {fastq_prefix}R2_001.fastq.gz {job_name}")



