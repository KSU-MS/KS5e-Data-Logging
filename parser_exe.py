import sys
sys.path.insert(1, "../telemetry_parsers")
from parser_api import *
from folder_selection_utils import select_folder_and_get_path
########################################################################
# Entry Point to Framework
########################################################################
print("Welcome to KSU motorsports parser")
print("The process will be of two parts: CSV to CSV parsing, and then CSV to MAT parsing.")
print("----------------------------------------------------------------------------------")
print("Looking for dbc-files folder: ")
if not os.path.exists("dbc-files"):
    print("FATAL ERROR: 'dbc-files' folder was not found.")
    print("please select the folder with dbc files to use for parsing...")
    dbc_files_path=select_folder_and_get_path()
elif os.path.exists("dbc-files"):
    print("dbc-files found")
    dbc_files_path = ('dbc-files')
    
dbc_file = get_dbc_files(dbc_files_path)
print("Beginning CSV to CSV parsing...")
print("Select a folder which contains the raw logs to be parsed")
parse_folder(select_folder_and_get_path(),dbc_file=dbc_file)
print("Finished CSV to CSV parsing.")
print("----------------------------------------------------------------------------------")
print("Beginning CSV to MAT parsing...")
create_mat()
print("Finished CSV to MAT parsing.")
print("----------------------------------------------------------------------------------")
print("SUCCESS: Parsing Complete.")
input("press enter to exit")