import shutil
import os
from pathlib import Path
import time
import threading


start_bannner = '''
    __________   __  ___  __  ____________      __  _____  __   ____  ___   ___  _______ 
   / ___/ __/ | / / / _ |/ / / /_  __/ __ \____/ / / / _ \/ /  / __ \/ _ | / _ \/ __/ _ \ 
 _/ /___\ \ | |/ / / __ / /_/ / / / / /_/ /___/ /_/ / ___/ /__/ /_/ / __ |/ // / _// , _/
(_)___/___/ |___/ /_/ |_\____/ /_/  \____/    \____/_/  /____/\____/_/ |_/____/___/_/|_|                                                                                                                                                                                         
'''

print(start_bannner)

time.sleep(1)
print("Initializing and locating CSV files...")
print("")

# Get the current user's home directory
home_dir = Path.home()

# Define the destination directory, adjust the path as needed for consistency across users
dest_dir = os.path.join(home_dir, "Kennesaw State University", "Team-KS7 C E - Documents", "Data Acquisition and Code", "_AutoUploadedLogs")

# Check if the destination directory exists
if not os.path.exists(dest_dir):
    print(f"Error: Destination directory does not exist: {dest_dir}")
    print("Please create the directory and try again.")
    exit(1)  # Exit the script with an error code

# Create a dictionary of existing files in the destination directory with their sizes
existing_files = {f: os.path.getsize(os.path.join(dest_dir, f)) for f in os.listdir(dest_dir) if f.endswith('.csv') or f.endswith('.CSV')}

# Get the root directory of the drive where the script is located
root_dir = Path('/').resolve()

# Initialize an empty list to hold the paths of .csv files
csv_files = []

# Walk through the directory tree starting from the root directory
for dirpath, dirnames, filenames in os.walk(root_dir):
    if dirpath.lower().startswith('c:'):
        print("bro this isn't a good idea, you don't want me searching your entire drive- cancelling...")
        print("please move the logs to a usb, sd card, cd, anything not the C: drive and try again")
        print("")
        break

    for filename in filenames:
        # Skip the file named 'dlsnetparams.csv' (case-insensitive check)
        if filename.lower() == 'dlsnetparams.csv':
            continue  # Skip this file and move to the next one

        if filename.lower().endswith('.csv'):  # This handles case sensitivity
            file_path = os.path.join(dirpath, filename)
            # Check if the file is a duplicate based on name and size
            if filename in existing_files and os.path.getsize(file_path) == existing_files[filename]:
                print(f"Duplicate found, skipping {filename}...")
            else:
                csv_files.append(file_path)

# Check if any .csv files were found
if len(csv_files) == 0:
    print("No new CSVs found, please double check the directory!")
else:
    print(f"Found {len(csv_files)} new CSV file(s):")
    for file in csv_files:
        print(os.path.basename(file))

time.sleep(2)
print("")

# Copy each new .csv file to the destination directory
for src_file_path in csv_files:
    print("Beginning to copy new CSV files...")
    print("")
    
    filename = os.path.basename(src_file_path)
    dest_file_path = os.path.join(dest_dir, filename)
    
    # Print starting message
    print(f"Starting to copy {filename}...")
    
    # Copy the file
    shutil.copy(src_file_path, dest_file_path)
    
    # Print finished message
    print(f"Finished copying {filename}.")
    
    # Verify the file was copied
    if os.path.exists(dest_file_path):
        print(f"Verification successful: {filename} was copied.")
    else:
        print(f"Verification failed: {filename} was not copied.")

print("")

def exit_program():
    input("Uploading complete. Press ENTER to exit or exit automatically in 15 seconds...")
    os._exit(0)  # Forcefully exits the program

# Start a thread that waits for the user to press ENTER
exit_thread = threading.Thread(target=exit_program)
exit_thread.daemon = True  # This ensures the thread will not prevent the program from exiting
exit_thread.start()

time.sleep(15)  # Wait for 15 seconds before automatically exiting