#include "Wire.h"
#include "Protocentral_MLX90632.h"
#include "TCA9548A.h"

TCA9548A mux;
Protocentral_MLX90632 mlx[5];
const uint8_t MLX_CHANNELS[] = {0, 1, 2, 4, 5};

// Refresh rate configuration values
const uint16_t EE_MEAS_1_ADDR = 0x24E1;
const uint16_t EE_MEAS_1_32HZ_VALUE = 0x860D;
const uint16_t EE_MEAS_2_ADDR = 0x24E2;
const uint16_t EE_MEAS_2_32HZ_VALUE = 0x861D;
const uint16_t REFRESH_RATE_VALUE = 6; // Value for 32Hz refresh rate

bool isDebugMode = false;
const int buttonPin = 5; // Button pin connected to D5

volatile bool stopMeasurementButtonPressedFlag = false; // Volatile flag used in the interrupt routine

const unsigned long doubleClickTimeframe = 2000;  // Timeframe for double click in milliseconds
unsigned long lastButtonPressTime = 0; 

/*****************************************  setup() *************************************************/
void setup() {
  Serial.begin(9600);
  while (!Serial) {};

  pinMode(buttonPin, INPUT_PULLUP); // Set button pin as input with internal pull-up resistor

  // Attach interrupt to the button pin, trigger on FALLING edge
  attachInterrupt(digitalPinToInterrupt(buttonPin), buttonPressed, FALLING);

  // WIRE SETUP
  Wire.begin();
  Wire.setClock(400000);
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
}

/*****************************************  loop() *************************************************/
void loop() {
  int amount_of_data_columns = 5; 
  int data[amount_of_data_columns + 1];
  data[0] = amount_of_data_columns;  // Number of data elements

  if (stopMeasurementButtonPressedFlag) {
    unsigned int timestamp = millis();
    Serial.println("Pressed stop, now finished");
    while (true);
  }

  // Get the current timestamp
  for (uint8_t i = 0; i < 5; i++) {
    mux.closeAll();
    mux.openChannel(MLX_CHANNELS[i]);

    data[i + 1] = mlx[i].getObjectTemp() * 100;
  }

  // print data
  Serial.print("Data: ");
  for (int i = 1; i <= 5; i++) {
    Serial.print(data[i]);
    if (i != 5) {
      Serial.print(", ");
    }
  }
  Serial.println();
}

/*****************************************  Button Interrupt Handling *************************************************/
void buttonPressed() {
  unsigned long currentButtonPressTime = millis();  // Current timestamp of the button press

  // Check if the time between the current and last button press is within the double click timeframe (2 seconds)
  if (currentButtonPressTime - lastButtonPressTime < doubleClickTimeframe) {
    // Double click detected within the timeframe
    stopMeasurementButtonPressedFlag = true;  // Set the flag to indicate a double click
    lastButtonPressTime = 0;  // Reset the last button press time
  } else {
    // Single click detected, record the current button press time
    lastButtonPressTime = currentButtonPressTime;
  }
}