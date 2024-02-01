# This script
# INFLUXDB_TOKEN="sQDuwGgAlynPWjjcYXsTWl02hu7Z2Ji7o7rhn9LMCyZy7oA7IecTbpO8BTp_Tk3D-sX9HyZBUXu4j7jTekwbEA=="
import influxdb_client,os,time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS,ASYNCHRONOUS
INFLUXDB_TOKEN="L09DVSnd8wsJaC54NP55aOiWcQNp7_U1vVPa1CO5htyTEBcVTH0zwHkQCITXDEBo2GexBfYY00y23h5vYGvMuA=="

# import cantools
# token = os.environ.get("INFLUXDB_TOKEN")
# token = INFLUXDB_TOKEN
token = INFLUXDB_TOKEN
org = "ksu"
url = "http://localhost:8086"
bucket="ksu"
client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
print(client)
write_api = client.write_api(write_options=SYNCHRONOUS)
timestampstr = '2024-01-31T01:05:00.051Z'
timestampstr2 = '2024-01-31T01:06:00.031Z'
timestamp = 1706680456069
timestamp2 = 1706680455069
msgdict={
    "car":"car_test",
    # "timestamp":1706680456069,
    "timestamp":timestampstr2,
    "bus":"buss1",
    "message":"msg2",
    "signal2":13
}
msgdict2={
    "car":"car_test",
    # "timestamp":1706680455069,
    "timestamp":timestampstr,
    "bus":"buss1",
    "message":"msg2",
    "signal2":11
}
# point = Point.from_dict(msgdict, write_precision=WritePrecision.MS,
#                         record_measurement_key="car",
#                         record_time_key="timestamp",
#                          record_tag_keys=["bus","message"],
#                          record_field_keys=["signal2"])
# point2 = Point.from_dict(msgdict2, write_precision=WritePrecision.MS,
#                         record_measurement_key="car",
#                         record_time_key="timestamp",
#                          record_tag_keys=["bus","message"],
#                          record_field_keys=["signal2"])
point = Point("test_measurement")
point.field("balls",76)
# point.time(time=1706683590169000000)
# point2 = Point("test_measurement")
# point.time(time=timestampstr2,write_precision=WritePrecision.MS)
point.field("ballz",76)

print(point)
# print(point2)
# point_list = [point,point2]
write_api.write(bucket=bucket,org=org, record=point)
time.sleep(1) # separate points by 1 second

# query = """SELECT * FROM 'car_test'"""

# # Execute the query
# table = client.query(query=query, database="kennesaw_test", language='sql')
# print(table)
# # Convert to dataframe
# df = table.to_pandas().sort_values(by="time")
# print(df)