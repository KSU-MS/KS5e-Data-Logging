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
from scipy.io import savemat
from os.path import isfile, join
from os import listdir
from collections import OrderedDict
import dateutil.parser as dp
import numpy as np
import scipy.io
import re
import os
import sys
from datetime import datetime
import cantools
from cantools.database import Message, Database
import pandas as pd
import csv
import json
import tempfile
import shutil
import time
import parser_utils.parser_logger as parser_logger
import parser_utils.checkdbcversion as checkdbcvers
import logging

DEBUG = False  # Set True for optional error print statements
PARSER_EXIT_TIMEOUT = 10


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
        logging.error('error: dbc scraping failed')
        logging.error('get_dbc_files('+str(path_name)+')')
        return None

    logging.info(f'Found {file_count} .dbc files in the dbc-files folder')
    mega_dbc = cantools.db.Database()
    for filename in file_path:
        with open(filename, 'r') as newdbc:
            try:
                mega_dbc.add_dbc(newdbc)
                logging.info(f"Added {filename} to dbc for parsing")
            except:
                logging.error(f"Error adding dbc file: {filename}")

    if (len(mega_dbc.messages) > 0):
        logging.info(
            f"dbc successfully created with {len(mega_dbc.messages)} messages")
        logging.info(f"DBC VERSION: {mega_dbc.version}")
        checkdbcvers.check_newer_commit(checkdbcvers.repo_owner+"/"+checkdbcvers.repo_name,(mega_dbc.version.strip()))
        return mega_dbc
    else:
        logging.warning(f"error: dbc was empty! it has no messages :(")
        return None


def parse_ids_in_database(db: Database):
    dbc_ids = []
    for message in db.messages:
        # print(str(vars(message)) + "\n")
        dbc_ids.append(message.frame_id)
        # print(str(message.name)+" ID: "+str(message.frame_id)+" Note: "+str(message.comment))
        # print("\tsignals: ")
        # for signal in message.signals:
        # print("\t\t"+ signal.name)
    return dbc_ids


def parse_message(id: int, data: bytearray, db: Database, decode_enums=False):
    labels = []
    values = []
    units = []
    actual_message = db.get_message_by_frame_id(id)
    signal_list = actual_message.signals
    try:
        parsed_message = db.decode_message(
            id, data, decode_choices=decode_enums)
        for i in parsed_message:
            message_label = str(i)
            labels.append(message_label)
            values.append(str(parsed_message[i]))
            for signal in signal_list:
                if message_label == signal.name:
                    units.append(str(signal.unit))
    except:
        return "INVALID_ID"
    message_name = actual_message.name
    return [message_name, labels, values, units]


def parse_table_from_message(id: int, parsed_message, message_definition: Message):
    labels = []
    values = []
    units = []
    signal_list = message_definition.signals
    try:
        parsed_message = parsed_message
        for i in parsed_message:
            message_label = str(i)
            labels.append(message_label)
            values.append(str(parsed_message[i]))
            for signal in signal_list:
                if message_label == signal.name:
                    units.append(str(signal.unit))
    except:
        return "INVALID_ID"
    message_name = message_definition.name
    return [message_name, labels, values, units]


def parse_message_to_cantools_msg(id: int, data: bytearray, db: Database, decode_enums=False):
    try:
        parsed_message = db.decode_message(
            id, data, decode_choices=decode_enums)
        return parsed_message
    except (cantools.db.DecodeError, KeyError) as e:
        logging.debug(f"{e}: Error decoding {id}")

    # except (cantools.db.DecodeError) as e:
    #     logging.error(f"{e}: Error decoding {id}")
    #     logging.warning(f"going to remove {id} from database")
    #     actual_message = db.get_message_by_frame_id(id)
    #     print(db.messages)
    #     index = (db.messages).index(actual_message)
    #     print(index)
    #     removed_message = db.messages.pop(index)
    #     logging.warning(f"removed message: {removed_message.frame_id} {removed_message.name}")
    return "INVALID_ID"


def parse_time(raw_time):
    '''
    @brief: Converts raw time into human-readable time.
    @input: The raw time given by the raw data CSV.
    @return: A string representing the human-readable time.
    '''
    ms = int(raw_time) % 1000
    raw_time = int(raw_time) / 1000
    time = str(datetime.utcfromtimestamp(
        raw_time).strftime('%Y-%m-%dT%H:%M:%S'))
    time = time + "." + str(ms).zfill(3) + "Z"
    return time

