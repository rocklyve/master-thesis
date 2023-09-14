#ifndef LEDManager_h
#define LEDManager_h
#include <Arduino.h>

class LEDManager
{
public:
    void changeLEDColor(bool reset);

private:
    const int LED_R_PIN = A7; // GPIO 16
    const int LED_G_PIN = A6; // GPIO 17
    const int LED_B_PIN = A0; // GPIO 25
};

#endif