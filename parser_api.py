########################################################################
########################################################################
# Raw Data CSV to Parsed Data CSV Code Section
########################################################################
########################################################################


"""
TODO: update this workflow to be accurate with dbc parsing methods
parse_folder --> parse_file --> parse_time
                            --> parse_message --> parse_ID_XXXXXXXXX
"""

# Imports
import os
import sys
from datetime import datetime
import cantools
import pandas as pd
import csv
import tempfile
import shutil

DEBUG = False # Set True for option error print statements

def get_dbc_files(path_name='dbc-files') -> cantools.db.Database:
    # Get all the DBC files for parsing and add them together
    try:
        path_name = path_name
        file_path = []
        file_count = 0
        for root, dirs, files in os.walk(path_name, topdown=False):
            for name in files:
                if ".dbc" in name or ".DBC" in name:
                    fp = os.path.join(root, name)
                    file_path.append(fp)
                    file_count += 1
    except:
        print('FATAL ERROR: dbc scraping failed')
        print('get_dbc_files('+path_name+')')
        input("press enter to exit")
        sys.exit(0)
    mega_dbc=cantools.database.Database()
    for filename in file_path:
        with open (filename, 'r') as newdbc:
            mega_dbc.add_dbc(newdbc)

    print('Step 1: found ' + str(file_count) + ' files in the dbc-files folder')
    return mega_dbc

def print_all_the_shit_in_dbc_file(db):
    dbc_ids=[]
    for message in db.messages:
        # print(str(vars(message)) + "\n")
        dbc_ids.append(message.frame_id)
        # print(str(message.name)+" ID: "+str(message.frame_id)+" Note: "+str(message.comment))
        # print("\tsignals: ")
        # for signal in message.signals:
            # print("\t\t"+ signal.name)
    return dbc_ids

def parse_message(id, data, db,dbc_ids,unknown_ids):
    labels=[]
    values=[]
    units=[]
    if int(id,16) in dbc_ids:
        actual_message = db.get_message_by_frame_id(int(id,16))
        for signal in actual_message.signals:
            units.append(str(signal.unit))
        parsed_message = db.decode_message(int(id,16),bytearray.fromhex(data),decode_choices=False)
        for i in parsed_message:
            message_label = str(i)
            labels.append(message_label)
            values.append(str(parsed_message[i]))
        message_name = actual_message.name
        return [message_name,labels,values,units]
    if (id not in unknown_ids) & (int(id,16) not in dbc_ids):
        unknown_ids.append(id)
    return "INVALID_ID"

def parse_message_better(id, data, db,dbc_ids,unknown_ids):
    if int(id,16) in dbc_ids:
        parsed_message = db.decode_message(int(id,16),bytearray.fromhex(data),decode_choices=False)
        return parsed_message
    if (id not in unknown_ids) & (int(id,16) not in dbc_ids):
        unknown_ids.append(id)
    return "INVALID_ID"

def parse_time(raw_time):
    '''
    @brief: Converts raw time into human-readable time.
    @input: The raw time given by the raw data CSV.
    @return: A string representing the human-readable time.
    '''
    ms = int(raw_time) % 1000
    raw_time = int(raw_time) / 1000
    time = str(datetime.utcfromtimestamp(raw_time).strftime('%Y-%m-%dT%H:%M:%S'))
    time = time + "." + str(ms).zfill(3) + "Z"
    return time
def parse_used_ids(filename,dbc_for_parsing,dbc_ids,unknown_ids):
    header_list = ["Time"]
    infile = open(filename, "r")
    flag_first_line=True
    for line in infile.readlines():
        if flag_first_line:
            flag_first_line = False
        else:
            raw_id = line.split(",")[1]
            length = line.split(",")[2]
            raw_message = line.split(",")[3]
            if length == 0 or raw_message == "\n":
                continue
            raw_message = raw_message[:(int(length) * 2)] # Strip trailing end of line/file characters that may cause bad parsing
            raw_message = raw_message.zfill(16) # Sometimes messages come truncated if 0s on the left. Append 0s so field-width is 16.
            current_message = parse_message_better(raw_id,raw_message,dbc_for_parsing,dbc_ids,unknown_ids)
            if current_message != "INVALID_ID":
                for i in current_message:
                    if i not in header_list:
                        header_list.append(i)
    return header_list

