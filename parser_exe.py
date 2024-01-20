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
print("Beginning CSV to CSV parsing...")
print("Select a folder which contains the raw logs to be parsed")
parse_folder(select_folder_and_get_path())
print("Finished CSV to CSV parsing.")
print("----------------------------------------------------------------------------------")
print("Beginning CSV to MAT parsing...")
create_mat()
print("Finished CSV to MAT parsing.")
print("----------------------------------------------------------------------------------")
print("SUCCESS: Parsing Complete.")
input("press enter to exit")