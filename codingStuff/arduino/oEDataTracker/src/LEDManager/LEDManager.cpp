#include "LEDManager.h"
#include "../SensorManager/SensorManager.h"

void LEDManager::changeLEDColor(bool reset)
{
    int id = SensorManager::getMeasurementState();
    int redValue = 255;
    int greenValue = 255;
    int blueValue = 255;

    // Check if id is not -1
    if (!reset)
    {
        // Determine the color based on id
        int colorSegment = id % 10;

        // Assign colors to different segments
        switch (colorSegment)
        {
        case 0:
            redValue = 0;
            break;
        case 1:
            greenValue = 0;
            break;
        case 2:
            blueValue = 0;
            break;
        case 3:
            redValue = 0;
            greenValue = 0;
            break;
        case 4:
            redValue = 0;
            blueValue = 0;
            break;
        case 5:
            greenValue = 0;
            blueValue = 0;
            break;
        case 6:
            redValue = 0;
            greenValue = 128;
            break;
        case 7:
            redValue = 128;
            greenValue = 2055;
            break;
        case 8:
            greenValue = 0;
            blueValue = 128;
            break;
        case 9:
            redValue = 128;
            blueValue = 0;
            break;
        default:
            break;
        }
    }

    analogWrite(LED_R_PIN, redValue);   // GPIO 16 (A7)
    analogWrite(LED_G_PIN, greenValue); // GPIO 17 (A6)
    analogWrite(LED_B_PIN, blueValue);  // GPIO 25 (A0)
}