def delete_lines_containing_string(input_file, specified_string):
    # Create a temporary file to write the filtered content
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, newline='', encoding='utf-8')

    with open(input_file, 'r', newline='', encoding='utf-8') as infile:
        reader = csv.reader(infile)
        writer = csv.writer(temp_file)

        for row in reader:
            # Check if the specified string is present in the row
            if specified_string not in ','.join(row):
                writer.writerow(row)

    # Close the temporary file
    temp_file.close()

    # Replace the original file with the temporary file
    shutil.move(temp_file.name, input_file)

def parse_file(filename,dbc):
    '''
    @brief: Reads raw data file and creates parsed data CSV.
            Loops through lines to write to parsed datafile.
            Calls the parse_message and parse_time functions as helpers.
    @input: The filename of the raw and parsed CSV.
    @return: N/A
    '''
    print("start parsing: "+filename)
    # Delete any lines that contain this blank glitchy CAN message of ID 0 and data 0
    specified_string = ',0,8,0000000000000000'  # Replace with the specified string to be removed
    delete_lines_containing_string(filename,specified_string)

    # Array to keep track of IDs we can't parse

    unknown_ids = []
    # Array to keep track of IDs we CAN parse
    dbc_ids = print_all_the_shit_in_dbc_file(dbc)
    header_list = parse_used_ids(filename,dbc,dbc_ids,unknown_ids)
    # Miscellaneous shit lol
    nextline = [""] * len(header_list)
    header_string=",".join(header_list)


    infile = open(filename, "r")
    outfile = open("temp-parsed-data/" + filename, "w")
    outfile2 = open("parsed-data/parsed" + filename, "w")

    flag_second_line = True
    flag_first_line = True
    last_time=''
    for line in infile.readlines():
        # On the first line, do not try to parse. Instead, set up the CSV headers.
        if flag_first_line:
            flag_first_line = False
            outfile.write("time,id,message,label,value,unit\n")
            outfile2.write(header_string+"\n")
        # Otherwise attempt to parse the line.
        else:
            raw_time = line.split(",")[0]
            raw_id = line.split(",")[1]
            length = line.split(",")[2]
            raw_message = line.split(",")[3]

            # Do not parse if the length of the message is 0, otherwise bugs will occur later.
            if length == 0 or raw_message == "\n":
                continue
            
            # Call helper functions
            time = parse_time(raw_time)
            raw_message = raw_message[:(int(length) * 2)] # Strip trailing end of line/file characters that may cause bad parsing
            raw_message = raw_message.zfill(16) # Sometimes messages come truncated if 0s on the left. Append 0s so field-width is 16.
            # Get actual message, referencing our DBC file and ID lists
            table = parse_message(raw_id, raw_message,dbc,dbc_ids,unknown_ids)

            if table == "INVALID_ID" or table == "UNPARSEABLE":
                continue

            # Assertions that check for parser failure. Notifies user on where parser broke.
            assert len(table) == 4, "FATAL ERROR: Parser expected 4 arguments from parse_message at ID: 0x" + table[0] + ", got: " + str(len(table))
            assert len(table[1]) == len (table[2]) and len(table[1]) == len(table[3]), "FATAL ERROR: Label, Data, or Unit numbers mismatch for ID: 0x" + raw_id
            
            # Harvest parsed datafields and write to outfile.
            message = table[0].strip()
            for i in range(len(table[1])):
                label = table[1][i].strip()
                value = str(table[2][i]).strip()
                unit = table[3][i].strip()

                outfile.write(time + ",0x" + raw_id + "," + message + "," + label + "," + value + "," + unit + "\n")
            current_message = parse_message_better(raw_id,raw_message,dbc,dbc_ids,unknown_ids)
            if current_message != "INVALID_ID":
                for i in current_message:
                    nextline[header_list.index(str(i))]=str(current_message[i])
            if time == last_time:
                continue
            elif flag_second_line==True:
                flag_second_line = False
                continue
            elif time != last_time:
                # write our line to file
                # clear it out and begin putting new values in it
                last_time = time
                nextline[header_list.index("Time")]=raw_time
                outfile2.write(",".join(nextline) + "\n")
                nextline = [""] * len(header_list)
    print("These IDs not found in DBC: " +str(unknown_ids))
    infile.close()
    outfile.close()
    outfile2.close()
    return

