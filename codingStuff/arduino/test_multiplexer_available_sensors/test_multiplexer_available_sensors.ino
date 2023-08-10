#include <Wire.h>
#include "TCA9548A.h"

TCA9548A mux;
const uint8_t MLX_CHANNELS[] = {0, 1, 2, 3, 4, 5, 6, 7};

void setup()
{
  Wire.begin();

  Serial.begin(9600);

  mux.begin();
  while (!Serial);            
  mux.closeAll();
}

// Now lets assume, the address is 0x70 of the multiplexer... lets search for connected sensors
void loop()
{
  for (uint8_t i = 0; i < sizeof(MLX_CHANNELS); i++) {
    mux.openChannel(MLX_CHANNELS[i]);
    delay(50);
    
    byte error, address;
    int nDevices;

    Serial.println("Scanning...");

    nDevices = 0;
    for(address = 1; address < 127; address++ ) 
    {

      Wire.beginTransmission(address);
      error = Wire.endTransmission();

      if (error == 0)
      {
        Serial.print("I2C device found at address 0x");
        if (address<16) 
          Serial.print("0");
        Serial.print(address,HEX);
        Serial.println("!");

        nDevices++;
      }

    }
    if (nDevices == 0)
      Serial.println("No I2C devices found\n");
    else
      Serial.println("done\n");

    mux.closeChannel(MLX_CHANNELS[i]);
    delay(50);
  }

  delay(5000);           // wait 5 seconds for next scan
}
