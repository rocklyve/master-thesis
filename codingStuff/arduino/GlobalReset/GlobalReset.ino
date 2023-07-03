#include "Wire.h"
#include "SparkFun_MLX90632_Arduino_Library.h"
#include "TCA9548A.h"

TCA9548A mux;
MLX90632 mlx[5];
const uint8_t MLX_CHANNELS[] = {0, 1, 2, 4, 5};

// Refresh rate configuration values
const uint16_t EE_MEAS_1_ADDR = 0x24E1;
const uint16_t EE_MEAS_1_32HZ_VALUE = 0x860D;
const uint16_t EE_MEAS_2_ADDR = 0x24E2;
const uint16_t EE_MEAS_2_32HZ_VALUE = 0x861D;
const uint16_t REFRESH_RATE_VALUE = 6; // Value for 32Hz refresh rate

const uint16_t GLOBAL_TMP_SENSOR_RESET_ADDRESS = 0x0000;
const uint16_t GLOBAL_TMP_SENSOR_RESET_VALUE   = 0x0000;

const uint16_t TMP_SENSOR_ADDRESS = 0x0000;
const uint16_t TMP_SENSOR_VALUE   = 0x0000;

bool isDebugMode = false;
const int buttonPin = 5; // Button pin connected to D5

volatile bool stopMeasurementButtonPressedFlag = false; // Volatile flag used in the interrupt routine

const unsigned long doubleClickTimeframe = 2000;  // Timeframe for double click in milliseconds
unsigned long lastButtonPressTime = 0;

/*****************************************  setup() *************************************************/
void setup() {
  Serial.begin(9600);
  while (!Serial) {};

  // pinMode(buttonPin, INPUT_PULLUP); // Set button pin as input with internal pull-up resistor

  // Attach interrupt to the button pin, trigger on FALLING edge
  // attachInterrupt(digitalPinToInterrupt(buttonPin), buttonPressed, FALLING);

  // WIRE SETUP
  Wire.begin();
  // Wire.setClock(400000);
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
    } else {
      if (i == 1) {

      
      mlx[i].enableDebugging(Serial);
        // Serial.println("Now make global reset");
        // Wire.beginTransmission(GLOBAL_TMP_SENSOR_RESET_ADDRESS);
        // Wire.write(GLOBAL_TMP_SENSOR_RESET_VALUE);
        // delay(1000);
        // uint8_t transmissionResult = Wire.endTransmission();

        // Serial.print("Transmission Result: ");
        // Serial.println(transmissionResult);

        // ********************* write EE_MEAS_1 *************************************

        //readRegister16 returns a status value not the value found at the memory location
        //We have to pass in a container for readRegister to store the data into
        uint16_t valueInMemory; //Create a container
        mlx[i].readRegister16(EE_MEAS_1_ADDR, valueInMemory);
        Serial.print("Value stored in EE_MEAS_1_ADDR: 0x");
        Serial.println(valueInMemory, HEX);

        //Write a new value to EE_MEAS_1_ADDR register.
        mlx[i].writeRegister16(0x0000, 0x0000);
        delay(1000);

        mlx[i].readRegister16(EE_MEAS_1_ADDR, valueInMemory);
        Serial.print("New value stored in EE_MEAS_1_ADDR (should be 0x860D): 0x");
        Serial.println(valueInMemory, HEX);


        // ********************* write EE_MEAS_2 *************************************


        uint16_t valueInMemory2; //Create a container
        mlx[i].readRegister16(EE_MEAS_2_ADDR, valueInMemory);
        Serial.print("Value stored in EE_MEAS_2_ADDR: 0x");
        Serial.println(valueInMemory2, HEX);

        //Write a new value to EE_MEAS_2_ADDR register.
        mlx[i].writeRegister16(0x0000, 0x0000);
        delay(1000);

        mlx[i].readRegister16(EE_MEAS_2_ADDR, valueInMemory2);
        Serial.print("New value stored in EE_MEAS_2_ADDR (should be 0x861D): 0x");
        Serial.println(valueInMemory2, HEX);

        Serial.println("Done");
    }
    }
  }
}

/*****************************************  loop() *************************************************/
void loop() {
  // int amount_of_data_columns = 5; 
  // int data[amount_of_data_columns + 1];
  // data[0] = amount_of_data_columns;  // Number of data elements

  // if (stopMeasurementButtonPressedFlag) {
  //   unsigned int timestamp = millis();
  //   Serial.println("Pressed stop, now finished");
  //   while (true);
  // }

  // // Get the current timestamp
  // for (uint8_t i = 0; i < 5; i++) {
  //   mux.closeAll();
  //   mux.openChannel(MLX_CHANNELS[i]);

  //   data[i + 1] = mlx[i].getObjectTemp() * 100;
  // }

  // // print data
  // Serial.print("Data: ");
  // for (int i = 1; i <= 5; i++) {
  //   Serial.print(data[i]);
  //   if (i != 5) {
  //     Serial.print(", ");
  //   }
  // }
  // Serial.println();
}