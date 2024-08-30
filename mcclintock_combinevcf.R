library(data.table)
library(stringr)
library(dplyr)

#set to work in the directory where the files are or readdata will fail
setwd("~/Documents/Research/dunham/freeze_thaw_evolution/jan2024_FTevo/transposons/Z/")

#get all the files from this directory
all_files <- list.files(path = ".", pattern = ".vcf")

#function to read in without the long header
#and add sample name and tool (from file name) as columns
readdata <- function(fn){
  dt_temp <- fread(fn, sep="\t", header = TRUE, skip = '#CHROM') %>%
    #cbind(sample=str_extract(fn, "(?<=caffeine_).+(?=_R1)")) %>%
    cbind(sample=str_extract(fn, ".+(?=_R1)")) %>%
    cbind(tool=str_extract(fn, "(?<=001_).+(?=_nonredundant)"))
  return(dt_temp)
}

#apply function to these files and append together
mylist <- lapply(all_files, readdata)
all_te <- rbindlist(mylist, fill=T)
colnames(all_te)[1] <- "CHROM" #get rid of annoying # in name

#make a variable of chr:pos to use to id repeated tes
all_te$location <- cbind(location = paste(all_te$CHROM, all_te$POS, sep=":"))

#take the ancestor into separate df
anc_te <- subset(all_te, sample == "anc") #change if ancestor file has different name

#filter out ancestral tes
ancfilt_te <- filter(all_te, !location %in% anc_te$location)

#for each sample, keep only if appear in >=3 tools (location shows up 3 or more times)
repl_te_3 <- ancfilt_te %>%
  group_by(sample, location) %>%
  filter(n() >= 3)

write.table(repl_te_3, file="Z20_filtered_te.txt", sep="\t", row.names = F)

#keep just one, regardless of tool
repl_te_uniq <- repl_te_3 %>%
  group_by(sample) %>%
  distinct(location, .keep_all=T)

write.table(repl_te_uniq, file="Z20_filtered_te_uniq.txt", sep="\t", row.names = F)
