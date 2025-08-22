import os
import argparse

parser = argparse.ArgumentParser(description="Gather all non-redundant_vcf files from each caller and organize them into a folder")
parser.add_argument("transposons_dir_path", help="Path to transposons directory")
args = parser.parse_args()

transposons_path = args.transposons_dir_path


directory_list = open(f"{transposons_path}/sample_list.txt", "r")

te_detectors_list = ["ngs_te_mapper", "ngs_te_mapper2", "popoolationte", "popoolationte2", "relocate", "relocate2", "retroseq", "te-locate", "tebreak", "teflon", "temp", "temp2"]

for fastq in directory_list:
    #get name of each sample directory
    path_names = fastq.strip().split("/")
    sample_dir1 = path_names[-1][:-16]
    sample_dir2 = sample_dir1 + "_R1_001"
    sample_directory = os.path.join(transposons_path,sample_dir1) # transposons/sample
    nonredundant_dir = os.path.join(sample_directory, "nonredundant_vcfs")
    os.makedirs(nonredundant_dir, exist_ok=True)
    results_directory = os.path.join(sample_directory, sample_dir2, "results") # workdirectory/sample/sample_R1_001/results

    for detector in te_detectors_list:
        detector_path = os.path.join(results_directory, detector)
        for file in os.listdir(detector_path):
            if file.endswith("nonredundant_non-reference_siteonly.vcf"):
                nonredun_file = os.path.join(detector_path, file)
                os.system(f"cp {nonredun_file} {nonredundant_dir}")
                print(f"Copied {nonredun_file} over to {nonredundant_dir}")

