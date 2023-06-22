#include <Wire.h>
#include "Protocentral_MLX90632.h"
#include "TCA9548A.h"

TCA9548A mux;
Protocentral_MLX90632 mlx[5];
const uint8_t MLX_CHANNELS[] = {0, 1, 2, 4, 5};

void setup() {
  Serial.begin(9600);

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
}

void loop() {
  // Read temperature from each sensor
  for (uint8_t i = 0; i < 5; i++) {
    mux.closeAll();
    mux.openChannel(MLX_CHANNELS[i]);
    
    float temperature = mlx[i].getObjectTemp();

    Serial.print("Sensor ");
    Serial.print(i);
    Serial.print(" Temperature: ");
    Serial.print(temperature);
    Serial.println(" °C");
  }

  // delay(1000); // Delay between temperature readings
}