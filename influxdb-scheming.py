# This script
# INFLUXDB_TOKEN="sQDuwGgAlynPWjjcYXsTWl02hu7Z2Ji7o7rhn9LMCyZy7oA7IecTbpO8BTp_Tk3D-sX9HyZBUXu4j7jTekwbEA=="
import os,time
from influxdb_client_3 import InfluxDBClient3, Point
from influxdb_client_3.write_client.domain.write_precision import WritePrecision

# import cantools
# token = os.environ.get("INFLUXDB_TOKEN")
# token = INFLUXDB_TOKEN
org = "mathos.brook@gmail.com"
host = "https://us-east-1-1.aws.cloud2.influxdata.com"
tokenfile = open('influxdb_token.txt', 'r')
influxdb_token = tokenfile.readline()
client = InfluxDBClient3(host=host, token=influxdb_token, org=org)
print(client)

database="kennesaw_test"

msgdict={
    "car":"car_test",
    "timestamp":1706143457068,
    "bus":"buss1",
    "message":"msg2",
    "signal2":10
}
msgdict2={
    "car":"car_test",
    "timestamp":1706143458067,
    "bus":"buss1",
    "message":"msg2",
    "signal2":10
}
point = Point.from_dict(msgdict, write_precision=WritePrecision.MS,
                        record_measurement_key="car",
                        record_time_key="timestamp",
                         record_tag_keys=["bus","message"],
                         record_field_keys=["signal2"])
point2 = Point.from_dict(msgdict2, write_precision=WritePrecision.MS,
                        record_measurement_key="car",
                        record_time_key="timestamp",
                         record_tag_keys=["bus","message"],
                         record_field_keys=["signal2"])
point_list = [point,point2]
client.write(database=database, record=point_list,write_precision=WritePrecision.MS)
time.sleep(1) # separate points by 1 second

query = """SELECT * FROM 'ks7e'"""

# Execute the query
table = client.query(query=query, database="kennesaw_test", language='sql')
print(table)
# Convert to dataframe
df = table.to_pandas().sort_values(by="time")
print(df)