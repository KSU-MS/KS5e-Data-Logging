import cantools
import pandas as pd
import datetime
from folder_selection_utils import select_folder_and_get_path
# import matplotlib.pyplot as plt 
import time
failed_id_list=[]

import influxdb_client,os,time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
INFLUXDB_TOKEN="sTRcOn3LruRWypvny2JfqKNvZZzlkbb7D8rN0fCNpE2W7hE0TKTZiABof2pqy7ubLFoGJyUQEDvWPncn1DIetQ=="

# import cantools
# token = os.environ.get("INFLUXDB_TOKEN")
token = INFLUXDB_TOKEN
org = "ksu"
url = "http://localhost:8086"
bucket="ksu_test"
def df_row_to_msg(id,data,dbc):
    try:
        id_int = int(id,16)
    except:
        pass
        print(f"ID Parsing failed. {id_int}")
    try:
        strdata = str(data).zfill(16)
        bytedata = bytearray.fromhex(strdata)
    except:
        pass
        print(f"Data parsing failed.{id_int} {data}")
    try:
        name = (dbc.get_message_by_frame_id(id_int)).name
        msg = dbc.decode_message(id_int,bytedata,decode_choices=False)
        return name,msg 
    except:
        pass
        if (id_int==195):
            print(f"message decode failed. id: {id_int} data: {data}")
        failed_id_list.append(id)
        return None

def get_msg_from_df(df,dbc):
    msg_list = []

    for index, row in input_df.iterrows():

        msg_id = input_df.at[index,'msg.id']
        msg_data = input_df.at[index,'data']
        msg = (df_row_to_msg(id=msg_id,data=msg_data,dbc=mega_dbc))
        # print(f"Line #{index}\t",end="")
        if msg is not None:
            msgname = msg[0]
            msgdata=msg[1]
            for i in msg[1]:
                raw_time=((input_df.at[index,'time']))
                msg_parsed = [raw_time,"bus1",msgname,str(i),msgdata[i]]
                msg_list.append(msg_parsed)
                
    return msg_list

def msg_list_to_point_list(measurement="ks6e_debug",msg_list=None):
    point_list=[]
    msg_list=msg_list
    measurement=measurement
    for item in msg_list:
        # msgdict={
        #     "car":"ks6e",
        #     "timestamp":item[0],
        #     "bus":item[1],
        #     "message":item[2],
        #     item[3]:item[4]
        # }
        timestamp = item[0]
        bus = item[1]
        message = item[2]
        signal = item[3]
        value = item[4]
        point = Point(measurement_name=measurement).time(timestamp,write_precision=WritePrecision.MS).tag("message",message).tag("bus",bus).field(signal,value)
        # print(point)
        # point = Point.from_dict(msgdict, write_precision=WritePrecision.MS,
        #                     record_measurement_key="car",
        #                     record_time_key="timestamp",
        #                     record_tag_keys=["bus","message"],
        #                     record_field_keys=[item[3]])
        point_list.append(point)
    return point_list

mega_dbc=cantools.database.Database()

with open ('./dbc-files/ksu-dbc.dbc', 'r') as newdbc:
    mega_dbc.add_dbc(newdbc)



client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
print(client)
write_api = client.write_api(write_options=SYNCHRONOUS)


MAX_SEND_LENGTH = 20000
    

path=select_folder_and_get_path()
msg_list = []
for file in os.listdir(path):
    print(file)
    filename = os.fsdecode(file)
    if filename.endswith(".CSV") or filename.endswith(".csv"):
        start_time = time.time()
        
        print("start time loaded csv at : "+str(start_time))

        input_df = pd.read_csv(os.path.join(path,filename))
        end_time = time.time()-start_time
        start_time2 = time.time() 
               
        print("end time loaded csv at : "+str(end_time))

        newlist = get_msg_from_df(input_df,mega_dbc)
        # print(newlist)
        point_list = msg_list_to_point_list(msg_list=newlist)
        print(len(point_list))
        start_time = time.time()
        print("Starting upload at "+str(start_time))
        
        for i in range(0,len(point_list),MAX_SEND_LENGTH):
            chunk = point_list[i:i + MAX_SEND_LENGTH]
            print("Sending chunk: ")
            print(len(chunk))
            for i in range(10):
                try:
                    write_api.write(bucket=bucket,org=org,record=chunk,write_precision=WritePrecision.MS)
                    break
                except:
                    print("write failed with exception, trying again")
                    print("count: "+str(i))
                    
        end_time = time.time()-start_time
        print("Ending upload at "+str(end_time))
        end_time2 = time.time()-start_time2

        print("ended list gen at : "+str(end_time2))

        print("\tSuccessfully parsed: " + filename)
    else:
        print("\t\tSkipped " + filename + " because it does not end in .csv")
        continue
with open(os.path.join(path,"uploaded.txt"),'w') as f:
    f.write("parsed this folder!\none day this will be a real log")
exit()
failed_id_list=list(set(failed_id_list))
# print("FAILED TO PARSE: \n ======================")
# print(failed_id_list)
# print("==========================")
new_df = pd.DataFrame(columns=['timestamp'])
for entry in msg_list:
    timestamp, label, value = entry
    if label not in new_df.columns:
        new_df[label]=pd.Series(index=new_df.index)
        # print(len(list(new_df)))
    new_df.loc[timestamp, label]=value
end_time = time.time()
end_time = (end_time-start_time)
print("end time: ",str(end_time))
# print(new_df)
newfile = 'new_parse_method_test.csv'
with open(newfile,"w") as f:
    new_df.to_csv(newfile)
print("end time after csv export: ",str(time.time()-start_time()))

# fig = plt.figure()
# def plot_vs_time(plot,thing,ls='-'):
#     try:
#         plot.plot(new_df['Time'],thing.interpolate(),ls,label=thing.name)
#     except: 
#         plot.plot(new_df['Time'],thing,ls)
        
# plot_vs_time(plt,new_df['D3_VAB_Vd_Voltage'])
# plot_vs_time(plt,new_df["D4_VBC_Vq_Voltage"])
# plt.show()