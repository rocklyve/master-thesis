#include "ButtonManager.h"
#include "../LEDManager/LEDManager.h"
#include "../SensorManager/SensorManager.h"
#include <Arduino.h>

volatile bool ButtonManager::stopMeasurementButtonPressedFlag = false;
unsigned long ButtonManager::lastButtonPressTime = 0;
const unsigned long ButtonManager::doubleClickTimeframe = 2000; // Timeframe for double click in milliseconds
const int ButtonManager::buttonPin = 5;                         // Button pin connected to D5

void ButtonManager::setupButtonInterrupt()
{
    pinMode(buttonPin, INPUT_PULLUP);                                             // Set button pin as input with internal pull-up resistor
    attachInterrupt(digitalPinToInterrupt(buttonPin), buttonPressedISR, FALLING); // Attach interrupt to the button pin, trigger on FALLING edge
}

void ButtonManager::loop()
{
    if (stopMeasurementButtonPressedFlag)
    {
        handleButtonPress();
    }
}

void ButtonManager::buttonPressedISR()
{
    unsigned long currentButtonPressTime = millis();
    if (stopMeasurementButtonPressedFlag == true)
    {
        return;
    }

    if (currentButtonPressTime - lastButtonPressTime < doubleClickTimeframe)
    {
        stopMeasurementButtonPressedFlag = true;
        lastButtonPressTime = 0;
    }
    else
    {
        lastButtonPressTime = currentButtonPressTime;
        SensorManager::incrementMeasurementState();
        LEDManager::changeLEDColor(false);
    }
}

bool ButtonManager::getStopMeasurementButtonPressedFlag()
{
    return stopMeasurementButtonPressedFlag;
}

void ButtonManager::handleButtonPress()
{
    // Your code to handle a double button press.
    // This will be called from the main loop when the flag stopMeasurementButtonPressedFlag is set.
    // For example, you could safely stop the logging, change the LED color, or reset the device.
    // After handling, reset the flag:
    stopMeasurementButtonPressedFlag = false;
}
