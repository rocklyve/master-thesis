#include <Wire.h>
#include "Protocentral_MLX90632.h"
#include "TCA9548A.h"
#include "SD_Logger.h"
#include "IMU_Sensor.h"

TCA9548A mux;

const uint8_t MLX_CHANNELS[] = {0,1,2,3,4,5,6,7};
const uint8_t amount_of_sensors = sizeof(MLX_CHANNELS);
Protocentral_MLX90632 mlx[amount_of_sensors];


// Refresh rate configuration values
const uint16_t EE_MEAS_1_ADDR = 0x24E1;
const uint16_t EE_MEAS_1_32HZ_VALUE = 0x860D;
const uint16_t EE_MEAS_2_ADDR = 0x24E2;
const uint16_t EE_MEAS_2_32HZ_VALUE = 0x861D;
const uint16_t REFRESH_RATE_VALUE = 6; // Value for 32Hz refresh rate

bool isDebugMode = false;
const int buttonPin = 5; // Button pin connected to D5

volatile bool stopMeasurementButtonPressedFlag = false; // Volatile flag used in the interrupt routine

SD_Logger *logger;
IMU_Sensor imu;

const unsigned long doubleClickTimeframe = 2000;  // Timeframe for double click in milliseconds
unsigned long lastButtonPressTime = 0;  // Stores the timestamp of the last button press

// Function prototypes
void setupSensors();
void setupButtonInterrupt();
void initializeMLXSensor(Protocentral_MLX90632 &sensor, uint8_t index);
void initializeIMU();
void readSensorData(int data[]);
void saveDataToSDCard(int data[]);
void checkButtonPress();
void handleButtonPress();

/*****************************************  setup() *************************************************/
void setup() {
  Serial.begin(9600);
  while (!Serial) {};

  setupButtonInterrupt();
  initializeIMU();
  setupSensors();

  logger = new SD_Logger();
  // logger->set_name("data.csv");  // Set the name of the log file
  if (!logger->begin()) {
    Serial.println("SD Logger initialization failed!");
    while (1);  // Stop execution if SD Logger initialization fails
  } else {
    Serial.println("Logger initialized and CSV name set.");
  }
}

/*****************************************  loop() *************************************************/
void loop() {
  int amount_of_data_columns = amount_of_sensors + 9; 
  int data[amount_of_data_columns + 1];
  data[0] = amount_of_data_columns;  // Number of data elements

  if (stopMeasurementButtonPressedFlag) {
    saveDataToSDCard(data, -1);
    // Logging the data
    logger->end();
    Serial.println("Pressed stop, now finished");
    while (true);
  }
  checkButtonPress(); 
  readSensorData(data);
  saveDataToSDCard(data, 1);

  // print data
  if (data[1] != -1) {
    Serial.print("Data: ");
  for (int i = 1; i <= amount_of_sensors; i++) {
    Serial.print(data[i]);
    if (i != amount_of_sensors) {
      Serial.print(", ");
    }
  }
  Serial.println();

  Serial.print("IMU [");
  for (int i = 6; i <= 14; i++) {
    Serial.print(data[i]);
    if (i != 14) {
      Serial.print(", ");
    }
  }
  Serial.println("]");
  Serial.println("");
  }
}

void setupSensors() {
  Wire.begin();
  Wire.setClock(400000);
  // Initialize the multiplexer
  mux.begin();
  // Initialize MLX sensors...
  for (uint8_t i = 0; i < amount_of_sensors; i++) {
    initializeMLXSensor(mlx[i], i);
  }
}

void setupButtonInterrupt() {
  pinMode(buttonPin, INPUT_PULLUP); // Set button pin as input with internal pull-up resistor
  attachInterrupt(digitalPinToInterrupt(buttonPin), buttonPressed, FALLING); // Attach interrupt to the button pin, trigger on FALLING edge
}

void initializeMLXSensor(Protocentral_MLX90632 &sensor, uint8_t index) {
  mux.closeAll();
  mux.openChannel(MLX_CHANNELS[index]);

  if (!sensor.begin()) {
    Serial.print("Sensor ");
    Serial.print(index);
    Serial.println(" not found. Check wiring or address.");
  } else {
    Serial.print("Sensor ");
    Serial.print(index);
    Serial.println(" found!");
  }

  sensor.pre_get_Temp();
}

void initializeIMU() {
    imu.start();
}

void readSensorData(int data[]) {
  // Read MLX sensor data...
  for (uint8_t i = 0; i < amount_of_sensors; i++) {
    mux.closeAll();
    mux.openChannel(MLX_CHANNELS[i]);
    
    if (mlx[i].dataAvailable()) {
      data[i + 1] = mlx[i].get_Temp() * 100;
      mlx[i].pre_get_Temp();
    } else {
      data[i + 1] = -1;
    }
  }
  // now store IMU data
  float accelX, accelY, accelZ;
  imu.get_acc(accelX, accelY, accelZ);
  data[6] = accelX * 100;
  data[7] = accelY * 100;
  data[8] = accelZ * 100;

  // Get gyroscope data
  float gyroX, gyroY, gyroZ;
  imu.get_gyro(gyroX, gyroY, gyroZ);
  data[9] = gyroX * 100;
  data[10] = gyroY * 100;
  data[11] = gyroZ * 100;

  // Get magnetometer data
  float magX, magY, magZ;
  imu.get_mag(magX, magY, magZ);
  data[12] = magX * 100;
  data[13] = magY * 100;
  data[14] = magZ * 100;
}

void saveDataToSDCard(int data[], int id) {
  unsigned int timestamp = millis();
  logger->data_callback(id, timestamp, (uint8_t*) data);
}

void checkButtonPress() {
  if (stopMeasurementButtonPressedFlag) {
    handleButtonPress();
  }
}

void handleButtonPress() {
  unsigned int timestamp = millis();
  logger->data_callback(-1, timestamp, nullptr);
  // Logging the data

  logger->end();
  Serial.println("Pressed stop, now finished");
  while (true);
}

void buttonPressed() {
  unsigned long currentButtonPressTime = millis();

  if (currentButtonPressTime - lastButtonPressTime < doubleClickTimeframe) {
    stopMeasurementButtonPressedFlag = true;
    lastButtonPressTime = 0;
  } else {
    lastButtonPressTime = currentButtonPressTime;
  }
}