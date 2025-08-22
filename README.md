# yeast_transposon_pipeline
Scripts to help with running Mcclintock transposon caller 

## Prerequisites 
You must have Mcclintock (and its corresponding dependencies) installed on your environment.

You can check out installation instructions from the [Mcclintock Github](https://github.com/bergmanlab/mcclintock) or for a more detailed installation guide look below or, check out the shared google doc version [here](https://docs.google.com/document/d/1cA9sQ-0HiX67_fNMSfAapybzSDzP6EO1-JooZWAwC2U/edit?tab=t.0).

### Install Conda and Mamba via Miniforge
First, you want to install Conda and Mamba. The script provided in the github will create a folder in your home directory (~/…) called “conda” with all the necessary files for running a conda environment.

IMPORTANT: if you want to do a clean installation, you must delete the conda folder in your home directory from your previous mcclintock installation or else this step may cause some errors. You can check on your installation of conda (which is likely in your home directory) by

```
cd ~
ls
```
and if you see conda as one of your directories listed, then you'll want to delete it to get a clean installation
```
rm -rf conda
```

Next, run this code in your terminal (you can copy, paste, and run the whole thing or run the code line by line):

```
wget -O Miniforge3.sh 
"https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
bash Miniforge3.sh -b -p "${HOME}/conda" 
source "${HOME}/conda/etc/profile.d/conda.sh"
source "${HOME}/conda/etc/profile.d/mamba.sh
conda init
```
These lines of code checks what kind of operating system and architecture you have and automatically downloads the conda package for your OS. 
Afterwards, it will create a directory called “conda” in your home directory that will contain the mamba and conda files. 
This is what it should look like when you `ls`, you should have 
```
yourname@cluster:~$ ls
conda
```

#### Clone Mcclintock from Github
Run this command in your terminal while in the directory that you want your mcclintock folder to be in. 

```
git clone git@github.com:bergmanlab/mcclintock.git
cd mcclintock
```

#### Create Mcclintock Conda Environment
Install base dependencies that you need in order to run the Mcclintock scripts. Run this command in the terminal.

```
mamba env create -f install/envs/mcclintock.yml --name mcclintock
```
After this is completed, activate your conda environment. You’ll have to do this every time you want to use mcclintock.
```
conda activate mcclintock
```

#### Install Conda Environments for each component method used in Mcclintock
We need to install scripts and create specialized conda environments for each of component methods used in mcclintock (some methods use python 2.9 while others use python 3.5 so we need different conda environments to run them)

Run this command in the terminal to install the scripts (this may take a while)
```
python3 mcclintock.py --install
```

#### (OPTIONAL) Double Checking installation using test data (if your installation is not working as intended, this is a good way to check if your mcclintock scripts behave correctly)

To make sure that there are no issues with your installation, you could optionally check the functionality of the mcclintock scripts by running it on some test data that Mcclintock provides from their github. 

While in the mcclintock directory in the terminal, run this command:
```
python test/download_test_data.py
```
WARNING: Downloading the test data (especially the fastq files) may error out for some reason and you may only get only 1 fastq file (only downloaded SRR800842_1.fastq.gz but was unable to download SRR800842_2.fastq.gz ). In this case, just run the python test/download_test_data.py command in the terminal again and the script should recognize that it will only need to download the other fastq.gz file. 

After that, you should have all of your test data downloaded. To test your mcclintock installation, you could run the mcclintock.py script on the terminal; however, this script does take a few hours to run, so writing a shell script and qsub-ing is recommended. 

Here is an example script that takes advantage of SnakeMake to speed up our results via parallel processing. 

```
#!/bin/bash
#$ -wd /path/to/working/directory
#$ -o /path/to/outputs/
#$ -e /path/to/errors/
#$ -pe serial 5
#$ -l mfree=16G
#$ -l h_rt=10:0:0

MCDIR=/path/to/mcclintock

mkdir test_output
cd test_output

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
   -1 ${MCDIR}/test/SR800842_1.fastq.gz \
   -2 ${MCDIR}/test/SR800842_2.fastq.gz \
   -p 5 

conda deactivate
```

After the script has finished executing, the working installation of mcclintock should produce a results file under: `path/to/test_output/SRR800842_1/results/summary/data/run/summary_report.txt`
It should have something like with perhaps a few differences in numbers: 
```
----------------------------------
MAPPED READ INFORMATION
----------------------------------
read1 sequence length:  94
read2 sequence length:  94
read1 reads:            18547823
read2 reads:            18558412
median insert size:     302
avg genome coverage:    268.201
----------------------------------

-----------------------------------------------------
METHOD          ALL       REFERENCE    NON-REFERENCE 
-----------------------------------------------------
ngs_te_mapper   35        21           14            
ngs_te_mapper2  87        49           38            
relocate        80        63           17            
relocate2       139       41           98            
temp            365       311          54            
temp2           311       311          0             
retroseq        58        0            58            
popoolationte   142       130          12            
popoolationte2  189       164          25            
te-locate       714       165          549           
teflon          414       390          24            
tebreak         61        0            61            
-----------------------------------------------------

```
You can also check `path/to/mcclintock/test/expected_results/summary_report.txt` to see the exact expected results and compare it to your test results as well. 

#### Running Scripts on Samples:
As of right now, the simplest way to use Mcclintock on your samples would simply be to use a script similar to the example script above and qsub on the cluster. You can use the transposons_batch.sh and modify it to match your paths. 

You could also just run the python command in your terminal as long as you are in the mcclintock directory. Just remember that you would need to keep the terminal open while the script is potentially running for a few hours. 
```
#run mcclintock with your samples
python3 mcclintock.py \
   -r /test/sacCer2.fasta \
   -c /test/sac_cer_TE_seqs.fasta \
   -g /test/reference_TE_locations.gff \
   -t /test/sac_cer_te_families.tsv \
   -1 /path/to/first/fastq \
   -2 /path/to/second/fastq \
   -p 5
```
If you are unable to see your results, try checking to see if you set your work directory to your expected path.

#### Citations for Mcclintock
Check out the [Mcclintock Github](https://github.com/bergmanlab/mcclintock) for citation details

## Usage
Start by cloning the yeast_transposon_pipeline(ONLY IF THE REPO IS PUBLIC). You can do this by typing 
```
git clone https://github.com/leahmarieanderson/yeast_transposon_pipeline.git
```
else, you'll need to just copy the yeast_transposon_pipeline directory from Leah or Zilong.

Make sure that your target destination for your `cp` command is your work directory. It should be the directory that contain your fastq directory as well as your `mcclintock` directory
```
└── WorkDirectory <-- *THIS ONE*
    ├── ...
    ├── mcclintock
    └── fastq
        ├── sample1_R1_001.fastq.gz
        ├── sample1_R2_001.fastq.gz
        ├── sample2_R1_001.fastq.gz
        └── sample2_R2_001.fastq.gz
```
Just run this command while on the cluster.
```
cp /net/dunham/vol2/Zilong/updating_pipeline_2024/yeast_transposon_pipeline path/to/WorkDirectory
```
Your work directory should now have the yeast_transposon_pipeline directory with the main scripts being `output_organizer.py`, `tn_batch_runner.py`, and `transposon_batch.sh`. It should look like this:
```
└── WorkDirectory
    ├── ...
    ├── yeast_transposon_pipeline
        ├── ...
        ├── output_organizer.py
        ├── tn_batch_runner.py
        └── transposon_batch.sh
    ├── mcclintock
    └── fastq
        ├── sample1_R1_001.fastq.gz
        ├── sample1_R2_001.fastq.gz
        ├── sample2_R1_001.fastq.gz
        └── sample2_R2_001.fastq.gz
```

Now all you would have to do is run 
```
python3 tn_batch_runner.py path/to/work/directory 
```
or if you wanted to run the transposon pipeline of another fastq folder with a different name besides `fastq`, you can add another argument to the python command.
```
└── WorkDirectory
    ├── ...
    ├── yeast_transposon_pipeline
    ├── mcclintock
    └── TE_fastq * different name from "fastq"*
```
Then you would run the command with `TE_fastq` as an additional argument.
```
python3 tn_batch_runner.py path/to/work/directory TE_fastq
```

As long as your files are organized in the way that is shown in the images above, this will result in an output that looks like this:
```
└── WorkDirectory
    ├── ...
    ├── yeast_transposon_pipeline
    ├── transposons <-- *NEW*
        ├── sample1 *click into sample1 to view results*
            ├── sample1_R1_001 *check here for full details on output*
            ├── logs
            ├── nonredundant_vcfs *check here for nonredundant-nonreference-siteonly.vcfs*
            ├── sacCer2 
            └── snakemake
        └── sample2
    ├── mcclintock
    └── fastq
```
You can check out the new `transposons` directory to view your results. You can look into each sample and get full details on each of mcclintock's method's results. The `nonredundant_vcfs` directory contains a collection of all of the nonredundant-nonreference-siteonly vcfs from each of the methods. 