# Get signals that occur in log to populate header (column names)
# 1. Convert csv to df
# 2. Get unique IDs in "msg.id" column
# 3. For each:
#   a) try to get CAN frame from database with ID as key
#   b) add each signal in the message to the header list
#   c) if CAN ID not valid,
# 4. return header list


def parse_ids_used_in_log(filename, dbc_for_parsing: cantools.db.Database):
    header_list = ["Time"]
    unknown_list = []
    log_df = pd.read_csv(filename)
    log_ids = log_df["msg.id"].unique()
    for id in log_ids:
        id_as_int = int(id, 16)
        try:
            can_frame = dbc_for_parsing.get_message_by_frame_id(id_as_int)
            for can_signal in can_frame.signals:
                header_list.append(can_signal.name)
        except KeyError as e:
            unknown_list.append(id)

    unknown_list = list(OrderedDict.fromkeys(unknown_list))
    header_list = list(OrderedDict.fromkeys(header_list))

    return header_list, unknown_list


def delete_lines_containing_string(input_file, specified_string):
    # Create a temporary file to write the filtered content
    temp_file = tempfile.NamedTemporaryFile(
        mode='w', delete=False, newline='', encoding='utf-8')

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


def get_parsed_log_info(log_input_path):
    # TODO this function should verify that the file is a correctly formatted one (Time,signal1,signal2..)
    PARAMS = [
        "VCU_STATEMACHINE_STATE",
        "Pack_SOC",
        "D1_Commanded_Torque",
        "D2_Motor_Speed",
        "Pack_Current",
        "High_Temperature",
        "D1_DC_Bus_Voltage"
    ]
    log_stats_dict = {}
    try:
        df = pd.read_csv(log_input_path)
    except:
        logging.error(f"failed to load csv: {log_input_path}")
        return None
    
    log_time_start = df["Time"].min()
    log_time_end = df["Time"].max()
    log_time_duration = log_time_end-log_time_start
    log_time_duration_seconds = log_time_duration/1000
    log_minutes, log_seconds_remainder = divmod(log_time_duration_seconds, 60)
    log_time_elapsed = f"{int(log_minutes):03}:{log_seconds_remainder:06.3f}"
    log_stats_dict["duration"]=log_time_elapsed
    for field in PARAMS:
        try:
            log_stats_dict[field] = {
                'max': df[field].max(),
                'min': df[field].min(),
                'average': df[field].mean()
            }
        except KeyError as e:
            logging.error(f"{e} key {field} not found in {log_input_path}")
    return log_stats_dict

