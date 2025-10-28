// --- Pin Aliases (change to your actual GPIOs if needed) ---
#define PIN_1   5
#define PIN_4   2
#define PIN_5   14
#define PIN_11  12
#define PIN_12  13

// How long readings must be stable before confirming a new state
const unsigned long STABLE_DELAY_MS = 100; 

String lastStableState = "unknown";
String lastPrintedState = "unknown";
unsigned long lastChangeTime = 0;

void setup() {
  Serial.begin(115200);
  Serial.println("\nStarting configuration detection...");

  // Inputs: Use INPUT if you have external pull resistors, else INPUT_PULLUP for testing
  pinMode(PIN_1, INPUT);
  pinMode(PIN_4, INPUT);
  pinMode(PIN_5, INPUT);
  pinMode(PIN_11, INPUT);
  pinMode(PIN_12, INPUT);
}

String detectConfig() {
  int v1 = digitalRead(PIN_1);
  int v4 = digitalRead(PIN_4);
  int v5 = digitalRead(PIN_5);
  int v11 = digitalRead(PIN_11);
  int v12 = digitalRead(PIN_12);

  if (v1 == HIGH && v4 == LOW && v5 == HIGH && v11 == HIGH && v12 == HIGH)
    return "controller";

  if (v1 == LOW && v4 == HIGH && v5 == HIGH && v11 == LOW && v12 == LOW)
    return "mouse";

  return "unknown";
}

void loop() {
  String current = detectConfig();

  // If reading changed, mark transition start
  if (current != lastStableState) {
    lastChangeTime = millis();
    lastStableState = current;
  }

  // If the state has remained stable long enough
  if (millis() - lastChangeTime > STABLE_DELAY_MS) {
    if (lastStableState != lastPrintedState) {
      if (lastStableState == "unknown") {
        Serial.println("transitioning...");
      } else {
        Serial.println(lastStableState);
      }
      lastPrintedState = lastStableState;
    }
  }

  delay(50); // sampling interval
}
