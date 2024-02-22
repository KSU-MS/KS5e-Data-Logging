import logging
import cantools
from cantools.database import Database
import subprocess
import sys
import os
import re
sys.stdout.write = logging.info
def convert_can_logs(input_file, output_file, output_file_path="./motec_formatted_logs"):
    if not os.path.exists(output_file_path):
        os.makedirs(output_file_path)
    with open(input_file, 'r') as f_in, open(os.path.join(output_file_path,output_file), 'w') as f_out:
        first_line = True
        for line in f_in:
            if first_line:
                first_line=False
                continue
            parts = line.strip().split(',')
            timestamp_sec = float(parts[0]) / 1000  # Convert milliseconds to seconds
            msg_id = parts[1]
            msg_len = int(parts[2])
            data = parts[3]

            # Convert message ID and length to hexadecimal format
            msg_id_hex = f'{int(msg_id, 16):X}'
            msg_len_hex = f'{msg_len:X}'

            # Modify the format of the data section
            data_formatted = data

            # Write the converted log entry to the output file
            f_out.write(f'({timestamp_sec:.6f}) can0 {msg_id_hex.zfill(3)}#{data_formatted}\n')
    return output_file

def strip_invalid_filename_chars(filename):
    # Define the regex pattern for invalid characters
    pattern = r"[\/\\\:\*\?\"\<\>\|\n]"

    # Replace invalid characters with an empty string
    return re.sub(pattern, "", filename)


def cantools_plot_csv(input_file,dbc:Database,plotargs):
    dbcfilename = dbc.version+'.dbc'
    dbcfilename = strip_invalid_filename_chars(dbcfilename)

    with open(dbcfilename,mode="w") as dbcfil:
        cantools.db.dump_file(dbc,dbcfilename)
        
    file = convert_can_logs(input_file=input_file,output_file=(input_file+".log"))

    exit_status = subprocess.call(
        ['python','-m','cantools','plot',dbcfilename,plotargs],
        stdin=open(file=file)
    )
    return exit_status
if __name__ == "__main__":
    file = sys.argv[1]
    argsz = sys.argv[2]
    dbc=sys.argv[3]
    logging.info(f"plotter args: {sys.argv}")
    logging.info(f"plotter script success: {cantools_plot_csv(file,dbc,argsz)}")