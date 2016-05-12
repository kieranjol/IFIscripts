import sys
import subprocess
import os
from glob import glob

starting_dir = sys.argv[1]
csv_report_filename = os.path.basename(starting_dir) + "_report"
csv_report = os.path.expanduser("~/Desktop/%s.csv") % csv_report_filename 
print csv_report

checkfile = os.path.isfile(csv_report)

print checkfile

if checkfile == True:
    print "CSV file already exists."
elif checkfile == False:
    print "No CSV file exists."
    
    
"""
As-11 Fixity

1. Import all relevant modules
2. Define path to starting folder
3. Check if CSV report already exists
4. Allow option to overwrite
5. Define name for CSv file
6. Create CSV file with headings
7. Search through folders to verify if more than 1 file exists
8. If more that 1 file exists check if MXF and XML
9. Check if same filename
10. Check if folder is empty, note in CSV report 
11. If only MXF, note in CSV report. MXF FILENAME + "No sidecar"
12. Extract MD5 from xml file and store as variable
13. Generate MD5 checksum on MXF file
14. Compare the 2 MD5s
15. Write to CSV report

"""
