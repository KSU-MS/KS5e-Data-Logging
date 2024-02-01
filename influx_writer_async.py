import asyncio
import cantools
import pandas as pd
import datetime
from folder_selection_utils import select_folder_and_get_path
from serial import Serial
# import serial_asyncio
import influxdb_client,os,time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS,ASYNCHRONOUS
from influxdb_client.client.write_api_async import WriteApiAsync
from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync
import can
import math
INFLUXDB_TOKEN="L09DVSnd8wsJaC54NP55aOiWcQNp7_U1vVPa1CO5htyTEBcVTH0zwHkQCITXDEBo2GexBfYY00y23h5vYGvMuA=="

# import matplotlib.pyplot as plt 
import time
class InfluxDBAsyncWriter:
    def __init__(self,write_api:WriteApiAsync,buffer_size=15000, write_interval=5,):
        self.buffer_size = buffer_size
        self.write_interval = write_interval
        self.buffer = []
        self.loop = asyncio.get_event_loop()
        self.flush_timer = None  # Store the timer object
        self.flush_fired = False
        # Initialize InfluxDB client
        self.token = INFLUXDB_TOKEN
        self.org = "ksu"
        self.url = "http://localhost:8086"
        self.bucket = "ksu"
        # self.client =  client
        self.writeapi = write_api
        
    async def write_data(self):
        while True:
            await asyncio.sleep(self.write_interval)
            await self._flush_buffer()
            self.reset_timer()

    async def _flush_buffer(self):
        if self.buffer:
            print(f'Flushing {len(self.buffer)} points to InfluxDB...')
            try:
                await self.writeapi.write(self.bucket,self.org,self.buffer,write_precision=WritePrecision.MS)
                print('Flush successful!')
                self.buffer = []
                self.flush_fired = True
                self.reset_timer()
            except Exception as e:
                self.buffer = []
                print(f'Error flushing data to InfluxDB: {e}')

    async def add_point_to_buffer(self, point: Point):
        self.buffer.append(point)

        if len(self.buffer) >= self.buffer_size:
            self.loop.create_task(self._flush_buffer())
            
    def reset_timer(self):
        # Cancel the existing timer if it exists
        if self.flush_timer and not self.flush_timer.done():
            self.flush_timer.cancel()

        # Create a new timer for the next interval
        self.flush_timer = self.loop.create_task(self._create_timer())

    async def _create_timer(self):
        try:
            await asyncio.sleep(self.write_interval)
            await self._flush_buffer()
            self.reset_timer()
        except asyncio.CancelledError:
            pass  # Timer was canceled, do nothing    
        
async def read_serial_port(serialport: Serial,db):
    while (serialport.in_waiting > 0):
        line1=serialport.read_until(b'\n')
        try:
            msg_list = []
            raw_id = (line1[0:4])
            raw_data = line1[4:-3]
            message_name = (db.get_message_by_frame_id(int.from_bytes(raw_id,'little'))).name
            parsed_message = db.decode_message(int.from_bytes(raw_id,'little'),raw_data,decode_choices=False)
            for i in parsed_message:
                new_msg = Point("ks6e_telem_test").tag("message",message_name).field(str(i),parsed_message[i])
                msg_list.append(new_msg)
            return msg_list
        except:
            pass
        
async def read_serial_data(writer,serial_port,db):
    while True:
        # Replace with your actual function to read data from the serial port
        new_point = await read_serial_port(serialport=serial_port,db=db)
        
        # Process the raw data (assuming the format "time,measurement,data")
        try:
            for point in new_point:
                writer.add_point_to_buffer(point)
        except ValueError:
            print(f"Invalid data format: {new_point}")
 

async def continuous_can_receiver(can_msg_decoder: cantools.db.Database,queue: asyncio.Queue):
    with can.interface.Bus(
        interface='pcan', channel='PCAN_USBBUS1', bitrate=500000
    ) as bus:
        reader = can.AsyncBufferedReader()
        listeners = [
            reader  # AsyncBufferedReader() listener
        ]
        loop = asyncio.get_running_loop()
        notifier = can.Notifier(bus, listeners, loop=loop)
        while True:
            msg = await reader.get_message()
            try:
                message_name = (can_msg_decoder.get_message_by_frame_id(msg.arbitration_id)).name
                decoded_msg = can_msg_decoder.decode_message(msg.arbitration_id, msg.data, decode_choices=False)
                timestamp = time.time_ns() // 1000000
                # print(timestamp)

                for i in decoded_msg:
                    new_msg = Point("ks6e_telem_test").tag("message",message_name).field(str(i),decoded_msg[i]).time(timestamp,write_precision=WritePrecision.MS)
                    await queue.put(new_msg)
            except KeyError as e:
                print(f'Error parsing incoming CAN frame: {e}')
