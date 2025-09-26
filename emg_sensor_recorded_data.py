# Import necessary modules
import asyncio  # For asynchronous operations
import csv      # For writing data to CSV
from collections import defaultdict  # For dictionary with default list
import keyboard  # For keyboard input detection
import os
import json
import time 

# Import Trigno-related interfaces from AeroPy library
from Python.AeroPy.TrignoBase import TrignoBase
from Python.AeroPy.DataManager import DataKernel

durata = 10

# -----------------------------------
# Main class for managing Trigno sensors
# -----------------------------------
class TrignoRecorder:
    def __init__(self, host):
        self.HOST = host

        # Desired configuration for sensors
        # configuration could be change according to new mode selected from csv filtered file
        self.desired_mode = 'EMG raw (2148 Hz), skin check (74 Hz), +/-11mv, 10-850Hz'

        self.base = None # TrignoBase instance (will be initialized)
        self.guids = defaultdict(list) # Store GUIDs for each sensor type
        self.queues = {dtype: asyncio.Queue() for dtype in ['EMG', 'IMP']} # Queues for async processing

        # Store data to write to csv
        self.recorded_data_dicts = [] 
        self.sensor_info_dicts = []  

    # Set up Trigno base interface
    def setup_base(self):
        self.base = TrignoBase(None)
        self.base.collection_data_handler = DataKernel(self.base)

    # Discover sensors and apply configurations
    def configure_sensors(self):
        sensors = self.base.Scan_Callback() # Detect connected sensors
        for i, sensor in enumerate(sensors):
            self.base.TrigBase.SetSampleMode(i, self.desired_mode) # Apply configuration

        for sensor in sensors:
            for channel in sensor.TrignoChannels:
                ch_type = str(channel.Type)
                info_dict = {"Sensor": str(sensor.Id), "Channel": str(channel.Name), "GUID": str(channel.Id), "DataType": ch_type}
                self.sensor_info_dicts.append(info_dict) # Store sensor metadata

                # Store channel GUIDs for each data type
                if ch_type in self.guids:
                    self.guids[ch_type].append(channel.Id)
                if ch_type in self.queues:
                    self.guids[ch_type].append(channel.Id)

        return sensors

    # Process a queue for a specific sensor type (EMG, ACC, GYRO)
    async def process_queue(self, dtype):
        queue = self.queues[dtype]
        while True:
            guid, data = await queue.get() # Get next data item from queue --> .get() method flushes the elements present in the asyncio.Queue() object from the left most and empty the queue
                                            # --> if the Queue() object is empty, it waits until new data is queued
            for sample in data:
                record = {
                        "sensor_type": dtype,
                        "channel_guid": guid,
                        "time_stamp": sample.Item1,
                        "value": sample.Item2
                    }
            self.recorded_data_dicts.append(record)

            # if dtype == "EMG":
            #     print(f"[{record['time_stamp']}] EMG {record['channel_guid']}: {record['value']}")

    # Start recording sensor data for a given duration 
    async def record(self, duration=durata):
        self.base.TrigBase.Start(ytdata=True)
        print(f"Recording started. Press 'q' to stop or wait {duration} seconds.")

        start_time = time.time()

        while True:
            elapsed = time.time() - start_time

            # Stop if time is up or user presses 'q'
            if elapsed >= duration or await asyncio.to_thread(keyboard.is_pressed, 'q'):
                print("Stopping recording.")
                break

            # If new data is available
            if self.base.TrigBase.CheckYTDataQueue():
                yt_data = self.base.TrigBase.PollYTData()
                for guid, data in yt_data.items():
                    # Route data to appropriate queue
                    for dtype, guids in self.guids.items():
                        if guid in guids:
                            await self.queues[dtype].put((guid, data))  # .put() method append to the right end of the queue - i.e. asyncio.Queue() object

            await asyncio.sleep(0.001) # Prevent busy-waiting

        # Stop data collection and reset system
        self.base.TrigBase.Stop()
        self.base.TrigBase.ResetPipeline()
        print("Recording complete.")

    # Write recorded data and sensor info to CSV
    def save_to_csv(self, file_path, data_dicts_list):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", newline="") as f:
            # Write block
            writer = csv.DictWriter(f, fieldnames=[key for key in data_dicts_list[0].keys()])
            if not data_dicts_list:
                print(f"[WARNING] No data to save to {file_path}")
            writer.writeheader()
            writer.writerows(data_dicts_list)            

    # Full process: setup → wait → record → save
    async def run(self):
        self.setup_base() # Initialize base connection
        self.base.Connect_Callback() # Connect to sensors
        self.configure_sensors() # Configure sensors
        self.base.TrigBase.Configure(start_trigger=False, stop_trigger=False) # Configure base

        print("Press 's' to start recording...")
        await asyncio.to_thread(keyboard.wait, 's') # Wait for user to press 's'

        # Start background tasks for processing each sensor data type
        workers = [asyncio.create_task(self.process_queue(dtype)) for dtype in self.queues.keys()]
        await self.record()  # Run main recording loop
        
        # Cancel background tasks after recording ends
        for w in workers:
            w.cancel()
            try:
                await w
            except asyncio.CancelledError:
                pass

        info_file = "info_data_emg.csv"
        data_file = "recorded_data_emg.csv"
        base_path = os.getcwd()
        data_folder = "csv"
        self.save_to_csv(os.path.join(base_path, data_folder, info_file), self.sensor_info_dicts) # Save info data
        print(f"Successfully saved info data to {os.path.join(base_path, data_folder, info_file)}")
        self.save_to_csv(os.path.join(base_path, data_folder, data_file), self.recorded_data_dicts) # Save recorded data
        print(f"Successfully saved stream data to {os.path.join(base_path, data_folder, data_file)}")

# -----------------------------------
# Entry point for running the script
# -----------------------------------
if __name__ == "__main__":
    # Create a TrignoRecorder instance and run its async pipeline
    # IP change according to IP remote host
    asyncio.run(TrignoRecorder("192.168.0.156").run())