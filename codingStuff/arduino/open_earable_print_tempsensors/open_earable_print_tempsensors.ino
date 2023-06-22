#include <Wire.h>
#include "Protocentral_MLX90632.h"

#define TCA9548A_MAX_CHANNELS 8
#define TCA9548A_I2C_ADDRESS 0x70

/* The channels which are connected to an MLX90632 sensor */
const uint8_t MLX_CHANNELS[] = {0, 1, 2, 4, 5};
const uint8_t NUM_MLX_CHANNELS = sizeof(MLX_CHANNELS);

bool isDebugMode = true;

/* Create MLX90632 sensor object pointers */
Protocentral_MLX90632* mlxSensors[NUM_MLX_CHANNELS];

/* Object Temperature Array */
float objectTemps[NUM_MLX_CHANNELS];

/* Function prototypes */
uint8_t TCA9548A_ch(uint8_t channel);
bool i2cFailed();

/*****************************************  setup() *************************************************/
void setup() {
  Serial.begin(9600);
  Wire.begin();

  /* iterate all used channels and initialize each sensor individually */
  for (uint8_t i = 0; i < NUM_MLX_CHANNELS; i++) {
    mlxSensors[i] = new Protocentral_MLX90632();
    TCA9548A_ch(MLX_CHANNELS[i]);
    mlxSensors[i]->begin();
  }
}

/*****************************************  loop() *************************************************/
void loop() {
  if (i2cFailed()) {
    Serial.println("I2C Error: Not all I2C sensors found! Use isDebugMode = true to read which sensors fail.");
  } else {
    /* Iterate through all sensors: open channel and read sensor, repeat */
    for (uint8_t i = 0; i < NUM_MLX_CHANNELS; i++) {
      TCA9548A_ch(MLX_CHANNELS[i]);
      objectTemps[i] = mlxSensors[i]->getObjectTemp(); // Get the temperature of the object we're looking at in C
//      if (i == 0) {
        Serial.print("Object temperature of MLX");
        Serial.print(MLX_CHANNELS[i]);
        Serial.print(" = ");
        Serial.print(objectTemps[i], 2);
        Serial.println(" C");  
//      }
    }
  }
  delay(9900);
}


/*****************************************  TCA9548A_ch() *************************************************/
/**
 * Function to enable the chosen channel of the TCA9548A multiplexer.
 * This function only allows one channel to be opened at a time,
 * even though the chip supports multiple channels.
 * Multiple opened channels would cause bus conflicts.
 *
 * @param channel The channel number to be opened.
 * @return I2C error code (0 = success).
 */
uint8_t TCA9548A_ch(uint8_t channel) {
  if (channel < TCA9548A_MAX_CHANNELS) {
    Wire.beginTransmission(TCA9548A_I2C_ADDRESS);
    Wire.write(0x00);
    Wire.write(1 << channel);
    return Wire.endTransmission();
  }
  return 0xFF; // Invalid error code
}


/*****************************************  i2cFailed() *************************************************/
/**
 * Function to test I2C communication chain with MUX (TCA9548A) and multiple MLX sensors.
 * Returns true if all sensors are detected successfully, false otherwise.
 */
bool i2cFailed() {
  uint8_t sensor_counter = 0;

  /* Iterate all sensor channels */
  for (uint8_t i = 0; i < NUM_MLX_CHANNELS; i++) {
    /* Open single MLX channel */
    uint8_t error = TCA9548A_ch(MLX_CHANNELS[i]);

    /* No error */
    if (error == 0) {
      if (isDebugMode) {
        Serial.print("MUX Channel ");
        Serial.print(MLX_CHANNELS[i]);
        Serial.println(" enabled!");
      }
      /* Small delay before communication with sensor */
      delay(1);

      Wire.write(0x3A);
      error = 0xFF; // overwrite error with invalid value
      error = Wire.endTransmission();
      if (error == 0) {
        sensor_counter++;
        if (isDebugMode) {
          Serial.print("MLX ");
          Serial.print(MLX_CHANNELS[i]);
          Serial.println(" found!");
          Serial.println();
        }
      } else {
        if (isDebugMode) {
          Serial.print("MLX Error at channel ");
          Serial.print(MLX_CHANNELS[i]);
          Serial.println("!");
        }
      }
    } else {
      if (isDebugMode) {
        Serial.print("MUX Error at channel ");
        Serial.print(MLX_CHANNELS[i]);
        Serial.print(" with error: ");
        Serial.print(error);
        Serial.println("!");
      }
    }
  }
  if (sensor_counter == NUM_MLX_CHANNELS) {
    return false;
  } else {
    return true;
  }
}
