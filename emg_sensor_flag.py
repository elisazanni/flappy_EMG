# Import necessary modules
import asyncio
import csv
from collections import defaultdict
import keyboard
import os
import time

from Python.AeroPy.TrignoBase import TrignoBase
from Python.AeroPy.DataManager import DataKernel
import matplotlib as mpl

def write_state_to_file(state):
    file_path = "emg_state.txt"
    try:
        with open(file_path, "w") as f:
            f.write(str(state))
    except IOError as e:
        print(f"Errore nella scrittura del file: {e}")

# -----------------------------------
# Main class for managing Trigno sensors
# -----------------------------------
class TrignoRecorder:
    def __init__(self, host, max_amp):
        self.HOST = host

        # Desired configuration for sensors
        self.desired_mode = 'EMG raw (2148 Hz), skin check (74 Hz), +/-11mv, 10-850Hz'

        self.base = None
        self.guids = defaultdict(list)
        self.queues = {dtype: asyncio.Queue() for dtype in ['EMG', 'IMP']}

        self.recorded_data_dicts = []
        self.sensor_info_dicts = []

        # --- Variabili nuove ---
        self.max_amp = max_amp      # valore massimo globale calcolato da script 2
        self.switch = False         # variabile di stato
        self.last_switch_time = 0   # timestamp ultimo switch
        self.switch_delay = 0.05    # 50 ms minimo tra switch

    # Set up Trigno base interface
    def setup_base(self):
        self.base = TrignoBase(None)
        self.base.collection_data_handler = DataKernel(self.base)

    # Discover sensors and apply configurations
    def configure_sensors(self):
        sensors = self.base.Scan_Callback()
        for i, sensor in enumerate(sensors):
            self.base.TrigBase.SetSampleMode(i, self.desired_mode)

        for sensor in sensors:
            for channel in sensor.TrignoChannels:
                ch_type = str(channel.Type)
                info_dict = {"Sensor": str(sensor.Id), "Channel": str(channel.Name), "GUID": str(channel.Id), "DataType": ch_type}
                self.sensor_info_dicts.append(info_dict)

                if ch_type in self.guids:
                    self.guids[ch_type].append(channel.Id)
                if ch_type in self.queues:
                    self.guids[ch_type].append(channel.Id)

        return sensors

    # Process a queue for a specific sensor type
    async def process_queue(self, dtype):
        queue = self.queues[dtype]
        self.switch = False
        self.last_switch_time = time.time()
        write_state_to_file(self.switch)

        while True:
            guid, data = await queue.get()
            current_time = time.time()
            soglia = 0.6 * self.max_amp

            for sample in data:
                record = {
                    "sensor_type": dtype,
                    "channel_guid": guid,
                    "time_stamp": sample.Item1,
                    "value": sample.Item2
                }
                if dtype == "EMG":
                    value = float(record["value"])
                    
                    # SWITCH ON
                    if value > soglia and not self.switch and (current_time - self.last_switch_time > self.switch_delay):
                        self.switch = True
                        self.last_switch_time = current_time
                        write_state_to_file(self.switch) # Aggiorna il file
                        #print(f"[SWITCH ON] EMG {guid} ha superato soglia {soglia:.4f}")

                    # SWITCH OFF
                    elif value <= soglia and self.switch and (current_time - self.last_switch_time > self.switch_delay):
                        self.switch = False
                        self.last_switch_time = current_time
                        write_state_to_file(self.switch) # Aggiorna il file
                        #print(f"[SWITCH OFF]")


    # Start recording sensor data
    async def record(self):
        self.base.TrigBase.Start(ytdata=True)
        print("Recording started. Press 'q' to stop.")

        while True:
            if await asyncio.to_thread(keyboard.is_pressed, 'q'):
                print("Stopping recording.")
                break

            if self.base.TrigBase.CheckYTDataQueue():
                yt_data = self.base.TrigBase.PollYTData()
                for guid, data in yt_data.items():
                    for dtype, guids in self.guids.items():
                        if guid in guids:
                            await self.queues[dtype].put((guid, data))

            await asyncio.sleep(0.001)

        self.base.TrigBase.Stop()
        self.base.TrigBase.ResetPipeline()
        print("Recording complete.")

    # Full process: setup → wait → record
    async def run(self):
        self.setup_base()
        self.base.Connect_Callback()
        self.configure_sensors()
        self.base.TrigBase.Configure(start_trigger=False, stop_trigger=False)

        print("Press 's' to start recording...")
        await asyncio.to_thread(keyboard.wait, 's')

        # Start background tasks
        workers = [asyncio.create_task(self.process_queue(dtype)) for dtype in self.queues.keys()]
        await self.record()

        # Cancel workers after recording
        for w in workers:
            w.cancel()
            try:
                await w
            except asyncio.CancelledError:
                pass
        
    

# -----------------------------------
# Entry point
# -----------------------------------

if __name__ == "__main__":
    # Inserisci qui il max_amp calcolato dallo script 2
    max_amp_calcolato = 0.2

    asyncio.run(TrignoRecorder("192.168.0.156", max_amp_calcolato).run())

