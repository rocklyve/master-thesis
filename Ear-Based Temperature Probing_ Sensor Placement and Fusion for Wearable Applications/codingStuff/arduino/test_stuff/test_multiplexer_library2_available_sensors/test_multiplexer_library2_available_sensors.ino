#include <Wire.h>
#include "TCA9548.h"

TCA9548 mux(0x70);
const uint8_t MLX_CHANNELS[] = {0, 1, 2, 3, 4, 5, 6, 7};

void setup()
{
  Wire.begin();

  Serial.begin(9600);

  if (mux.begin() == false) {
    Serial.println("COULD NOT CONNECT");
  }
  
  while (!Serial);
}

// Now lets assume, the address is 0x70 of the multiplexer... lets search for connected sensors
void loop() {
  mux.reset();
  delay(20);
  Serial.println();
  Serial.println();
  Serial.println();
  Serial.println();

  for (int channel = 0; channel < sizeof(MLX_CHANNELS); channel++) {
    mux.selectChannel(MLX_CHANNELS[channel]);
    bool isConnected = mux.isConnected(0x3A);
    Serial.print("CHANNEL: ");
    Serial.print(MLX_CHANNELS[channel]);
    Serial.print("\t");
    Serial.println(isConnected ? "found!" : "x");
    mux.disableChannel(channel);
  }

  delay(500);
}
