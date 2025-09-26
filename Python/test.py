from AeroPy.TrignoBase import TrignoBase
from AeroPy.DataManager import DataKernel

class DataHandler():
    def __init__(self, trigno_base):
        self.DataHandler = DataKernel(trigno_base=trigno_base)

# Step 1: Create the TrignoBase object with a placeholder
base = TrignoBase(collection_data_handler=None)

# Step 2: Create the DataKernel object and pass the TrignoBase object to it
data_handler = DataHandler(trigno_base=base)

# Step 3: Set the collection_data_handler attribute of the TrignoBase object
base.collection_data_handler = data_handler

# Now you can use the TrignoBase object as intended
base.Connect_Callback()
print("Connected to Trigno Base Station")

# Scan sensors
base.Scan_Callback()

# Start data collection
print(base.TrigBase.GetPipelineState())
base.Start_Callback(False, False)
print("Data collection started")