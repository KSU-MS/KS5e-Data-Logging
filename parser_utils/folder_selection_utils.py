import platform
import os
import tkinter as tk
from tkinter import filedialog
import logging
import parser_utils.parser_logger as parser_logger
def select_folder_and_get_path():
    root = tk.Tk()
    root.attributes("-topmost", True)
    root.withdraw()  # Hide the main window

    folder_path = filedialog.askdirectory()
    
    if folder_path:
        logging.info(f"Selected folder path: {folder_path}")
        return folder_path
    else:
        logging.warning("No folder selected")
        return None

def select_folder_and_get_path_dbc():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    root.attributes("-topmost", True)
    folder_path = filedialog.askdirectory()
    
    if folder_path:
        logging.info(f"Selected folder path: {folder_path}")
        return folder_path
    else:
        logging.warning("No folder selected")
        return None
    
def open_path(path):
    system = platform.system()
    if system == 'Windows':
        logging.debug("detected that operating system is Windows")
        os.system(f'start "" "{path}"')
    elif system == 'Linux':
        logging.debug("detected that operating system is Linux")
    elif system == 'Darwin':
        os.system(f"xdg-open {path}")  
    else:
        logging.error("Unknown operating system")
    
# # Call the method to select a folder and get its path
# selected_folder_path = select_folder_and_get_path()

# if selected_folder_path:
#     # Use the selected folder path for further operations
#     pass
