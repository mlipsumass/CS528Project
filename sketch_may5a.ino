#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>

#define enviornmentService BLEUUID((uint16_t)0x181A)
#define MPU6050_SDA_PIN 0 // GPIO pin for SDA
#define MPU6050_SCL_PIN 1 // GPIO pin for SCL

bool deviceConnected = false;

void getData();
void BLETransfer(int16_t);

float temperature = -1000;

float x_acceleration = 0;
float y_acceleration = 0;
float z_acceleration = 0;

float x_gyroscope = 0;
float y_gyroscope = 0;
float z_gyroscope = 0;

uint32_t sample_index = 0;

Adafruit_MPU6050 mpu;

BLECharacteristic dataCharacteristic(
    BLEUUID((uint16_t)0x2A6E),
    BLECharacteristic::PROPERTY_READ |
        BLECharacteristic::PROPERTY_NOTIFY);

class MyServerCallbacks : public BLEServerCallbacks
{
  void onConnect(BLEServer *pServer)
  {
    deviceConnected = true;
  };

  void onDisconnect(BLEServer *pServer)
  {
    deviceConnected = false;
  }
};

void setup()
{
  Serial.begin(115200);
  while (!Serial)
    delay(10); // will pause Zero, Leonardo, etc until serial console opens

  // Begin I2C communication with custom GPIO pins
  Wire.begin(MPU6050_SDA_PIN, MPU6050_SCL_PIN);

  Serial.println("Adafruit MPU6050 test!");

  // Try to initialize!
  if (!mpu.begin())
  {
    Serial.println("Failed to find MPU6050 chip");
    while (1)
    {
      delay(10);
    }
  }
  Serial.println("MPU6050 Found!");

  mpu.setAccelerometerRange(MPU6050_RANGE_2_G);
  Serial.print("Accelerometer range set to: ");
  switch (mpu.getAccelerometerRange())
  {
  case MPU6050_RANGE_2_G:
    Serial.println("+-2G");
    break;
  case MPU6050_RANGE_4_G:
    Serial.println("+-4G");
    break;
  case MPU6050_RANGE_8_G:
    Serial.println("+-8G");
    break;
  case MPU6050_RANGE_16_G:
    Serial.println("+-16G");
    break;
  }
  mpu.setGyroRange(MPU6050_RANGE_250_DEG);
  Serial.print("Gyro range set to: ");
  switch (mpu.getGyroRange())
  {
  case MPU6050_RANGE_250_DEG:
    Serial.println("+- 250 deg/s");
    break;
  case MPU6050_RANGE_500_DEG:
    Serial.println("+- 500 deg/s");
    break;
  case MPU6050_RANGE_1000_DEG:
    Serial.println("+- 1000 deg/s");
    break;
  case MPU6050_RANGE_2000_DEG:
    Serial.println("+- 2000 deg/s");
    break;
  }

  mpu.setFilterBandwidth(MPU6050_BAND_260_HZ);
  Serial.print("Filter bandwidth set to: ");
  switch (mpu.getFilterBandwidth())
  {
  case MPU6050_BAND_260_HZ:
    Serial.println("260 Hz");
    break;
  case MPU6050_BAND_184_HZ:
    Serial.println("184 Hz");
    break;
  case MPU6050_BAND_94_HZ:
    Serial.println("94 Hz");
    break;
  case MPU6050_BAND_44_HZ:
    Serial.println("44 Hz");
    break;
  case MPU6050_BAND_21_HZ:
    Serial.println("21 Hz");
    break;
  case MPU6050_BAND_10_HZ:
    Serial.println("10 Hz");
    break;
  case MPU6050_BAND_5_HZ:
    Serial.println("5 Hz");
    break;
  }
  // ############################################## Bluetooth Start ##############################################
  // Create the BLE Device
  BLEDevice::init("MyESP32");

  // Create the BLE Server
  BLEServer *pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks());

  // Create the BLE Service
  BLEService *pEnviornment = pServer->createService(enviornmentService);

  // Create a BLE Characteristic
  pEnviornment->addCharacteristic(&dataCharacteristic);

  // https://www.bluetooth.com/specifications/gatt/viewer?attributeXmlFile=org.bluetooth.descriptor.gatt.client_characteristic_configuration.xml
  // Create a BLE Descriptor
  dataCharacteristic.addDescriptor(new BLE2902());

  BLEDescriptor DataDescriptor(BLEUUID((uint16_t)0x2901));
  DataDescriptor.setValue("Ax, Ay, Az, Gx, Gy, Gz");
  dataCharacteristic.addDescriptor(&DataDescriptor);

  pServer->getAdvertising()->addServiceUUID(enviornmentService);

  // Start the service
  pEnviornment->start();

  // Start advertising
  pServer->getAdvertising()->start();
  Serial.println("Waiting a client connection to notify...");
}

void loop()
{
  getData();

  // Create a buffer to hold the data
  uint8_t buffer[28];

  // Copy the float values into the buffer
  memcpy(buffer, &x_acceleration, sizeof(float));
  memcpy(buffer + 4, &y_acceleration, sizeof(float));
  memcpy(buffer + 8, &z_acceleration, sizeof(float));
  memcpy(buffer + 12, &x_gyroscope, sizeof(float));
  memcpy(buffer + 16, &y_gyroscope, sizeof(float));
  memcpy(buffer + 20, &z_gyroscope, sizeof(float));
  memcpy(buffer + 24, &sample_index, sizeof(uint32_t));
  // int16_t value = 123;
  // BLETransfer(value);
  dataCharacteristic.setValue((uint8_t *)&buffer, 28);
  dataCharacteristic.notify();
  delay(10);
}

// void BLETransfer(int16_t val){
//   int16_t value = 43;
//   dataCharacteristic.setValue((uint8_t*)&val, 2);
//   dataCharacteristic.notify();
// }

void getData()
{
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);

  x_acceleration = a.acceleration.x;
  y_acceleration = a.acceleration.y;
  z_acceleration = a.acceleration.z;

  x_gyroscope = g.gyro.x;
  y_gyroscope = g.gyro.y;
  z_gyroscope = g.gyro.z;

  Serial.println(g.gyro.x);
  Serial.println(g.gyro.y);
  Serial.println(g.gyro.z);

  sample_index = sample_index + 1;
}
