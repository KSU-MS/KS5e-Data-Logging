import time
import asyncio
import cantools
from cantools.database.utils import DecodeError
import pandas as pd
import datetime
from folder_selection_utils import select_folder_and_get_path
# from serial import Serial
import serial_asyncio
import influxdb_client
import os
import time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS, ASYNCHRONOUS
from influxdb_client.client.write_api_async import WriteApiAsync
from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync
import can
import math
INFLUXDB_TOKEN = "L09DVSnd8wsJaC54NP55aOiWcQNp7_U1vVPa1CO5htyTEBcVTH0zwHkQCITXDEBo2GexBfYY00y23h5vYGvMuA=="

# import matplotlib.pyplot as plt


async def read_serial_port(serialport, db, queue: asyncio.Queue):
    """async task to read from a specified serial port, decode the message into CAN frames, and then put them into the queue

    Args:
        serialport (StreamReader): this is returned by serial_asyncio.open_serial_connection
        db (cantool databse): cantools database to decode with
        queue (asyncio.Queue): the queue of CAN frames
    """
    while True:

        line1 = await serialport.readline()
        try:
            # TODO
            raw_id = (line1[0:4])
            raw_data = line1[4:-3]
            message_name = (db.get_message_by_frame_id(
                int.from_bytes(raw_id, 'little'))).name
            parsed_message = db.decode_message(int.from_bytes(
                raw_id, 'little'), raw_data, decode_choices=False)
            timestamp = time.time_ns() // 1000000
            for i in parsed_message:
                new_msg = Point("ks6e_telem_test").tag("message", message_name).field(
                    str(i), parsed_message[i]).time(timestamp, write_precision=WritePrecision.MS)
                await queue.put(new_msg)

        except (KeyError, DecodeError) as e:
            print(f'Error parsing incoming CAN frame: {e}')
            print(line1)
            pass


async def continuous_can_receiver(can_msg_decoder: cantools.db.Database, queue: asyncio.Queue):
    with can.interface.Bus(
        'test', interface='virtual'
        # interface='pcan', channel='PCAN_USBBUS1', bitrate=500000
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
                message_name = (can_msg_decoder.get_message_by_frame_id(
                    msg.arbitration_id)).name
                decoded_msg = can_msg_decoder.decode_message(
                    msg.arbitration_id, msg.data, decode_choices=False)
                timestamp = time.time_ns() // 1000000
                # print(timestamp)

                for i in decoded_msg:
                    new_msg = Point("ks6e_telem_test").tag("message", message_name).field(
                        str(i), decoded_msg[i]).time(timestamp, write_precision=WritePrecision.MS)
                    await queue.put(new_msg)
            except KeyError as e:
                print(f'Error parsing incoming CAN frame: {e}')


async def continuous_can_sender(can_msg_encoder: cantools.db.Database):
    """send CAN messages continuously to simulate data input (UNUSED)

    Args:
        can_msg_encoder (cantools.db.Database): _description_
    """
    def generate_sine_wave(amplitude, frequency, phase_shift, time_variable):
        """generate a value which follows a sine wave function

        Args:
            amplitude (int): sine wave amplitude
            frequency (int): frequency in hertz
            phase_shift (int): phase shift in degrees
            time_variable (time): time.time()

        Returns:
            _type_: _description_
        """
        return amplitude * math.sin(2 * math.pi * frequency * time_variable + phase_shift)

    with can.interface.Bus(
        'test', interface='virtual'
    ) as bus1:
        rpm = can_msg_encoder.get_message_by_name("M165_Motor_Position_Info")
        value = 100
        # data = msg.encode({"D4_DC_Bus_Current": 100,"D1_Phase_A_Current":int(value),"D2_Phase_B_Current":int(value),"D3_Phase_C_Current":int(value)})

        # msg = can.Message(arbitration_id=msg.frame_id, is_extended_id=False, data=data)
        # print(msg)
        rpm_set = 100
        while (1):
            # rpm_set= rpm_set+1
            # bus1.send(msg)
            rpm_set = generate_sine_wave(3000, 1, 90, time.time()) + 3000
            rpm_data = rpm.encode({'D4_Delta_Resolver_Filtered': int(1), 'D3_Electrical_Output_Frequency': int(
                1), 'D2_Motor_Speed': rpm_set, 'D1_Motor_Angle_Electrical': int(1)})
            rpm_msg = can.Message(
                arbitration_id=rpm.frame_id, is_extended_id=False, data=rpm_data)
            bus1.send(rpm_msg)
            await asyncio.sleep(.01)
            # print("Message sent on {}".format(bus1.channel_info))


async def influx_write(queue: asyncio.Queue):
    """write from queue into influx

    Args:
        queue (asyncio.Queue): queue which contains LISTS of POINTS, not single points
    """
    # TODO make the url and stuff not hard-coded (load from json)
    async with InfluxDBClientAsync(url="http://localhost:8086", token=INFLUXDB_TOKEN, org="ksu") as client:
        write_api = client.write_api()
        while True:
            newpoint = await queue.get()
            await write_api.write(bucket="ksu", org="ksu", record=newpoint, write_precision=WritePrecision.MS)


async def buildup_list(inqueue: asyncio.Queue, outqueue: asyncio.Queue):
    """buffer points to be batch sent to influxdb

    Args:
        inqueue (asyncio.Queue): the queue to get individual points from
        outqueue (asyncio.Queue): the queue to put LISTS of points into
    """
    msg_list = []
    timeout = 5  # Set the timeout to 5 seconds
    timeout_event = asyncio.Event()

    async def check_timeout():
        while True:
            await asyncio.sleep(timeout)
            timeout_event.set()

    # Start the timeout-checking task
    timer = asyncio.create_task(check_timeout())

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

    # comport = input("Type in com port as 'COM#'")
    # serialport = Serial(comport)
    # serialport, _ = await serial_asyncio.open_serial_connection(url=comport, baudrate=921600)

    mega_dbc = cantools.database.Database()

    with open ('./dbc-files/ksu-dbc.dbc', 'r') as newdbc:
        mega_dbc.add_dbc(newdbc)

    # Start the writer and reader tasks
    influx_writer_task = asyncio.create_task(influx_write(outqueue))
    list_builder_task = asyncio.create_task(
        buildup_list(inqueue=inqueue, outqueue=outqueue))
    can_reader_task = asyncio.create_task(
        continuous_can_receiver(mega_dbc, inqueue))
    can_sender_task = asyncio.create_task(continuous_can_sender(mega_dbc))
    # serial_port_read_task = asyncio.create_task(read_serial_port(
    #     serialport=serialport, db=mega_dbc, queue=inqueue))
    # Run the main loop
    await asyncio.gather(influx_writer_task, can_reader_task, can_sender_task, list_builder_task)
    # await asyncio.gather(influx_writer_task,serial_port_read_task,list_builder_task)

if __name__ == "__main__":
    asyncio.run(main())
