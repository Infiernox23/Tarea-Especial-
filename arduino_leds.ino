// Recibe una letra por USB y enciende el LED correspondiente.
// A = clase 1 (pin 8) | B = clase 2 (pin 9) | C = clase 3 (pin 10)

const int LED_A = 8;
const int LED_B = 9;
const int LED_C = 10;

void apagarTodos() {
  digitalWrite(LED_A, LOW);
  digitalWrite(LED_B, LOW);
  digitalWrite(LED_C, LOW);
}

void setup() {
  pinMode(LED_A, OUTPUT);
  pinMode(LED_B, OUTPUT);
  pinMode(LED_C, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
    char c = Serial.read();
    apagarTodos();
    if (c == 'A') digitalWrite(LED_A, HIGH);
    if (c == 'B') digitalWrite(LED_B, HIGH);
    if (c == 'C') digitalWrite(LED_C, HIGH);
  }
}
