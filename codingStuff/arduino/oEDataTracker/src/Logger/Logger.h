#ifndef Logger_h
#define Logger_h

#include "Arduino.h"
#include "../SD_Logger/SD_Logger.h"

class Logger
{
public:
    void initialize();
    void loop();
    void saveDataToSDCard(int *data, int id); // Using pointer here
private:
    SD_Logger *logger;
    String generateFileName();
};

#endif