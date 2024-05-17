import serial
import csv
import os
import glob

def get_next_filename():
    # List all files matching the pattern and determine the next file index
    existing_files = glob.glob('fall_*.csv')
    max_index = 0
    for filename in existing_files:
        # Extract the number from the filename
        index = int(filename.replace('fall_', '').replace('.csv', ''))
        if index > max_index:
            max_index = index
    return f'fall_{max_index + 1:03}.csv'

def main():
    serial_port = '/dev/cu.usbserial-2130'
    baud_rate = 115200
    ser = serial.Serial(serial_port, baud_rate, timeout=1)

    try:
        csv_file_path = get_next_filename()
        file = open(csv_file_path, 'w', newline='')
        writer = csv.writer(file)
        writer.writerow(['AX', 'AY', 'AZ', 'GX', 'GY', 'GZ'])
        print(f"Collecting data... Current file: {csv_file_path}")

        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').strip()
                if line:
                    data = list(map(float, line.split(',')))
                    writer.writerow(data)

    except KeyboardInterrupt:
        print("Data collection stopped by user.")
    finally:
        file.close()
        ser.close()
        print(f"Data saved to {csv_file_path}. Serial connection closed.")

if __name__ == '__main__':
    main()
