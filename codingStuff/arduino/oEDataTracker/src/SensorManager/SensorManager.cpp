#include "SensorManager.h"
#include "../Protocentral_MLX90632/Protocentral_MLX90632.h"
#include "TCA9548A.h"

// Your other includes and global variables here
TCA9548A mux;
const uint8_t MLX_CHANNELS[] = {1, 2, 3, 4, 6, 7};
const uint8_t amount_of_sensors = sizeof(MLX_CHANNELS);
Protocentral_MLX90632 mlx[amount_of_sensors];
int found_sensor_counter = 0;
unsigned long previousMillis = 0;
const long interval = 20;
int measurement_state = 1;

void SensorManager::setupSensors()
{
    Wire.begin();
    Wire.setClock(400000);
    // Initialize the multiplexer
    mux.begin();
    // Initialize MLX sensors...
    found_sensor_counter = 0;
    for (uint8_t i = 0; i < amount_of_sensors; i++)
    {
        initializeMLXSensor(i);
    }
    // Add your code to handle LED or other indications here
}

void SensorManager::initializeMLXSensor(int index)
{
    mux.openChannel(MLX_CHANNELS[index]);
    if (!mlx[index].begin())
    {
        // Handle the sensor not found condition here
    }
    else
    {
        found_sensor_counter++;
    }
    mux.closeChannel(MLX_CHANNELS[index]);
}

void SensorManager::loop()
{
    unsigned long currentMillis = millis();
    if (currentMillis - previousMillis >= interval)
    {
        previousMillis = currentMillis;
        if (found_sensor_counter != amount_of_sensors)
        {
            // Handle the condition where not all sensors are found
        }
        else
        {
            readSensorData();
        }
    }
}

void SensorManager::readSensorData()
{
    for (uint8_t i = 0; i < amount_of_sensors; i++)
    {
        mux.openChannel(MLX_CHANNELS[i]);
        // Replace the delay with non-blocking code if necessary
        int objectTemp = mlx[i].get_Temp() * 100;
        int sensorTemp = mlx[i].get_sensor_temp() * 100;
        mux.closeChannel(MLX_CHANNELS[i]);

        // Add code to store or process these readings
    }
    // Add your IMU code here as per your original code
}

void SensorManager::readIMUData()
{
    // Your code to read IMU data
    float accelX, accelY, accelZ;
    imu.get_acc(accelX, accelY, accelZ);

    float gyroX, gyroY, gyroZ;
    imu.get_gyro(gyroX, gyroY, gyroZ);

    float magX, magY, magZ;
    imu.get_mag(magX, magY, magZ);

    // Add code to store or process these readings
}

void SensorManager::incrementMeasurementState()
{
    measurement_state++;
}

int SensorManager::getMeasurementState()
{
    return measurement_state;
}