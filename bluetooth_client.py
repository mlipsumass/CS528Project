import asyncio
from bleak import BleakClient
import struct
from queue import Queue
import joblib
import numpy as np

CHARACTERISTIC_UUID = "00002A6E-0000-1000-8000-00805F9B34FB"
DEVICE_UUID = "33DE9560-3100-C7AC-E968-A5C054F81037"

samples_queue = Queue()

window_size = 50

model_filename = "modified_knn_model.pkl"

async def connect_to_esp32_device(mac_address):
    last_sample_number = None
    last_sample_batch = None
    calculate_fall = False

    loaded_model = joblib.load(model_filename)

    async with BleakClient(mac_address) as client:
        
        # Connect to the ESP32
        await client.connect()
        services = await client.get_services()
        
        # Find the correct service
        for service in services:

            # Find the correct characteristics in the selected server
            characteristics = service.characteristics
            for characteristic in characteristics:

                # Repeatedly read the data values collected from the ESP32
                while True:
                    
                    # The byte data of the characteristic
                    value = await client.read_gatt_char(CHARACTERISTIC_UUID)
                    x_accel, y_accel, z_accel, x_gyro, y_gyro, z_gyro = struct.unpack('ffffff', value[:24])
                    sample_number = struct.unpack('I', value[24:])[0]

                    # Scale acceleration values for sensitivity
                    sensitivity_value = 5
                    x_accel *= sensitivity_value
                    y_accel *= sensitivity_value
                    z_accel *= sensitivity_value

                    # Calculate how many datapoints were missed
                    if last_sample_number is None:
                        sample_difference = 1
                        last_sample_number = sample_number
                    else:
                        sample_difference = sample_number - last_sample_number
                        last_sample_number = sample_number

                    # Add samples to the queue
                    for _ in range(sample_difference):
                        samples_queue.put([x_accel, y_accel, z_accel, x_gyro, y_gyro, z_gyro])

                    # Calculate when to recalculate the fall detection algorithm on the sample batch
                    if last_sample_batch is None:
                        last_sample_batch = sample_number
                    elif sample_number >= last_sample_batch + window_size:
                        last_sample_batch += window_size
                        calculate_fall = True

                    read_loop(calculate_fall, samples_queue, loaded_model)

                    if calculate_fall:
                        calculate_fall = False

def read_loop(calculate_fall, samples_queue, loaded_model):

    if calculate_fall and samples_queue.qsize() > 190:
        batch_list = list(samples_queue.queue)

        if len(batch_list) > 200:
            batch_list = batch_list[:200]
        elif len(batch_list) < 200:
            for _ in range(200 - len(batch_list)):
                batch_list.append(batch_list[-1])

        batch_list = np.array(batch_list)

        # Model prediction
        max_numbers = 5
        modified_data = np.zeros((1, 6, max_numbers))
        batch_list = np.abs(batch_list)
        for j in range(6):
            modified_data[0, j, :] = np.partition(batch_list[:, j], -max_numbers)[-max_numbers:]
        prediction = loaded_model.predict(modified_data.flatten().reshape(1, -1))[0]

        while samples_queue.qsize() > 200 - window_size:
            samples_queue.get()

        try:
            with open("./FallDetected.txt", "w") as file:
                file.write(str(1 - prediction))
        except FileNotFoundError:
            print("Data.txt file not found")


# Asynchronously run the bluetooth low energy search, connect, and data
asyncio.run(connect_to_esp32_device(DEVICE_UUID))
