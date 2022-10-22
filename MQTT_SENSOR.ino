void setup()
{
  Serial.begin(9600);
}

uint16_t value = 0;
uint8_t data[2];

void loop()
{
  if (Serial.available())
  {
    if (Serial.read())
    {
      int16_t value = analogRead(A0);
      data[0] = value >> 8 & 0xFF;
      data[1] = value & 0xFF;
      Serial.write(data, 2);
    }
  }
}
