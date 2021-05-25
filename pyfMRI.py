import sys
import os
import pydicom
import glob
from tqdm import tqdm
import concurrent.futures
import time

usage ="""
usage: python3 main_mr.py OPTION /PATH/TO/DICOM_FOLDER

OPTIONS: 

-h or --help for usage menu
-seq to list sequences
-num to list mr number

"""

seq_dict = {}
files_lst = []

def mr_number(subj):
    for i in os.listdir(subj):
	    if i.startswith('MR') is True:
	        files_lst.append(i)
	        if len(files_lst) > 0: break
    return "MR Number is: " + pydicom.filereader.dcmread(subj + files_lst[0]).PatientID


def seq_file_org(file):
    if file.startswith('MR' or 'SC'):
        seq_name = pydicom.filereader.dcmread(file).SeriesDescription
        seq_num = pydicom.filereader.dcmread(file).SeriesNumber
        if seq_num not in seq_dict.keys():
            seq_dict[seq_num] = seq_name

def seq_listr(subj):
    start = time.time()
    os.chdir(subj) 
    with concurrent.futures.ThreadPoolExecutor() as executor:
	    list(tqdm(executor.map(seq_file_org, os.listdir()), total=len(os.listdir())))
    end = time.time()
    print('\nThis subject had these runs done:\n\n')
    print(*(' '.join(map(str, x)) for x in sorted(seq_dict.items())), sep='\n')
    print(f'\nTime taken: {end - start:.2f}s\n')
    return 'Completed Successfully!'

def main():
    help_flags = ["-h", "--help"]
    options = {"-seq": seq_listr,  "-num": mr_number}
    try:
        if len(sys.argv) > 1:
            arg1 = sys.argv[1]
            if arg1 in help_flags:
                print(usage)
            elif arg1 in options.keys():
                print(options[arg1](sys.argv[2]))
            elif arg1 not in options.keys():
                print("\nIncorrect usage. See below:\n\n", usage)
    except Exception as e:
        print(e)
        print("\n\n", usage)
	
	
if __name__ == "__main__":
    main()
