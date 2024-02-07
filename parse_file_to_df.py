import cantools
import pandas as pd
import datetime
from folder_selection_utils import select_folder_and_get_path
# import matplotlib.pyplot as plt 
import time
failed_id_list=[]

def df_row_to_msg(id,data,dbc):
    try:
        id_int = int(id,16)
    except:
        pass
        # print(f"ID Parsing failed. {id_int}")
    try:
        data = bytearray.fromhex(str(data))
    except:
        pass
        # print(f"Data parsing failed. {data}")
    try:
        name = (dbc.get_message_by_frame_id(id_int)).name
        msg = dbc.decode_message(id_int,data,decode_choices=False)
        return name,msg 
    except:
        pass
        # print(f"message decode failed. id: {id_int} data: {data}")
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

def msg_list_to_point_list(msg_list):
    point_list=[]
    for item in msg_list:
        msgdict={
            "car":"ks6e",
            "timestamp":item[0],
            "bus":item[1],
            "message":item[2],
            item[3]:item[4]
        }
        point = Point.from_dict(msgdict, write_precision=WritePrecision.MS,
                            record_measurement_key="car",
                            record_time_key="timestamp",
                            record_tag_keys=["bus","message"],
                            record_field_keys=[item[3]])
        point_list.append(point)
    return point_list

mega_dbc=cantools.database.Database()

with open ('./dbc-files/ksu-dbc.dbc', 'r') as newdbc:
    mega_dbc.add_dbc(newdbc)


OTHER_TOKEN="g3nQ5gZ_QeR3o3D07WxlO-bWbAkvliSnguvmgegPJTx3dbNsq-37h4KOJCnnhx2CUW8oUGb4-qsRY4W7U2dbhw=="
INFLUXDB_TOKEN="sQDuwGgAlynPWjjcYXsTWl02hu7Z2Ji7o7rhn9LMCyZy7oA7IecTbpO8BTp_Tk3D-sX9HyZBUXu4j7jTekwbEA=="
import os,time
from influxdb_client_3 import InfluxDBClient3, Point
from influxdb_client_3.write_client.domain.write_precision import WritePrecision
# import cantools
# token = os.environ.get("INFLUXDB_TOKEN")
token = OTHER_TOKEN
org = "mathos.brook@gmail.com"
host = "https://us-east-1-1.aws.cloud2.influxdata.com"

client = InfluxDBClient3(host=host, token=token,database="kennesaw_test" ,org=org)
print(client)


MAX_SEND_LENGTH = 15000
    

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
        print(newlist)
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
                    client.write(record=chunk,write_precision=WritePrecision.MS)
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