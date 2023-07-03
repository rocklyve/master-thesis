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

bool isDebugMode = false;

/*****************************************  setup() *************************************************/
void setup() {
  Serial.begin(9600);
  while (!Serial) {};

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
        readEEPROM(mlx[i]);
        // sendAddressedReset(mlx[i]);
        // sendGlobalReset(mlx[i]);
        // writeEEPROM(mlx[i]);
        readEEPROM(mlx[i]);
      }
    }
  }
}

void writeEEPROM(MLX90632 &sensor) {
  // ********************* write EE_MEAS_1 *************************************
  sensor.writeEEPROM(EE_MEAS_1_ADDR, EE_MEAS_1_32HZ_VALUE);
  delay(100);

  // ********************* write EE_MEAS_2 *************************************
  sensor.writeEEPROM(EE_MEAS_2_ADDR, EE_MEAS_2_32HZ_VALUE);
  delay(100);
}

void readEEPROM(MLX90632 &sensor) {
  uint8_t originalMode = sensor.getMode();
  sensor.setMode(MODE_SLEEP);

  sensor.enableDebugging(Serial);

  // ********************* write EE_MEAS_1 *************************************
  uint16_t valueInMemory; //Create a container
  sensor.readRegister16(EE_MEAS_1_ADDR, valueInMemory);
  Serial.print("Value stored in EE_MEAS_1_ADDR: 0x");
  Serial.println(valueInMemory, HEX);
  delay(100);

  // ********************* write EE_MEAS_2 *************************************
  uint16_t valueInMemory2; //Create a container
  sensor.readRegister16(EE_MEAS_2_ADDR, valueInMemory2);
  Serial.print("Value stored in EE_MEAS_2_ADDR: 0x");
  Serial.println(valueInMemory2, HEX);
  delay(100);

  sensor.setMode(originalMode);
}

void sendGlobalReset(MLX90632 &sensor) {
  uint8_t originalMode = sensor.getMode();
  sensor.setMode(MODE_SLEEP);

  sendAddressedSignal(0x00, 0x00);
  sendAddressedSignal(0x00, 0x06);
  Serial.println("Addressed reset send successfully");
  
  sensor.setMode(originalMode);
}

void sendAddressedReset(MLX90632 &sensor) {
  uint8_t originalMode = sensor.getMode();
  sensor.setMode(MODE_SLEEP);

  sendAddressedSignal(0x3A, 0x3A);
  sendAddressedSignal(0x3A, 0x30);
  sendAddressedSignal(0x3A, 0x05);
  sendAddressedSignal(0x3A, 0x00);
  sendAddressedSignal(0x3A, 0x06);
  
  sensor.setMode(originalMode);
  Serial.println("Addressed reset send successfully");
}

void sendAddressedSignal(uint8_t address, uint8_t value) {
  Wire.beginTransmission(address);
  Wire.write(value);
  
  // Check if the device is available at the address
  uint8_t deviceStatus = Wire.requestFrom(address, (uint8_t)1);
  if (deviceStatus == 0) {
    Serial.println("Device not found at the specified address.");
    return;
  }
  
  uint8_t transmissionStatus = Wire.endTransmission();
  if (transmissionStatus != 0) {
    Serial.print("Error sending addressed signal. Status: ");
    Serial.println(transmissionStatus);
  }
}

/*****************************************  loop() *************************************************/
void loop() {
}