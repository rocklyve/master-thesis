int loopCounter = 0;              // Counts the number of loop iterations that meet the condition
unsigned long startTime = 0;      // Time when we start counting
const int N = 100;     
const long interval = 20;
unsigned long previousMillis = 0; // Stores last time data was sampled

void setup() {
  // initialize serial communication at 9600 bits per second:
  Serial.begin(115200);
}           // Number of iterations to count before calculating frequency

void loop() {
  unsigned long currentMillis = millis(); // Grab current time
  
  // if (currentMillis - previousMillis >= interval) {
    // Save the last time data was sampled
    previousMillis = currentMillis;

    // Your existing code here

    // Start the timer when the first sample is taken
    if (loopCounter == 0) {
      startTime = currentMillis;
    }
    
    // Update the loop counter
    loopCounter++;
    
    // Calculate frequency every N iterations
    if (loopCounter >= N) {
      unsigned long elapsedTime = currentMillis - startTime; // Time for N iterations in milliseconds
      float frequency = (float)N / (elapsedTime / 1000.0);  // Calculate frequency in Hz
      
      Serial.print("Frequency: ");
      Serial.print(frequency);
      Serial.println(" Hz");

      // Reset variables
      loopCounter = 0;
    }
  // }
}
