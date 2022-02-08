#define POT_A A0
#define POT_B A1

int i = 0;
int k = 0;
int correction = 4;

void setup() {
  Serial.begin(9600);
  pinMode(POT_A, INPUT );
  pinMode(POT_B, INPUT );
}

void sendToRPi(int pot1, int pot2) {
  Serial.print(pot1);
  Serial.print(",");
  Serial.println(pot2);
}

void loop() {
  int a = analogRead(POT_A);
  int b = analogRead(POT_B);

  if ((a != i) && !(a > i-correction && a < i+correction)) {
    if (a == analogRead(POT_A)) {
      i = a;
      sendToRPi(a, b);
    }
    
  }
  
  else if ((a != i) && (a == 0 || a == 1023)) {
    if (a == analogRead(POT_A)) {
      i = a;
      sendToRPi(a, b);
    }
  }



  if ((b != k) && !(b > k-correction && b < k+correction)) {
    if (b == analogRead(POT_B)) {
      k = b;
      sendToRPi(a, b);
    }
  }
  else if ((b != k) && (b == 0 || b == 1023)) {
    if (b == analogRead(POT_B)) {
      k = b;
      sendToRPi(a, b);
    }
  }

  delay(10);
  
}
