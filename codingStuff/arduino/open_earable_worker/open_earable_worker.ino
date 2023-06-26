#include <Wire.h>
#include "Protocentral_MLX90632.h"
#include "TCA9548A.h"
#include "SD_Logger.h"
#include "IMU_Sensor.h"

TCA9548A mux;
Protocentral_MLX90632 mlx[5];
const uint8_t MLX_CHANNELS[] = {0, 1, 2, 4, 5};

bool isDebugMode = false;
int counter = 0;

SD_Logger * logger;
IMU_Sensor imu;

/*****************************************  setup() *************************************************/
void setup() {
  Serial.begin(9600);
  while (!Serial) {};

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
  } else{
    Serial.println("Logger initialized and CSV name set.");
  }  
}

/*****************************************  loop() *************************************************/
void loop() { 
  int amount_of_data_columns = 5 + 9; 
  int data[amount_of_data_columns + 1];
  data[0] = amount_of_data_columns;  // Number of data elements

  if (counter == 1000) {
    unsigned int timestamp = millis();
    logger->data_callback(-1, timestamp, (uint8_t*)data);
    // Logging the data
    logger->end();
    while (true);
  } else {
    counter += 1;
    // Get the current timestamp
    for (uint8_t i = 0; i < 5; i++) {
      mux.closeAll();
      mux.openChannel(MLX_CHANNELS[i]);
      
      data[i+1] = mlx[i].getSensorTemp() * 100;
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
    Serial.print("Data: ");
    Serial.print(data[1]);
    Serial.print(", ");
    Serial.print(data[2]);
    Serial.print(", ");
    Serial.print(data[3]);
    Serial.print(", ");
    Serial.print(data[4]);
    Serial.print(", ");
    Serial.println(data[5]);
    Serial.print("IMU [");
    Serial.print(data[6]);
    Serial.print(", ");
    Serial.print(data[7]);
    Serial.print(", ");
    Serial.print(data[8]);
    Serial.print(", ");
    Serial.print(data[9]);
    Serial.print(", ");
    Serial.print(data[10]);
    Serial.print(", ");
    Serial.print(data[11]);
    Serial.print(", ");
    Serial.print(data[12]);
    Serial.print(", ");
    Serial.print(data[13]);
    Serial.print(", ");
    Serial.print(data[14]);
    Serial.println("]");
    Serial.println("");
    logger->data_callback(1, timestamp, (uint8_t*) data);
  }
}
