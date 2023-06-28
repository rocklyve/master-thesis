#include <Wire.h>
#include "Protocentral_MLX90632.h"
#include "TCA9548A.h"
#include "SD_Logger.h"
#include "IMU_Sensor.h"

TCA9548A mux;
Protocentral_MLX90632 mlx[5];
const uint8_t MLX_CHANNELS[] = {0, 1, 2, 4, 5};

bool isDebugMode = false;
unsigned long buttonPressTime = 0;
const int debounceDelay = 50; // Debounce delay in milliseconds
const int buttonPin = 5; // Button pin connected to D5

volatile bool buttonPressedFlag = false; // Volatile flag used in the interrupt routine

SD_Logger *logger;
IMU_Sensor imu;

/*****************************************  setup() *************************************************/
void setup() {
  Serial.begin(9600);
  while (!Serial) {};

  pinMode(buttonPin, INPUT_PULLUP); // Set button pin as input with internal pull-up resistor

  // Attach interrupt to the button pin, trigger on CHANGE (both rising and falling edges)
  attachInterrupt(digitalPinToInterrupt(buttonPin), buttonPressed, CHANGE);

  // WIRE SETUP
  Wire.begin();
  // Initialize the multiplexer
  mux.begin();
  imu.start();

  // Select the multiplexer channel for each sensor
  for (uint8_t i = 0; i < 5; i++) {
    mux.closeAll();
    mux.openChannel(MLX_CHANNELS[i]);

    // Initialize the sensor on the selected channel
    if (!mlx[i].begin()) {
      Serial.print("Sensor ");
      Serial.print(i);
      Serial.println(" not found. Check wiring or address.");
    }
  }

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
  int amount_of_data_columns = 5 + 9; 
  int data[amount_of_data_columns + 1];
  data[0] = amount_of_data_columns;  // Number of data elements

  if (buttonPressedFlag) {
    // Check if button was pressed twice within 2 seconds
    if (millis() - buttonPressTime < 2000) {
      unsigned int timestamp = millis();
      logger->data_callback(-1, timestamp, nullptr);
      // Logging the data
      logger->end();
      Serial.println("Pressed stop, now finished");
      while (true);
    } else {
      buttonPressedFlag = false; // Reset the flag if not meeting the conditions
    }
  }

  // Get the current timestamp
  for (uint8_t i = 0; i < 5; i++) {
    mux.closeAll();
    mux.openChannel(MLX_CHANNELS[i]);

    data[i + 1] = mlx[i].getSensorTemp() * 100;
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

  // now save to SD card
  unsigned int timestamp = millis();

  // print data
  Serial.print("Data: ");
  for (int i = 1; i <= 5; i++) {
    Serial.print(data[i]);
    if (i != 5) {
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

  // save data
  logger->data_callback(1, timestamp, (uint8_t*) data);
}

/*****************************************  Button Interrupt Handling *************************************************/
void buttonPressed() {
  // Debounce the button
  if (millis() - buttonPressTime > debounceDelay) {
    buttonPressTime = millis();
    buttonPressedFlag = true;
  }
}