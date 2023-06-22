// #include <Wire.h>
#include "SD_Logger.h"

#define TCA9548A_MAX_CHANNELS 8
#define TCA9548A_I2C_ADDRESS 0x70

/* The channels which are connected to an MLX90632 sensor */
const uint8_t MLX_CHANNELS[] = {0, 1, 2, 4, 5};
const uint8_t NUM_MLX_CHANNELS = sizeof(MLX_CHANNELS);

bool isDebugMode = false;

bool flag = false;

SD_Logger * logger;

/* Object Temperature Array */
float objectTemps[NUM_MLX_CHANNELS];

/*****************************************  setup() *************************************************/
void setup() {
  Serial.begin(9600);
  while (!Serial) {};
  
  // Wire.begin();
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
  if (flag) return;
  
  Serial.println("start loop");  //Simulating data to be logged
  
  int data[4];
   data[0] = 3;  // Number of data elements
   data[1] = 10;
   data[2] = 11;
   data[3] = 12;
  
   unsigned int timestamp = millis();  // Get the current timestamp

   Serial.println("now callback");
  
  // // Logging the data
   logger->data_callback(1, timestamp, (uint8_t*) data);
   logger->data_callback(2, timestamp, (uint8_t*)data);
   logger->data_callback(3, timestamp, (uint8_t*)data);
   logger->data_callback(-1, timestamp, (uint8_t*)data);

  logger->end();
  flag = true;

  Serial.println("wait 10 seconds");
  delay(100);  // Delay between logging data
}