def generate_sine_wave(amplitude, frequency, phase_shift, time_variable):
    return amplitude * math.sin(2 * math.pi * frequency * time_variable + phase_shift)

async def continuous_can_sender(can_msg_encoder: cantools.db.Database):
    with can.interface.Bus(
        'test', interface='virtual'
    ) as bus1:
        rpm = can_msg_encoder.get_message_by_name("M165_Motor_Position_Info")
        value=100
        # data = msg.encode({"D4_DC_Bus_Current": 100,"D1_Phase_A_Current":int(value),"D2_Phase_B_Current":int(value),"D3_Phase_C_Current":int(value)})
        
        # msg = can.Message(arbitration_id=msg.frame_id, is_extended_id=False, data=data)
        # print(msg)
        rpm_set = 100
        while(1):
            # rpm_set= rpm_set+1
            # bus1.send(msg)
            rpm_set = generate_sine_wave(3000,1,90,time.time()) + 3000
            rpm_data = rpm.encode({'D4_Delta_Resolver_Filtered': int(1), 'D3_Electrical_Output_Frequency': int(1), 'D2_Motor_Speed': rpm_set, 'D1_Motor_Angle_Electrical': int(1)})
            rpm_msg = can.Message(arbitration_id=rpm.frame_id, is_extended_id=False, data=rpm_data)
            bus1.send(rpm_msg)
            await asyncio.sleep(.01)
            # print("Message sent on {}".format(bus1.channel_info))

async def influx_write(queue:asyncio.Queue):
    async with InfluxDBClientAsync(url="http://localhost:8086",token = INFLUXDB_TOKEN,org = "ksu") as client:
        write_api = client.write_api()
        while True:
            newpoint = await queue.get()
            await write_api.write(bucket = "ksu",org="ksu",record=newpoint,write_precision=WritePrecision.MS)
            
# async def buildup_list(inqueue:asyncio.Queue,outqueue:asyncio.Queue):
#     msg_list = []
#     while True:
#         newmsg = await inqueue.get()
#         msg_list.append(newmsg)
#         print(len(msg_list))
#         if len(msg_list) > 100:
#             print(f"sent {len(msg_list)} points to out queue")
#             await outqueue.put(msg_list)
#             msg_list=[]

async def buildup_list(inqueue: asyncio.Queue, outqueue: asyncio.Queue):
    msg_list = []
    timeout = 5  # Set the timeout to 5 seconds
    last_put_time = await asyncio.sleep(0)
    timeout_event = asyncio.Event()

    async def check_timeout():
        while True:
            print("Check_timeout")
            await asyncio.sleep(timeout)
            timeout_event.set()

    timer = asyncio.create_task(check_timeout())  # Start the timeout-checking task

    while True:
        newmsg = await inqueue.get()
        msg_list.append(newmsg)
        # print(len(msg_list))

        if len(msg_list) > 15000 or timeout_event.is_set():
            print(f"Sent {len(msg_list)} points to out queue")
            await outqueue.put(msg_list)
            msg_list = []
            timeout_event.clear() 
            timer.cancel()
            timer = asyncio.create_task(check_timeout())
            
                       
async def main():
    inqueue = asyncio.Queue()
    outqueue = asyncio.Queue()
    # async with InfluxDBClientAsync(url="http://localhost:8086",token = INFLUXDB_TOKEN,org = "ksu") as client:
    #     write_api = client.write_api()
        
    # writer = InfluxDBAsyncWriter(write_api)
    # comport = input("Type in com port as 'COM#'")
    # serialport = Serial(comport)
    # serialport.baudrate = 921600
    # serialport.timeout = None #specify timeout when using readline()
    
    mega_dbc=cantools.database.Database()

    with open ('./dbc-files/ksu-dbc.dbc', 'r') as newdbc:
        mega_dbc.add_dbc(newdbc)
    
    # Start the writer and reader tasks
    # writer_task = asyncio.create_task(writer.write_data())
    influx_writer_task = asyncio.create_task(influx_write(outqueue))
    list_builder_task = asyncio.create_task(buildup_list(inqueue=inqueue,outqueue=outqueue))
    # reader_task = asyncio.create_task(read_serial_data(writer,serialport,mega_dbc))
    can_reader_task = asyncio.create_task(continuous_can_receiver(mega_dbc,inqueue))
    can_sender_task = asyncio.create_task(continuous_can_sender(mega_dbc))
    # Run the main loop
    # await asyncio.gather(influx_writer_task,can_reader_task,can_sender_task,list_builder_task)
    await asyncio.gather(influx_writer_task,can_reader_task,list_builder_task)

if __name__ == "__main__":
    asyncio.run(main())
