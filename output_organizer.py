import os
import sys

directory_list = open("sample_list.txt", "r")

#you are currently in the "transposons" directory, along with directories for each sample's mcclintock outputs
os.system("mkdir all_nonredundant_vcfs")

#get the current file path, identify "results" folder for later
current_dir = os.getcwd()
result_directory = "results"

for fastq in directory_list:
    
    #get name of each sample directory
    path_names = fastq.split("/")
    directory1 = path_names[-1][:-21]
    directory2 = path_names[-1][:-10]
    target_directory = os.path.join(current_dir, directory1, directory2, result_directory)

    #go into that folder, then go into the folder with the longer name
    os.chdir(target_directory)
    os.system("ls > temp.txt")
    with open("temp.txt", "r") as method_list:
        for method in method_list:
            method = method.strip()
            if method == "temp.txt":
                continue 
            method_directory = os.path.join(target_directory, method)
            os.chdir(method_directory)
            # try:
            #     os.system("cp *nonredundant_non-reference.vcf ../../../../all_nonredundant_vcfs")
            # except:
            #      print("No vcf in this directory, but no need to worry! Continuing...")
            #      continue

            command = "cp *nonredundant_non-reference.vcf ../../../../all_nonredundant_vcfs"

            exit_status = os.system(command)

            if exit_status == 0:
                print("copied a vcf!")
            else:
                print("No vcf in this directory, but no need to worry! Continuing...")
    
    #remove temp file with names of all transposon methods
    os.system(f"rm {target_directory}/temp.txt")