def parse_file(filename, dbc: Database, dbc_ids: list):
    '''
    @brief: Reads raw data file and creates parsed data CSV.
            Loops through lines to write to parsed datafile.
            Calls the parse_message and parse_time functions as helpers.
    @input: The filename of the raw and parsed CSV.
    @return: N/A
    '''
    logging.info("start parsing: "+filename)
    expected_columns = "time,msg.id,msg.len,data"
    infile = open(filename, "r")
    first_line = infile.readline().strip()    # Delete any lines that contain this blank glitchy CAN message of ID 0 and data 0
    logging.debug(f"first line of {filename} = {first_line}")
    if (first_line) != (expected_columns):
        raise ValueError("columns in the CSV file do not match the expected format.")
    # Replace with the specified string to be removed
    specified_string = ',0,8,0000000000000000'
    # delete_lines_containing_string(filename,specified_string)

    dbc_ids = dbc_ids
    
    ids_used_in_log = parse_ids_used_in_log(filename, dbc)
    header_list = ids_used_in_log[0]
    unknown_ids = ids_used_in_log[1]
    # Miscellaneous shit lol
    nextline = [""] * len(header_list)
    header_string = ",".join(header_list)
    try:
        outfile = open("temp-parsed-data/" + filename, "w")
    except PermissionError as e:
        logging.error(f"could not open {'temp-parsed-data/' + filename} to write, {e}")
        raise e
    try:  
        outfile2 = open("parsed-data/parsed" + filename, "w")
    except PermissionError as e:
        logging.error(f"could not open {'parsed-data/parsed' + filename} to write, {e}")
        raise e
        
    flag_second_line = True
    flag_first_line = True
    last_time = ''
    infile_readlines = infile.readlines()
    for line in infile_readlines:
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
            int_id = int(raw_id, 16)
            try:
                message_def = dbc.get_message_by_frame_id(int_id)
            except:
                continue
            # Do not parse if the length of the message is 0, otherwise bugs will occur later.
            if length == 0 or raw_message == "\n":
                continue

            # Call helper functions
            time = parse_time(raw_time)
            # Strip trailing end of line/file characters that may cause bad parsing
            raw_message = raw_message[:(int(length) * 2)]
            # Sometimes messages come truncated if 0s on the left. Append 0s so field-width is 16.
            raw_message = raw_message.zfill(16)
            # Get actual message, referencing our DBC file and ID lists
            message_bytearray = bytearray.fromhex(raw_message)
            parsed_message = parse_message_to_cantools_msg(
                int_id, message_bytearray, dbc)
            try:
                table = parse_table_from_message(
                    int_id, parsed_message, message_definition=message_def)
            except:
                table = "INVALID_ID"

            if table == "INVALID_ID" or table == "UNPARSEABLE":
                continue

            # Assertions that check for parser failure. Notifies user on where parser broke.
            assert len(table) == 4, "error: Parser expected 4 arguments from parse_message at ID: 0x" + \
                table[0] + ", got: " + str(len(table))
            assert len(table[1]) == len(table[2]) and len(table[1]) == len(
                table[3]), "error: Label, Data, or Unit numbers mismatch for ID: 0x" + raw_id

            # Harvest parsed datafields and write to outfile.
            message = table[0].strip()
            for i in range(len(table[1])):
                label = table[1][i].strip()
                value = str(table[2][i]).strip()
                unit = table[3][i].strip()

                outfile.write(time + ",0x" + raw_id + "," + message +
                              "," + label + "," + value + "," + unit + "\n")

            current_message = parsed_message
            if current_message != "INVALID_ID":
                for i in current_message:
                    nextline[header_list.index(str(i))] = str(
                        current_message[i])
            if time == last_time:
                continue
            elif flag_second_line == True:
                flag_second_line = False
                continue
            elif time != last_time:
                # write our line to file
                # clear it out and begin putting new values in it
                last_time = time
                nextline[header_list.index("Time")] = raw_time
                outfile2.write(",".join(nextline) + "\n")
                nextline = [""] * len(header_list)
    logging.warning("These IDs not found in DBC: " + str(unknown_ids))
    infile.close()
    outfile.close()
    outfile2.close()
    return {"length": len(infile_readlines), "unknown_ids": unknown_ids,"input_file":infile.name,"outfile":outfile.name,"outfile2":outfile2.name}


def parse_folder(input_path, dbc_file: cantools.db.Database):
    '''
    @brief: Locates Raw_Data directory or else throws errors. Created Parsed_Data directory if not created.
            Calls the parse_file() function on each raw CSV and alerts the user of parsing progress.
    @input: N/A
    @return: N/A
    '''
    newpath = input_path
    logging.debug("Selected path is: " + str(newpath))
    os.chdir(newpath)
    logging.debug("Current path is: " + os.getcwd())
    newpath = os.getcwd()
    # Creates Parsed_Data folder if not there.
    if not os.path.exists("temp-parsed-data"):
        logging.debug("created 'temp-parsed-data' folder")
        os.makedirs("temp-parsed-data")
        # Creates Parsed_Data folder if not there.
    if not os.path.exists("parsed-data"):
        logging.debug("created 'parsed-data' folder")
        os.makedirs("parsed-data")
    # Generate the main DBC file object for parsing
    dbc_file = dbc_file
    dbc_ids = parse_ids_in_database(dbc_file)
    num_of_csvs_in_folder = 0
    for file in os.listdir(newpath):
        filename = os.fsdecode(file)
        if filename.endswith(".CSV") or filename.endswith(".csv"):
            logging.debug(f"found csv: {filename}")
            num_of_csvs_in_folder+=1
            
    logging.info(f"found {num_of_csvs_in_folder} CSVs in {newpath}")
    
    if num_of_csvs_in_folder == 0:
        logging.warning("there are ZERO CSV files in this folder. did you select the right one?")
        
    parsed_folder_stats = {
        "dbc_version":dbc_file.version
    }
    # Loops through files and call parse_file on each raw CSV.
    for file in os.listdir(newpath):
        filename = os.fsdecode(file)
        if filename.endswith(".CSV") or filename.endswith(".csv"):
            start_time = time.time()
            
            try:
                parsed_file_stats = parse_file(filename, dbc_file, dbc_ids)
                length = parsed_file_stats["length"]
                end_time = time.time()
                logging.info(
                    f"Successfully parsed: {filename} with {length} lines in {end_time-start_time} seconds")
                
                parsed_log_info = get_parsed_log_info(parsed_file_stats["outfile2"])
                parsed_folder_stats[filename]={
                    "parsing time":end_time-start_time,
                    "summary":parsed_log_info,
                    "debug_info":parsed_file_stats
                }
                logging.debug(json.dumps(parsed_log_info,indent=1))
                
            except (ValueError,PermissionError) as e:
                logging.error(f"attempt to parse {filename} raised error {e}")
                
        else:
            logging.debug("Skipped " + filename +" because it does not end in .csv")
            continue

    return parsed_folder_stats

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
        logging.error('error: Process failed at step 1.')
        return None

    logging.info('Step 1: found ' + str(file_count) +
                 ' files in the ' + path_name + ' folder')
    return file_path