def parse_folder(input_path,dbc_file: cantools.db.Database):
    '''
    @brief: Locates Raw_Data directory or else throws errors. Created Parsed_Data directory if not created.
            Calls the parse_file() function on each raw CSV and alerts the user of parsing progress.
    @input: N/A
    @return: N/A
    '''
    newpath = input_path
    print("Selected path is: " + str(newpath))
    os.chdir(newpath)
    print("Current path is: " + os.getcwd())
    

    # Creates Parsed_Data folder if not there.
    if not os.path.exists("temp-parsed-data"):
        print("created 'temp-parsed-data' folder")
        os.makedirs("temp-parsed-data")
        # Creates Parsed_Data folder if not there.
    if not os.path.exists("parsed-data"):
        print("created 'parsed-data' folder")
        os.makedirs("parsed-data")
    # Generate the main DBC file object for parsing
    dbc_file=dbc_file
    # Loops through files and call parse_file on each raw CSV.
    for file in os.listdir(newpath):
        filename = os.fsdecode(file)
        if filename.endswith(".CSV") or filename.endswith(".csv"):
            parse_file(filename,dbc_file)
            print("\tSuccessfully parsed: " + filename)
        else:
            print("\t\tSkipped " + filename + " because it does not end in .csv")
            continue

    return 

########################################################################
########################################################################
# Parsed Data CSV to MAT struct Code Section
########################################################################
########################################################################

"""
@Author: Sophia Smith + Bo Han Zhu
@Date: 2/11/2022
@Description: Takes a Parse_Data folder of CSVs and outputs a .mat struct for plotting.

create_mat():
    read_files() --> create_dataframe(csv_files) --> get_time_elapsed(frames_list) --> create_struct(frames_list1) --> transpose_all(struct1)

"""

import os
import re
import pandas as pd
import scipy.io
import numpy as np
import dateutil.parser as dp
from os import listdir
from os.path import isfile, join
from datetime import datetime
from scipy.io import savemat


def read_files(folder):
    '''
    @brief: Reads parsed data files from Parsed_Data folder and returns a 
            list of file paths (as strings)
    @input: None
    @return: None
    '''
    try:
        path_name = folder

        file_path = []
        file_count = 0
        for root, dirs, files in os.walk(path_name, topdown=False):
            for name in files:
                if ".CSV" in name or ".csv" in name:
                    fp = os.path.join(root, name)
                    file_path.append(fp)
                    file_count += 1
    except:
        print('FATAL ERROR: Process failed at step 1.')
        input("press enter to exit")
        sys.exit(0)

    print('Step 1: found ' + str(file_count) + ' files in the ' + path_name + ' folder')
    return file_path

def create_dataframe(files = []):
    '''
    @brief: Reads parsed data file and creates a pandas dataframe.
            Each row is formatted to work with the Matlab parser. 
    @input: A list of files
    @return: A dataframe list
    '''
    try:
        df_list = []
        for f in files:
            df = pd.read_csv(f)
            df_list.append(df)
    except:
        print('FATAL ERROR: Process failed at step 2.')
        input("press enter to exit")
        sys.exit(0)

    print('Step 2: created dataframes')

    return df_list

