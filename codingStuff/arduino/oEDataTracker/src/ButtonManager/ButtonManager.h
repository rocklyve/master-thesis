#ifndef ButtonManager_h
#define ButtonManager_h

class ButtonManager
{
public:
    void setupButtonInterrupt();
    void loop();
    bool getStopMeasurementButtonPressedFlag();
    static void buttonPressedISR();
    static void handleButtonPress();

private:
    static volatile bool stopMeasurementButtonPressedFlag;
    static unsigned long lastButtonPressTime;
    static const unsigned long doubleClickTimeframe;
    static const int buttonPin;
};

#endif