import cantools
import pandas as pd
import datetime
from folder_selection_utils import select_folder_and_get_path
# import matplotlib.pyplot as plt 
import time
failed_id_list=[]

INFLUXDB_TOKEN="L09DVSnd8wsJaC54NP55aOiWcQNp7_U1vVPa1CO5htyTEBcVTH0zwHkQCITXDEBo2GexBfYY00y23h5vYGvMuA=="
import influxdb_client,os,time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
# import cantools
# token = os.environ.get("INFLUXDB_TOKEN")
token = INFLUXDB_TOKEN
org = "ksu"
url = "http://localhost:8086"
bucket="ksu"

client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
print(client)
write_api = client.write_api(write_options=SYNCHRONOUS)
query_api = client.query_api()

query = """from(bucket: "ksu")
 |> range(start: -30d)"""
tables = query_api.query(query, org="ksu")

for table in tables:
  for record in table.records:
    print(record)
   
exit()
