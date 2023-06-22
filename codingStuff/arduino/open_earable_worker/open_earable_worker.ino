#include <Wire.h>
#include "Protocentral_MLX90632.h"
#include "TCA9548A.h"
#include "SD_Logger.h"

TCA9548A mux;
Protocentral_MLX90632 mlx[5];
const uint8_t MLX_CHANNELS[] = {0, 1, 2, 4, 5};

bool isDebugMode = false;
int counter = 0;

SD_Logger * logger;

/*****************************************  setup() *************************************************/
void setup() {
  Serial.begin(9600);
  while (!Serial) {};

  // WIRE SETUP
  Wire.begin();
  // Initialize the multiplexer
  mux.begin();

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

  // SD SETUP
  Serial.println("Start setup");

  logger = new SD_Logger();
  
  // logger->set_name("data.csv");  // Set the name of the log file
  if (!logger->begin()) {
    Serial.println("SD Logger initialization failed!");
    while (1);  // Stop execution if SD Logger initialization fails
  } else{ 
  Serial.println("set csv name"); 

  Serial.println("Logger initialized and CSV name set.");
  }  
}

/*****************************************  loop() *************************************************/
void loop() {  
  int data[6];
  data[0] = 5;  // Number of data elements

  if (counter == 200) {
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
      
      float temperature = mlx[i].getObjectTemp();
      data[i+1] = temperature * 100;

      // Serial.print("Sensor ");
      // Serial.print(i);
      // Serial.print(" Temperature: ");
      // Serial.print(temperature);
      // Serial.print(" °C, counter: ");
      // Serial.println(counter);
    }
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
    Serial.print(data[5]);
    Serial.println("!");
    logger->data_callback(1, timestamp, (uint8_t*) data);
  }
}