def get_time_elapsed(frames = []):
    '''
    @brief: Calculated the elapsed time for each label based on a baseline
    @input: A dataframe list
    @ouput: An updated dataframe list with elapsed times
    '''
    skip = 0
    df_list = []
    start_time = 0
    set_start_time = True # boolean flag: we only want to set the start time once, during the first (i.e. earliest) CSV
    try:
        for df in frames:
            skip += 1
            timestamps = [dp.isoparse(x) for x in df['time']]
            if(len(timestamps) != 0):
                
                if set_start_time:
                    start_time = min(timestamps)
                    set_start_time = False # don't set start time again this run

                last_time = -1 # sometimes the Teensy has a slight ms miscue where it jumps back 1 sec on a second change, we must address it here
                time_delta = []
                for x in timestamps:
                    current_time = (x - start_time).total_seconds() * 1000
                    if current_time < last_time:
                        current_time += 1000 # add one second on a second switch miscue
                    time_delta.append(current_time)
                    last_time = current_time

                df['time_elapsed'] = pd.Series(time_delta)
                df_list.append(df)
            else:
                if DEBUG: print("Frame " + skip + "was skipped in elapsed time calculation.")
                continue
    except:
        print('FATAL ERROR: Process failed at step 3.')
        input("press enter to exit")
        sys.exit(0)

    print('Step 3: calculated elapsed time')
    return df_list

def create_struct(frames = []):
    '''
    @brief: Formats dataframe data to work with the Matlab parser. 
    @input: A dataframe of the original CSV with elapsed times
    @return: A dictionary of times and values for each label
    '''
    
    struct = {}
    all_labels = []

    # Need to average out all values under one timestamp
    last_time = {}
    same_time_sum = {}
    same_time_count = {}

    try:
        for df in frames:
            labels = df['label'].unique()
            df = df[pd.to_numeric(df['value'], errors='coerce').notnull()]

            for label in labels:
                df_label = df[df['label'] == label]
                df_new = df_label[['time_elapsed', 'value']].copy()
                rows = df_new.values.tolist()

                for i in range(len(rows)):
                    if label in all_labels:
                        # Do not add to struct if the time is the same, instead add to tracking dictionaries
                        if last_time[label] == float(rows[i][0]):
                            # Update tracking dictionaries
                            same_time_sum[label] = same_time_sum[label] + float(rows[i][1])
                            same_time_count[label] = same_time_count[label] + 1
                        else:
                            # Add tracking dictionaries' values to struct
                            struct[label][0].append(last_time[label])
                            struct[label][1].append(same_time_sum[label] / same_time_count[label])

                            # Reset all tracking dictionaries
                            last_time[label] = float(rows[i][0])
                            same_time_sum[label] = float(rows[i][1])
                            same_time_count[label] = 1
                    else:
                        struct[label] = [[float(rows[i][0])], [float(rows[i][1])]]
                        all_labels.append(label)
                        last_time[label] = float(rows[i][0])
                        same_time_sum[label] = float(rows[i][1])
                        same_time_count[label] = 1

    except:
        print('FATAL ERROR: Process failed at step 4.')
        input("press enter to exit")
        sys.exit(0)

    print('Step 4: created struct')
    return struct

def transpose_all(struct):
    '''
    @brief: Helper function to transfer 2xN array into Nx2 array for dataPlots
    @input: A dictionary of multiple 2xN arrays
    @return: A dictionary of those 2xN arrays transposed as Nx2 arrays
    '''
    for label in struct:
        struct[label] = np.array(struct[label]).T
    return struct

def create_mat():
    '''
    @brief: Entry point to the parser to create the .mat file
    @input: N/A
    @return: N/A
    '''
    print("Step 0: starting...")
    csv_files = read_files('temp-parsed-data')
    frames_list = create_dataframe(csv_files)
    frames_list1 = get_time_elapsed(frames_list)
    struct1 = create_struct(frames_list1)
    struct2 = transpose_all(struct1)

    try:
        savemat('parsed-data/output.mat', {'S': struct2}, long_field_names=True)
        print('Saved struct in output.mat file.')
    except:
        print('FATAL ERROR: Failed to create .mat file')


