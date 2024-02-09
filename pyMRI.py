#!/usr/bin/env python3

import sys
import os
import pydicom
import magic
from tqdm import tqdm
import time

usage = """
USAGE: python3 pyMRI.py <option>  </absolute/path/to/DICOM_folder/>


OPTIONS:
-h or --help for usage menu
-c to create sequence parameter txt files
-i to view info on sequence
-n to list mr number
-s to list sequences
"""

seq_dict = {}
mr_files = []

def mr_number(subj):
    os.chdir(subj)
    get_mr_files(os.listdir())
    return "MR Number is: " + pydicom.filereader.dcmread(mr_files[0]).PatientID


def get_mr_files(list):
    for i in list:
        if not os.path.isdir(i) and magic.from_file(i) == "DICOM medical imaging data":
            mr_files.append(i)


def seq_file_org(file):
    # Chooses which to use for seq_name based off of flag given
    if sys.argv[1] == "-c":
        # Sets name to literal file name
        seq_name = file
    elif sys.argv[1] == "-s" or sys.argv[1] == "-i":
        # Sets name to output of SeriesDescription (i.e. Sag_3D_MPRAGE)
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
    get_mr_files(os.listdir())
    [seq_file_org(i) for i in tqdm(mr_files)]
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
                    print(pydicom.filereader.dcmread(i))
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


def create_seq_txt(subj):
    subj_path = subj
    os.chdir(subj_path)
    sub_id = pydicom.filereader.dcmread(os.listdir()[0]).PatientID
    series_dir = str(sub_id + "_seriesinfo")
    if os.path.exists(subj_path + "/" + series_dir):
        return "Looks like: " + series_dir + " already exists"
    else:
        os.mkdir(series_dir)
        get_mr_files(os.listdir())
        with concurrent.futures.ThreadPoolExecutor() as executor:
            list(tqdm(executor.map(seq_file_org, mr_files), total=len(mr_files)))
        for i in sorted(seq_dict.items()):
            file = str(str(i[0]) + "_" + str(pydicom.filereader.dcmread(i[1]).SeriesDescription) + ".txt")
            with open(str(series_dir + "/" + file), "a") as f:
                f.write(str(pydicom.filereader.dcmread(i[1])))
    print("\nFiles created at: " + subj_path + series_dir + "\n")
    return 'Completed Successfully!'


def main():
    help_flags = ["-h", "--help"]
    options = {"-s": seq_listr, "-n": mr_number, "-i": get_seq_info, "-c": create_seq_txt}
    try:
        if len(sys.argv) > 1:
            arg1 = sys.argv[1]
            if arg1 in help_flags:
                print(usage)
            elif arg1 in options.keys():
                print(options[arg1](sys.argv[2]))
            elif arg1 not in options.keys():
                print(usage)
        else:
            print("\nIncorrect usage. See below:\n\n", usage)
    except Exception as e:
        print(e)
        print("\n\n", usage)


if __name__ == "__main__":
    main()
