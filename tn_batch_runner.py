import os
import sys

arg_list = sys.argv

working_directory = arg_list[1]

# Make a directory for the transposon outputs if it doesn't exist
transposons_dir = os.path.join(working_directory, "transposons")
os.makedirs(transposons_dir, exist_ok=True)

# Make the sample list, only forward reads
os.system(f"ls {working_directory}/fastq/*R1_001.fastq.gz > {transposons_dir}/sample_list.txt")

forward_read_list = open(f"{working_directory}/transposons/sample_list.txt", "r")

#open sample list
with open(f"{transposons_dir}/sample_list.txt", "r") forward_read_list:
	#iterate through the sample list; run transposon pipeline
	for fastq in forward_read_list:
		fastq = fastq.strip()
		fastq_prefix = fastq[:-15]
		path_names = fastq.split("/")
		job_name = path_names[-1][:-20]
		#submit each individual sample job to cluster with qsub
		os.system(
			f"qsub -N {job_name} -wd {working_directory}/transposons "
			f"-o {working_directory}/outputs -e {working_directory}/errors "
			f"transposons_batch.sh {fastq} {fastq_prefix}R2_001.fastq.gz {job_name}")



