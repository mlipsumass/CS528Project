import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score
import csv
import joblib

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
fall_data = abs(fall_data)
stand_data = np.array(stand_data)
stand_data = abs(stand_data)
walk_data = np.array(walk_data)
walk_data = abs(walk_data)

max_numbers = 5

modified_fall_data = np.zeros((200, 6, max_numbers))
modified_stand_data = np.zeros((100, 6, max_numbers))
modified_walk_data = np.zeros((100, 6, max_numbers))
for i in range(200):
    for j in range(6):
        modified_fall_data[i, 5 - j, :] = np.partition(fall_data[i, :, j], -max_numbers)[-max_numbers:]
        if i < 100:
            modified_stand_data[i, 5 - j, :] = np.partition(stand_data[i, :, j], -max_numbers)[-max_numbers:]
            modified_walk_data[i, 5 - j, :] = np.partition(walk_data[i, :, j], -max_numbers)[-max_numbers:]

combined_data =  np.vstack((modified_fall_data, modified_stand_data, modified_walk_data))

labels = np.array([0 if i < 200 else 1 for i in range(400)])

data_train, data_test, label_train, label_test = train_test_split(combined_data, labels, test_size=0.2, random_state=0)

data_train = data_train.reshape(label_train.shape[0], -1)
data_test = data_test.reshape(label_test.shape[0], -1)

print("KNN training")
knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(data_train, label_train)
print("KNN trained")

y_pred = knn.predict(data_test)
print(combined_data[0])
print(knn.predict(combined_data[0].flatten().reshape(1, -1)))
print(combined_data[250])
print(knn.predict(combined_data[250].flatten().reshape(1, -1)))

accuracy = accuracy_score(label_test, y_pred)
print("Accuracy:", accuracy)

model_filename = 'modified_knn_model.pkl'
joblib.dump(knn, model_filename)
