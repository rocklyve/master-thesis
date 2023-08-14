#include <Wire.h>
#include "Protocentral_MLX90632.h"
#include "TCA9548A.h"
#include "SD_Logger.h"
#include "IMU_Sensor.h"

TCA9548A mux;
SD_Logger *logger;
IMU_Sensor imu;

bool isDebugMode = false;

const uint8_t MLX_CHANNELS[] = {4,6,7};
const uint8_t amount_of_sensors = sizeof(MLX_CHANNELS);
Protocentral_MLX90632 mlx[amount_of_sensors];
int last_data_temp_line[amount_of_sensors];

const int buttonPin = 5; // Button pin connected to D5
volatile bool stopMeasurementButtonPressedFlag = false; // Volatile flag used in the interrupt routine
const unsigned long doubleClickTimeframe = 2000;  // Timeframe for double click in milliseconds
unsigned long lastButtonPressTime = 0;  // Stores the timestamp of the last button press

const int LED_R_PIN = A7; // GPIO 16
const int LED_G_PIN = A6; // GPIO 17
const int LED_B_PIN = A0; // GPIO 25

int measurement_state = 1; // Initial measurement state

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
  changeLEDColor(measurement_state); // Change LED color based on initial measurement state
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
  saveDataToSDCard(data, measurement_state);

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

  delay(20);
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
  mux.openChannel(MLX_CHANNELS[index]);

  if (!sensor.begin()) {
    Serial.print("Sensor ");
    Serial.print(index);
    Serial.println(" not found. Check wiring or address.");
  } else {
    Serial.print("Sensor ");
    Serial.print(index);
    Serial.println(" found!");
    last_data_temp_line[index] = 0;
    // sensor.pre_get_Temp();
    // delay(50);
  }
  mux.closeChannel(MLX_CHANNELS[index]);
}

void initializeIMU() {
    imu.start();
}

void readSensorData(int data[]) {
  // Read MLX sensor data...
  for (uint8_t i = 0; i < amount_of_sensors; i++) {
    mux.openChannel(MLX_CHANNELS[i]);
    delay(1);
    data [i + 1] = mlx[i].get_Temp() * 100;
    
    // if (mlx[i].dataAvailable()) {
    //   mlx_data_fetch_counter[i] = 0;
    //   data[i + 1] = mlx[i].get_Temp() * 100;
    //   delay(50);
    //   mlx[i].pre_get_Temp();
    //   delay(50);
    // } else {
    //   mlx_data_fetch_counter[i] = mlx_data_fetch_counter[i] + 1;
    //   if (mlx_data_fetch_counter[i] > MLX_TIMEOUT) {
    //     mlx[i].pre_get_Temp();
    //     Serial.print("Timeout reached, clear data for mlx ");
    //     Serial.println(MLX_CHANNELS[i]);
    //   }
    //   data[i + 1] = -1;
    // }
    delay(1);
    mux.closeChannel(MLX_CHANNELS[i]);
  }
  // now store IMU data
  int imu_muliplicator = 10000;
  float accelX, accelY, accelZ;
  imu.get_acc(accelX, accelY, accelZ);
  data[6] = accelX * imu_muliplicator;
  data[7] = accelY * imu_muliplicator;
  data[8] = accelZ * imu_muliplicator;

  // Get gyroscope data
  float gyroX, gyroY, gyroZ;
  imu.get_gyro(gyroX, gyroY, gyroZ);
  data[9] = gyroX * imu_muliplicator;
  data[10] = gyroY * imu_muliplicator;
  data[11] = gyroZ * imu_muliplicator;

  // Get magnetometer data
  float magX, magY, magZ;
  imu.get_mag(magX, magY, magZ);
  data[12] = magX * imu_muliplicator;
  data[13] = magY * imu_muliplicator;
  data[14] = magZ * imu_muliplicator;
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
    incrementMeasurementState();
    changeLEDColor(measurement_state);
  }
}

void incrementMeasurementState() {
  measurement_state++;
}

void changeLEDColor(int id) {
  int redValue = 0;
  int greenValue = 0;
  int blueValue = 0;

  // Adjust color values based on measurement_state (id)
  if (id % 3 == 0) { // Every third state (1, 4, 7, etc.) - Red
    redValue = 255;
  } else if (id % 3 == 1) { // Every third state + 1 (2, 5, 8, etc.) - Green
    greenValue = 255;
  } else { // Every third state + 2 (3, 6, 9, etc.) - Blue
    blueValue = 255;
  }

  analogWrite(LED_R_PIN, redValue); // GPIO 16 (A7)
  analogWrite(LED_G_PIN, greenValue); // GPIO 17 (A6)
  analogWrite(LED_B_PIN, blueValue); // GPIO 25 (A0)
}