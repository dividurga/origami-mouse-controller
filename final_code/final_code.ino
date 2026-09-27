// DIVIJA'S CODE
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

// VIBHA'S CODE
bool mouseMode = true;   // true = Mouse Mode, false = Controller Mode

// ------- PIN DEFINITIONS --------
const int W_PIN      = 18;
const int A_PIN      = 19;
const int S_PIN      = 16;
const int D_PIN      = 17;
const int LEFT_PIN   = 23;
const int RIGHT_PIN  = 25;

// Store last states to detect button edges
int lastState[6];


// -------------------------------
void setup() {
  Serial.begin(115200);
  
  // DIVIJA'S CODE
  Serial.println("\nStarting configuration detection...");

  // Inputs: Use INPUT if you have external pull resistors, else INPUT_PULLUP for testing
  pinMode(PIN_1, INPUT);
  pinMode(PIN_4, INPUT);
  pinMode(PIN_5, INPUT);
  pinMode(PIN_11, INPUT);
  pinMode(PIN_12, INPUT);
  // VIBHA'S CODE
  // Set pins as input_pullup (active low)
  pinMode(W_PIN, INPUT_PULLUP);
  pinMode(A_PIN, INPUT_PULLUP);
  pinMode(S_PIN, INPUT_PULLUP);
  pinMode(D_PIN, INPUT_PULLUP);
  pinMode(LEFT_PIN, INPUT_PULLUP);
  pinMode(RIGHT_PIN, INPUT_PULLUP);

  // Initialize state array
  for (int i = 0; i < 6; i++) lastState[i] = HIGH;

}

String detectConfig() {
  int v1 = digitalRead(PIN_1);
  //Serial.println(v1);
  int v4 = digitalRead(PIN_4);
  //Serial.println(v4);
  int v5 = digitalRead(PIN_5);
  //Serial.print(v5);
  int v11 = digitalRead(PIN_11);
  //Serial.println(v11);
  int v12 = digitalRead(PIN_12);
  //Serial.println(v12);

  if (v1 == HIGH && v4 == LOW && v11 == HIGH && v12 == HIGH) {
    mouseMode = false;
    return "controller";
  }

  else if (v1 == LOW && v4 == LOW && v11 == LOW && v12 == LOW) {
    mouseMode = true;
    return "mouse";
  }
  else {
  return "unknown";
  }

  
  
}
// --- Helper Function ---
bool pressed(int pin, int current, int last) {
  return (last == HIGH && current == LOW);
}
// -------------------------------
void loop() {
  // DIVIJA'S CODE
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

  // VIBHA'S CODE
  int currentState[6] = {
    digitalRead(W_PIN),
    digitalRead(A_PIN),
    digitalRead(S_PIN),
    digitalRead(D_PIN),
    digitalRead(LEFT_PIN),
    digitalRead(RIGHT_PIN)
  };

  // --- Mouse Mode ---
  if (lastPrintedState == "mouse") {
    if (pressed(LEFT_PIN, currentState[4], lastState[4])) {
      Serial.println("LEFT CLICK");
    }
    if (pressed(RIGHT_PIN, currentState[5], lastState[5])) {
      Serial.println("RIGHT CLICK");
    }
  }

  // --- Controller Mode ---
else if (lastPrintedState == "controller") {
    if (pressed(W_PIN, currentState[0], lastState[0])) {
      Serial.println("W (MOVE FORWARD)");
    }
    if (pressed(A_PIN, currentState[1], lastState[1])) {
      Serial.println("A (MOVE LEFT)");
    }
    if (pressed(S_PIN, currentState[2], lastState[2])) {
      Serial.println("S (MOVE BACKWARD)");
    }
    if (pressed(D_PIN, currentState[3], lastState[3])) {
      Serial.println("D (MOVE RIGHT)");
    }
}

  // Update previous states
  for (int i = 0; i < 6; i++) {
    lastState[i] = currentState[i];
  }

  delay(50); // Debounce
}


