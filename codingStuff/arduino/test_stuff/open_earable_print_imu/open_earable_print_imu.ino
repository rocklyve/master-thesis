#include <Wire.h>
#include "IMU_Sensor.h"

IMU_Sensor imu;

void setup() {
  Serial.begin(9600);
  Wire.begin();
  imu.start();
}

void loop() {
  // Get accelerometer data
  float accelX, accelY, accelZ;
  imu.get_acc(accelX, accelY, accelZ);

  // Get gyroscope data
  float gyroX, gyroY, gyroZ;
  imu.get_gyro(gyroX, gyroY, gyroZ);

  // Get magnetometer data
  float magX, magY, magZ;
  imu.get_mag(magX, magY, magZ);

  // Print the IMU data
  Serial.print("Accelerometer: ");
  Serial.print("X = ");
  Serial.print(accelX);
  Serial.print(", Y = ");
  Serial.print(accelY);
  Serial.print(", Z = ");
  Serial.println(accelZ);

  Serial.print("Gyroscope: ");
  Serial.print("X = ");
  Serial.print(gyroX);
  Serial.print(", Y = ");
  Serial.print(gyroY);
  Serial.print(", Z = ");
  Serial.println(gyroZ);

  Serial.print("Magnetometer: ");
  Serial.print("X = ");
  Serial.print(magX);
  Serial.print(", Y = ");
  Serial.print(magY);
  Serial.print(", Z = ");
  Serial.println(magZ);

  Serial.println();

  delay(1000);  // Delay for 1 second
}