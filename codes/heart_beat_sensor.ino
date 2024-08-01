
const int hbs = 2;

int heartrate;

void setup() {
  Serial.begin(9600);
  pinMode(hbs,INPUT);
 }

void loop() {
  get_HB_data();
  delay(500);
}

void get_HB_data()
{
int cnt=0;
double tempv=millis();
   while(millis()<(tempv+7000))
   {
     if((digitalRead(hbs)) == LOW)
     {
     cnt++; 
     delay(400);
     }
   }
cnt=cnt*7;
heartrate=cnt;
cnt=0;
Serial.write(heartrate/100+48);
Serial.write((heartrate/10)%10+48);
Serial.write((heartrate/1)%10+48);
Serial.println();
}
