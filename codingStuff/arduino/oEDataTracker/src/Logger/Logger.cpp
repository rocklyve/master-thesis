#include "Logger.h"
#include "../SensorManager/SensorManager.h"

void Logger::initialize()
{
    logger = new SD_Logger();

    String file_name = generateFileName();
    if (!logger->begin(file_name))
    {
        Serial.println("SD Logger initialization failed!");
        SensorManager::changeLEDColor(true);
        while (1)
            ; // Stop execution if SD Logger initialization fails
    }
    else
    {
        Serial.println("Logger initialized and CSV name set.");
        // TODO: Very important: INTIALIZE ALL SENSORS HERE
        // initializeIMU();
        SensorManager::setupSensors();
    }
}

String Logger::generateFileName()
{
    int randSuffix = random(1, 10001);                            // Generate a random integer between 1 and 10000
    return String("Logging") + "_" + String(randSuffix) + ".csv"; // Append suffix
}

void Logger::saveDataToSDCard(int *data, int id)
{
    unsigned int timestamp = millis();
    logger->data_callback(id, timestamp, (uint8_t *)data); // Dereferencing the pointer here
}
