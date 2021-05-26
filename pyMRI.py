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
-s to list sequences
-i to view info on sequence
-n to list mr number

"""

seq_dict = {}
files_lst = []

def mr_number(subj):
    return "MR Number is: " + pydicom.filereader.dcmread(subj + os.listdir(subj)[0]).PatientID


def seq_file_org(file):
    seq_name = pydicom.filereader.dcmread(file).SeriesDescription
    seq_num = pydicom.filereader.dcmread(file).SeriesNumber
    if seq_num not in seq_dict.keys():
        seq_dict[seq_num] = seq_name

def seq_listr(subj):
    os.system("clear")
    print("\n*******************************")
    print("* Compiling list of seqeunces *")
    print("*******************************\n")
    start = time.time()
    os.chdir(subj) 
    with concurrent.futures.ThreadPoolExecutor() as executor:
        list(tqdm(executor.map(seq_file_org, os.listdir()), total=len(os.listdir())))
    end = time.time()
    print('\nThis subject had these runs done:\n\n')
    print(*(' '.join(map(str, x)) for x in sorted(seq_dict.items())), sep='\n')
    print(f'\nTime taken: {end - start:.2f}s\n')
    return 'Completed Successfully!\n'

def get_seq_info(subj):
    seq_listr(subj)
    print("****************************************************")
    print("* Which number sequence would you like to look up? *")
    print("****************************************************")
    seq_select = input("\n: ")
    seq_of_int = seq_dict[int(seq_select)]
    print("\n**********************************************")
    print("* Which parameter would you like to look up? *")
    print("**********************************************\n")
    print("\ntype full for all info\n\nor\n\npress enter if not sure")
    param_select = input(": ")
    parameters = [i for i in dir(pydicom.filereader.dcmread(os.listdir()[0])) if i[0].isupper()]
    while param_select not in parameters:
        if param_select.lower() == "full":
            for i in os.listdir():
                if pydicom.filereader.dcmread(i).SeriesDescription == seq_of_int:
                    print(pydicom.filereader.dcmread(i),"\n")
                    return 'Completed Successfully\n'
        else:
            os.system("clear")
            print("************************")
            print("* Queryable parameters *")
            print("************************\n")
            print(parameters)
            print("\n\n*********************")
            print("* Enter a parameter *")
            print("*********************\n")
            param_select = input(": ")
               
    for i in os.listdir():
        if pydicom.filereader.dcmread(i).SeriesDescription == seq_of_int:
            value = getattr(pydicom.filereader.dcmread(i), param_select)
            print("\n", param_select, "is:", value, "\n")
            return 'Completed Successfully!'


def main():
    help_flags = ["-h", "--help"]
    options = {"-s": seq_listr,  "-n": mr_number, "-i": get_seq_info}
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
