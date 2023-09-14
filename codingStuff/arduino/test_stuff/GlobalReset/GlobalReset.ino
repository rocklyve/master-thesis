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
        
        readMemoryMap(mlx[i]);
        
        // sendAddressedReset(mlx[i]);
        // sendGlobalReset(mlx[i]);
        
        // readMemoryMap(mlx[i]);
        // writeEEPROM(mlx[i]);
        
        readEEPROM(mlx[i]);
      }
    }
  }
}

void readMemoryMap(MLX90632 &sensor) {
  Serial.println();
  Serial.println(readValueFromRegister(sensor, EE_Ha, "EE_Ha"));
  Serial.println(readValueFromRegister(sensor, EE_Hb, "EE_Hb"));
  Serial.println(readValueFromRegister(sensor, EE_CONTROL, "EE_CONTROL"));
  Serial.println(readValueFromRegister(sensor, EE_I2C_ADDRESS, "EE_I2C_ADDRESS"));
  Serial.println(readValueFromRegister(sensor, EE_MEAS_1_ADDR, "EE_MEAS_1"));
  Serial.println(readValueFromRegister(sensor, EE_MEAS_2_ADDR, "EE_MEAS_2"));
  Serial.println(readValueFromRegister(sensor, REG_I2C_ADDRESS, "REG_I2C_ADDRESS"));
  Serial.println(readValueFromRegister(sensor, REG_STATUS, "REG_STATUS"));
  Serial.println(readValueFromRegister(sensor, REG_CONTROL, "REG_CONTROL"));
  Serial.println();
}

void writeEEPROM(MLX90632 &sensor) {
  // ********************* write EE_MEAS_1 *************************************
  sensor.writeEEPROM(EE_MEAS_1_ADDR, EE_MEAS_1_32HZ_VALUE);
  delay(1000);

  // ********************* write EE_MEAS_2 *************************************
  sensor.writeEEPROM(EE_MEAS_2_ADDR, EE_MEAS_2_32HZ_VALUE);
  delay(1000);
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

String readValueFromRegister(MLX90632 &sensor, uint16_t address, String name) {
  uint16_t valueInMemory;
  sensor.readRegister16(address, valueInMemory);
  String result = "address 0x" + String(address, HEX) + ": 0x" + String(valueInMemory, HEX) + ", Name: " + name;
  delay(100);

  return result;
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

  sensor.writeRegister16(0x3005, 0x0006);
  delay(200);
  // sendAddressedSignal(0x3A, 0x3A);
  // sendAddressedSignal(0x3A, 0x30);
  // sendAddressedSignal(0x3A, 0x05);
  // sendAddressedSignal(0x3A, 0x00);
  // sendAddressedSignal(0x3A, 0x06);
  
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