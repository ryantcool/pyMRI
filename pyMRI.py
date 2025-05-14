#!/usr/bin/env python3

import asyncio
import io
import os
import sys
import time

import aiofiles
import magic
import pydicom
from tqdm import tqdm

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

# Variables for async i/o
seq_dict_lock = asyncio.Lock()
semaphore = asyncio.Semaphore(10)  # caps asyncio at 10 files


def mr_number(subj):
    os.chdir(subj)
    get_mr_files(os.listdir())
    return "MR Number is: " + pydicom.dcmread(mr_files[0]).PatientID


def get_mr_files(list):
    for i in list:
        if (
            not os.path.isdir(i)
            and magic.from_file(i) == "DICOM medical imaging data"
        ):
            mr_files.append(i)


async def seq_file_org(file, progress_bar: tqdm):
    async with semaphore, aiofiles.open(file, mode="rb") as f:
        dicom_data = await f.read()
    dicom_file_like = io.BytesIO(dicom_data)
    dicom_obj = pydicom.dcmread(dicom_file_like)
    seq_name = (
        dicom_obj.SeriesDescription
        if sys.argv[1] == "-s" or sys.argv[1] == "-i"
        else file
    )
    seq_num = dicom_obj.SeriesNumber
    async with seq_dict_lock:
        if seq_num not in seq_dict:
            seq_dict[seq_num] = seq_name
    progress_bar.update(1)


async def process_files(subj):
    os.chdir(subj)
    get_mr_files(os.listdir())
    with tqdm(
        total=len(mr_files), desc="Processing DICOM files", unit="file"
    ) as progress_bar:
        tasks = [seq_file_org(dcm, progress_bar) for dcm in mr_files]
        await asyncio.gather(*tasks)


def seq_listr(subj):
    os.system("clear")
    print("\n*******************************")
    print("* Compiling list of seqeunces *")
    print("*******************************\n")
    start = time.time()
    asyncio.run(process_files(subj))
    end = time.time()
    print("\nThis subject had these runs done:\n\n")
    print(*(" ".join(map(str, x)) for x in sorted(seq_dict.items())), sep="\n")
    print(f"\nTime taken: {end - start:.2f}s\n")
    return "Completed Successfully!\n"


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
    parameters = [
        i for i in dir(pydicom.dcmread(os.listdir()[0])) if i[0].isupper()
    ]
    while param_select not in parameters:
        if param_select.lower() == "full":
            for i in os.listdir():
                if pydicom.dcmread(i).SeriesDescription == seq_of_int:
                    print(pydicom.dcmread(i))
                    return "Completed Successfully\n"
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
        if pydicom.dcmread(i).SeriesDescription == seq_of_int:
            value = getattr(pydicom.dcmread(i), param_select)
            print("\n", param_select, "is:", value, "\n")
            return "Completed Successfully!"


def create_seq_txt(subj):
    subj_path = subj
    sub_id = pydicom.dcmread(
        subj_path + "/" + os.listdir(subj_path)[0]
    ).PatientID
    series_dir = str(sub_id + "_seriesinfo")
    if os.path.exists(subj_path + "/" + series_dir):
        return "Looks like: " + series_dir + " already exists"
    else:
        os.mkdir(subj_path + "/" + series_dir)
        seq_listr(subj)
        for index, dcm_file in sorted(seq_dict.items()):
            series_description = pydicom.dcmread(dcm_file).SeriesDescription
            file_name = f"{index}_{series_description}.txt"
            with open(f"{series_dir}/{file_name}", "a") as f:
                f.write(str(pydicom.dcmread(dcm_file)))
    print(f"\nFiles created at: {subj_path}/{series_dir}\n")
    return "Completed Successfully!"


def main():
    help_flags = ["-h", "--help"]
    options = {
        "-s": seq_listr,
        "-n": mr_number,
        "-i": get_seq_info,
        "-c": create_seq_txt,
    }
    try:
        if len(sys.argv) > 1:
            arg1 = sys.argv[1]
            if arg1 in help_flags:
                print(usage)
            elif arg1 in options:
                print(options[arg1](sys.argv[2]))
            elif arg1 not in options:
                print(usage)
        else:
            print("\nIncorrect usage. See below:\n\n", usage)
    except Exception as e:
        print(e)
        print("\n\n", usage)


if __name__ == "__main__":
    main()
