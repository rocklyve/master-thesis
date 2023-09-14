#ifndef SensorManager_h
#define SensorManager_h
#include <Arduino.h>

class SensorManager
{
public:
  void setupSensors();
  void loop();
  void incrementMeasurementState();
  void getMeasurementState();

private:
  void initializeMLXSensor(int index);
  void readSensorData();
};

#endif