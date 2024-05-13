import numpy as np
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Flatten, Dense
import csv

noise_standard_deviation = 0.001

###################### Fall Data ######################
fall_data = []

for i in range(1, 201):
    file_name = f"./Data/fall_{i:03d}.csv"

    with open(file_name, 'r') as file:
        csv_reader = csv.reader(file)
        file_data = [row for row in csv_reader][1:]

        for j, measurement in enumerate(file_data):
            file_data[j] = [float(value) for value in measurement]

    # Preprocess data to 200 samples across 2 seconds
    number_samples = len(file_data)
    if number_samples < 200:
        for j in range(200 - number_samples):
            noisy_values = [x + np.random.normal(0, noise_standard_deviation) for x in file_data[-1]]
            file_data.append(noisy_values)
    elif number_samples > 200:
        file_data = file_data[:200]
    
    for ii in range(200):
        if len(file_data[ii]) != 6:
            print(i, ii, len(file_data[ii]))

    fall_data.append(file_data)

###################### Stand Data ######################
stand_data = []

with open('./Data/stand.csv', 'r') as file:
    csv_reader = csv.reader(file)
    all_data = [row for row in csv_reader]

    for i in range(100):

        sample_data = all_data[i * 20:(i + 1) * 20]
        extended_sample_data = []
        for j, measurement in enumerate(sample_data):
            for _ in range(10):
                float_measurements = [float(value) for value in measurement]
                noisy_values = [x + np.random.normal(0, noise_standard_deviation) for x in float_measurements]
                extended_sample_data.append(noisy_values)

        stand_data.append(extended_sample_data)

###################### Walk Data ######################
walk_data = []

with open('./Data/walk.csv', 'r') as file:
    csv_reader = csv.reader(file)
    all_data = [row for row in csv_reader]

    for i in range(100):

        sample_data = all_data[i * 20:(i + 1) * 20]
        extended_sample_data = []
        for j, measurement in enumerate(sample_data):
            for _ in range(10):
                float_measurements = [float(value) for value in measurement]
                noisy_values = [x + np.random.normal(0, noise_standard_deviation) for x in float_measurements]
                extended_sample_data.append(noisy_values)

        walk_data.append(extended_sample_data)

fall_data = np.array(fall_data)
stand_data = np.array(stand_data)
walk_data = np.array(walk_data)

combined_data =  np.vstack((fall_data, stand_data, walk_data))
labels = np.array([0 if i < 200 else 1 for i in range(400)])

data_train, data_test, label_train, label_test = train_test_split(combined_data, labels, test_size=0.2, random_state=0)

model = Sequential([
    Flatten(input_shape=(6, 200)),
    Dense(128, activation='relu'),
    Dense(64, activation='relu'),
    Dense(32, activation='relu'),
    Dense(2, activation='softmax')
])

print("Neural network training")
model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])
model.fit(data_train, label_train, epochs=10, batch_size=32, validation_split=0.2)
print("Neural network trained")

test_loss, test_acc = model.evaluate(data_test, label_test)
print("Accuracy:", test_acc)
