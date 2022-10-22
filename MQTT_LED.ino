#define led_pin 6
int s;
void setup() {
  Serial.begin(9600);
//  Serial.println("WORK");
  pinMode(led_pin, OUTPUT);

}

void loop() {
  while (Serial.available()){
    s = Serial.read();
  }
  if( s == '1'){
    digitalWrite(led_pin, HIGH);
  }
  else if(s == '0'){
    digitalWrite(led_pin, LOW);
  }
}