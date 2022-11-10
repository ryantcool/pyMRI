# pyMRI
  
A script to easily extract meta-data from dicom files utilizing pydicom.

#### Usage:

 `>$ python3 pyMRI.py <option>  </absolute/path/to/DICOM_folder/>`
  
#### Options: 
*  -h or --help for usage menu
*  -c to create sequence parameter txt files
*  -i to view info on sequence
*  -n to list mr number (for Yale, scans are identified by their MR number - located in the PatientID field -, i.e. PB1234 where PB would be the initials of the scanner used, such as Prisma B)
*  -s to list sequences