def create_dataframe(files=[]):
    '''
    @brief: Reads parsed data file and creates a pandas dataframe.
            Each row is formatted to work with the Matlab parser. 
    @input: A list of files
    @return: A dataframe list
    '''
    try:
        df_list = []
        for f in files:
            try:
                df = pd.read_csv(f)
            except pd.errors.EmptyDataError as e:
                logging.error(f"failed to read csv ({f}) into dataframe: {e}")
                continue
            df_list.append(df)
    except:
        logging.error('error: Process failed at step 2.')
        
    logging.info('Step 2: created dataframes')

    return df_list


def get_time_elapsed(frames=[]):
    '''
    @brief: Calculated the elapsed time for each label based on a baseline
    @input: A dataframe list
    @ouput: An updated dataframe list with elapsed times
    '''
    skip = 0
    df_list = []
    start_time = 0
    # boolean flag: we only want to set the start time once, during the first (i.e. earliest) CSV
    set_start_time = True
    try:
        for df in frames:
            skip += 1
            timestamps = [dp.isoparse(x) for x in df['time']]
            if (len(timestamps) != 0):

                if set_start_time:
                    start_time = min(timestamps)
                    set_start_time = False  # don't set start time again this run

                last_time = -1  # sometimes the Teensy has a slight ms miscue where it jumps back 1 sec on a second change, we must address it here
                time_delta = []
                for x in timestamps:
                    current_time = (x - start_time).total_seconds() * 1000
                    if current_time < last_time:
                        current_time += 1000  # add one second on a second switch miscue
                    time_delta.append(current_time)
                    last_time = current_time

                df['time_elapsed'] = pd.Series(time_delta)
                df_list.append(df)
            else:
                logging.debug("Frame " + skip +
                                    "was skipped in elapsed time calculation.")
                continue
    except:
        logging.error('error: Process failed at step 3.')
        return None

    logging.info('Step 3: calculated elapsed time')
    return df_list


def create_struct(frames=[]):
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
                            same_time_sum[label] = same_time_sum[label] + \
                                float(rows[i][1])
                            same_time_count[label] = same_time_count[label] + 1
                        else:
                            # Add tracking dictionaries' values to struct
                            struct[label][0].append(last_time[label])
                            struct[label][1].append(
                                same_time_sum[label] / same_time_count[label])

                            # Reset all tracking dictionaries
                            last_time[label] = float(rows[i][0])
                            same_time_sum[label] = float(rows[i][1])
                            same_time_count[label] = 1
                    else:
                        struct[label] = [[float(rows[i][0])], [
                            float(rows[i][1])]]
                        all_labels.append(label)
                        last_time[label] = float(rows[i][0])
                        same_time_sum[label] = float(rows[i][1])
                        same_time_count[label] = 1

    except:
        logging.error('error: Process failed at step 4.')
        return None

    logging.info('Step 4: created struct')
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


def create_mat(path):
    '''
    @brief: Entry point to the parser to create the .mat file
    @input: N/A
    @return: N/A
    '''
    logging.info("Step 0: starting...")
    read_file_path = path
    csv_files = read_files(read_file_path)
    frames_list = create_dataframe(csv_files)
    frames_list1 = get_time_elapsed(frames_list)
    struct1 = create_struct(frames_list1)
    struct2 = transpose_all(struct1)

    try:
        savemat('parsed-data/output.mat',
                {'S': struct2}, long_field_names=True)
        logging.info('Saved struct in output.mat file.')
        return True
    except:
        logging.error('error: Failed to create .mat file')
        return False
