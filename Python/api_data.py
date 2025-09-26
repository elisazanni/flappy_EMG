import AeroPy 
import time
import keyboard

from AeroPy.TrignoBase import TrignoBase
from AeroPy.DataManager import DataKernel
from Export import CsvWriter

import threading
import csv

# Define the desired mode for the sensors
desired_mode = 'EMG raw (4000 Hz), skin check (74 Hz), ACC 2g (74 Hz), GYRO 250 dps (74 Hz), +/-11mv, 10-850Hz'

# Initialize a dictionary to store data for each channel
recorded_data = []

# Initialize Trigno Base connection
def initialize_trigno_base():
    try:
        # Create the TrignoBase object with a placeholder
        base = TrignoBase(None)
        # Create the DataKernel object and pass the TrignoBase object to it
        data_handler = DataKernel(base)  
        # Set the collection_data_handler attribute of the TrignoBase object
        base.collection_data_handler = data_handler 
        #print(base.TrigBase) #Aero.AeroPy
        print("Trigno Base initialized successfully.")
        return base
    except Exception as e:
        print(f"Error initializing Trigno Base: {e}")
        return None

def process_channel_data(channel_guid, data):
    sensor_type = None

    if channel_guid in emg_guids:
        sensor_type = "EMG"
    elif channel_guid in acc_guids:
        sensor_type = "ACC"
    elif channel_guid in gyro_guids:
        sensor_type = "GYRO"

    if sensor_type is None:
        # Skip if not a recognized sensor type
        return

    for sample in data:
        time_point = sample.Item1
        value = sample.Item2
        print(f"[{sensor_type}] Channel GUID: {channel_guid}, Time: {time_point}, Value: {value}")

        recorded_data.append({
            "sensor_type": sensor_type,
            "channel_guid": channel_guid,
            "time_point": time_point,
            "value": value
        })

# Main function
if __name__ == "__main__":
    base = initialize_trigno_base()
    
    #if Trigno Base inizialized successfully
    if base: 

        base.Connect_Callback() 
        print("Connected to Trigno Base Station")

        emg_guids = []
        skin_guids = []
        acc_guids = []
        gyro_guids = []
        # Get available sensors
        sensors = base.Scan_Callback()  
        print(f"Found {len(sensors)} sensors.")

        component_ids = []

        for sensor in sensors:
            print(f"Component Number: {sensor.Id}")
            component_ids.append(str(sensor.Id))
            for channel in sensor.TrignoChannels:
                print(f"  Channel Name: {channel.Name}, GUID: {channel.Id}") #appear the actually channel type

        sensor_names = base.TrigBase.GetSensorNames()
        # print("\nSensor Names from TrigBase:")
        # for i, name in enumerate(sensor_names):
            # print(f"Sensor {i} Name: {name}")

        for i in range(len(sensors)):
            # print(f"Sensor {i}")
            new_current_mode = base.TrigBase.SetSampleMode(i, desired_mode) #change the channel type into desidered
            # current_mode = base.TrigBase.GetCurrentSensorMode(i)
            # print(f"Current mode for sensor {i}: {current_mode}")

        for sensor in sensors:
            # print(f"Component Number: {sensor.Id}")
            for channel in sensor.TrignoChannels:
                name_ch = channel.Name
                guid = channel.Id
                type_ch = channel.Type
                # print(f"  Channel Name: {channel.Name}, GUID: {channel.Id}, Type: {channel.Type}")
                #to select only EMG channel for each sensor
                if str(channel.Type) == 'EMG':
                    emg_guids.append(guid)
                if str(channel.Type) == 'SkinCheck':
                    skin_guids.append(guid)
                if str(channel.Type) == 'ACC':    
                    acc_guids.append(guid)
                if str(channel.Type) == 'GYRO':
                    gyro_guids.append(guid)
        emg_guids_str = [str(guid) for guid in emg_guids]
        skin_guids_str = [str(guid) for guid in skin_guids]
        acc_guids_str = [str(guid) for guid in acc_guids]
        gyro_guids_str = [str(guid) for guid in gyro_guids]
        print(f"Component number: {component_ids}")
        print(f"EMG GUIDs: {emg_guids_str}")
        print(f"Skin GUIDs: {skin_guids_str}")
        print(f"ACC GUIDs: {acc_guids_str}")
        print(f"GYRO GUIDs: {gyro_guids_str}")

        #verify pipeline state 
        if base.TrigBase.GetPipelineState() == 'Connected':
            print(base.TrigBase.GetPipelineState()) #connected
            #if connected, the pipeline needs configuration
            base.TrigBase.Configure(start_trigger = False, stop_trigger = False)
            print(base.TrigBase.GetPipelineState()) #Armed

        # start data collection
        print("Press 's' to start data collection...")
        keyboard.wait('s') # Wait for 's' key to be pressed
        base.TrigBase.Start(ytdata = True)
        print("Data collection started...")

        # Now stream the data in a loop
        try:
            while True:
                # Check if new YT data is available
                if base.TrigBase.CheckYTDataQueue():  
                    # Get the data as a dictionary
                    yt_data = base.TrigBase.PollYTData()  
                    # Print the data (can be processed further)
                    print(f"YT Data: {yt_data}")  

                    threads = []
                    for channel_guid, data in yt_data.items():
                        thread = threading.Thread(target=process_channel_data, args=(channel_guid, data))
                        threads.append(thread)
                        thread.start()

                    for thread in threads:
                        thread.join()

                time.sleep(1)

                if keyboard.is_pressed('q'):  
                    print("You pressed 'q'. Stopping data stream...")
                    break
                time.sleep(0.1)

        finally:
            base.TrigBase.Stop()
            print("Data stream stopped. Pipeline is now Armed.")
            base.TrigBase.ResetPipeline()
            print("Pipeline reset. Now back to Connected state.")

            # Save the recorded data to a CSV file
            csv_file_path = "recorded_data.csv"
            try:
                with open(csv_file_path, mode="w", newline="") as csv_file:
                    # Write metadata (channel information) at the beginning of the file
                    for sensor in sensors:
                        csv_file.write("Component sensor:\n")
                        csv_file.write(f"Component Number: {str(sensor.Id)} \n")
                        for channel in sensor.TrignoChannels:
                            # csv_file.write("Channel Name,Channel GUID,Channel Type\n")
                            csv_file.write(f"{channel.Name},{channel.Id},{channel.Type}\n")
                    
                    csv_file.write("\n")  # Add a blank line before the data section

                    fieldnames = ["sensor_type", "channel_guid", "time_point", "value"]
                    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

                    # Write the header
                    writer.writeheader()
                    
                    # Write the data
                    for row in recorded_data:
                        writer.writerow(row)

                print(f"Data saved to {csv_file_path}")
            except Exception as e:
                print(f"Error saving data to CSV: {e}")

        


