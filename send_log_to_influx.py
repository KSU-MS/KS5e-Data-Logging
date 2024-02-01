INFLUXDB_TOKEN="sQDuwGgAlynPWjjcYXsTWl02hu7Z2Ji7o7rhn9LMCyZy7oA7IecTbpO8BTp_Tk3D-sX9HyZBUXu4j7jTekwbEA=="
import os,time
from influxdb_client_3 import InfluxDBClient3, Point
from influxdb_client_3.write_client.domain.write_precision import WritePrecision
# import cantools
# token = os.environ.get("INFLUXDB_TOKEN")
token = INFLUXDB_TOKEN
org = "mathos.brook@gmail.com"
host = "https://us-east-1-1.aws.cloud2.influxdata.com"

client = InfluxDBClient3(host=host, token=token, org=org)

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