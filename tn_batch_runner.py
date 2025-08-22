import os
import argparse

def createOutputDirectories(work_dir_path):
	# Make a directory for the transposon outputs if it doesn't exist
	transposons_dir = os.path.join(work_dir_path, "transposons")
	os.makedirs(transposons_dir, exist_ok=True)

	# Make the error and output directories if they don't exist already
	outputs_dir = os.path.join(work_dir_path, "outputs")
	errors_dir = os.path.join(work_dir_path, "errors")
	os.makedirs(outputs_dir, exist_ok=True)
	os.makedirs(errors_dir, exist_ok=True)

def batchSubmit(work_dir_path):
	# open sample list
	with open(f"{work_dir_path}/transposons/sample_list.txt", "r") as forward_read_list:
		#iterate through the sample list; run transposon pipeline
		for fastq in forward_read_list:
			fastq = fastq.strip()
			fastq_prefix = fastq[:-15]
			path_names = fastq.split("/")
			job_name = path_names[-1][:-16]
			#submit each individual sample job to cluster with qsub
			os.system(
				f"qsub -N {job_name} -wd {work_dir_path}/transposons "
				f"-o {work_dir_path}/outputs -e {work_dir_path}/errors "
				f"transposons_batch.sh {fastq} {fastq_prefix}R2_001.fastq.gz {job_name} {work_dir_path}")

def main():
	parser = argparse.ArgumentParser(description="Batch Submit fastq files for transposon analysis")
	parser.add_argument("work_dir_path", help="Path to working directory, should contain your fastq folder")
	parser.add_argument("fastq_dir_name", nargs="?", default="fastq", help="name of fastq folder to submit (default: fastq)")
	args = parser.parse_args()
	work_dir_path = args.work_dir_path
	fastq_dir_name = args.fastq_dir_name
	createOutputDirectories(work_dir_path)
	# Make the sample list, only forward reads
	os.system(f"ls {work_dir_path}/{fastq_dir_name}/*R1_001.fastq.gz > {work_dir_path}/transposons/sample_list.txt")
	batchSubmit(work_dir_path)

if __name__ == "__main__":
    main()



