#include <math.h>

// Data word and sensor parameters
const int TRANSMITBLOCKSIZE = 2;
uint32_t transmitBlock[TRANSMITBLOCKSIZE];
int Hi_429 = 5;
int Lo_429 = 4;
int test = 7;
int power = 6;
byte end = 0xff;

//Controls
int ENG_L = 3;
int ENG_R = 2;
int L_THRUST = 8;
int R_THRUST = 9;
int L_THRUST_VAL = A4;
int R_THRUST_VAL = A5;
int eng_l_state = 0;
int eng_r_state = 0;

union ArraytoInt
{
  byte txchunks[4];
  uint32_t txword;
} n1Left_w, n1Right_w;

//labels
byte n1Label = 0x5c; //Label 072
byte egtLabel = 0x8b; //Label 321
byte n2Label = 0x27; //Label 344
byte fuelLabel = 0xb5; //Label 255
byte oilPLabel = 0xf3; //Label 317

//parameters
int l_rawSpeed = 0;
int r_rawSpeed = 0;
int l_scaleSpeed = 0;
int r_scaleSpeed = 0;
int n1SpeedLeft = 0;
int n1SpeedRight = 0;


void setup() {
  // put your setup code here, to run once:
  pinMode(Hi_429, OUTPUT);
  pinMode(Lo_429, OUTPUT);
  pinMode(test, OUTPUT);
  pinMode(power, OUTPUT);
  pinMode(L_THRUST, OUTPUT);
  pinMode(R_THRUST, OUTPUT);

  pinMode(ENG_L, INPUT_PULLUP);
  pinMode(ENG_R, INPUT_PULLUP);

  digitalWrite(power, HIGH);
  digitalWrite(L_THRUST, HIGH);
  digitalWrite(R_THRUST, HIGH);

  Serial.begin(115200);
}

void tx_bit(char value)
{
  switch (value)
  {
    case 'H' : {digitalWrite(Hi_429, HIGH);digitalWrite(Lo_429, LOW);};break; // Hi
    case 'L' : {digitalWrite(Hi_429, LOW);digitalWrite(Lo_429, HIGH);};break; // Low
    case 'S' : {digitalWrite(Hi_429, LOW);digitalWrite(Lo_429, LOW);};break; // Space
    default : {digitalWrite(Hi_429, LOW);digitalWrite(Lo_429, LOW);};break; // Trash collector gives Space
  }
}

void tx_data(uint32_t dataword)
{
  uint32_t txw = dataword;
  int odd_counter=0; // odd counter calculate parity
  for (int tx=1;tx<32;tx++)
  {
    if ((txw%2)!=0) // tx bit high?
    {
      txw=txw/2; // push word to next bit
      odd_counter++; // count odd one up
      tx_bit('H');
    }
    else
    {
      txw=txw/2; // push word to next bit
      tx_bit('L');
    }
    delayMicroseconds(24);
    tx_bit('S');
    delayMicroseconds(40);
  }
  if (odd_counter%2==0)
  {
    tx_bit('H');
  }
  else
  {
    tx_bit('L');
  }
  delayMicroseconds(24);
  tx_bit('S');
}


void buildDemoWords(uint32_t *dataBlock, int y_l, int y_r)
{
  n1SpeedLeft = y_l;
  n1SpeedRight = y_r;

  n1SpeedLeft = (0x01) + ((n1SpeedLeft & 0x1fff) << 2);
  n1SpeedRight = (0x00) + ((n1SpeedRight & 0x1fff) << 2);

  n1Left_w.txchunks[0] = n1Label;
  n1Left_w.txchunks[1] = (byte)(n1SpeedLeft & 0xff);
  n1Left_w.txchunks[2] = (byte)((n1SpeedLeft >> 8) & 0xff);
  n1Left_w.txchunks[3] = 0x00;
  n1Right_w.txchunks[0] = n1Label;
  n1Right_w.txchunks[1] = (byte)(n1SpeedRight & 0xff);
  n1Right_w.txchunks[2] = (byte)((n1SpeedRight >> 8) & 0xff);
  n1Right_w.txchunks[3] = 0x00;

  dataBlock[0] = n1Left_w.txword;
  dataBlock[1] = n1Right_w.txword;
  
  return;
}


void loop() {
  // Receive data to transmit over serial
  // Parity bit will be ignored on whatever is sent and recalculated
  // Sent word includes the label, SDI, Data, and SSM
  // delayMicroseconds(320); 4 bit times between words

  eng_l_state = digitalRead(ENG_L);
  eng_r_state = digitalRead(ENG_R);
  Serial.print("ENGINE LEFT: ");
  Serial.print(eng_l_state);
  Serial.print(" ENGINE RIGHT: ");
  Serial.println(eng_r_state);

  if (eng_l_state == 0){
    l_rawSpeed = analogRead(L_THRUST_VAL);
    l_scaleSpeed = map(l_rawSpeed, 0, 1024, 100, 0);
    Serial.print("LEFT THRUST: ");
    Serial.println(l_scaleSpeed);
  }
  else{
    l_scaleSpeed = 0;
    Serial.print("LEFT THRUST: ");
    Serial.println(l_scaleSpeed);
  }

  if (eng_r_state == 0){
    r_rawSpeed = analogRead(R_THRUST_VAL);
    r_scaleSpeed = map(r_rawSpeed, 0, 1024, 100, 0);
    Serial.print("RIGHT THRUST: ");
    Serial.println(r_scaleSpeed);
  }
  else{
    r_scaleSpeed = 0;
    Serial.print("RIGHT THRUST: ");
    Serial.println(r_scaleSpeed);
  }


  memset(transmitBlock, 0, TRANSMITBLOCKSIZE);
  buildDemoWords(transmitBlock, l_scaleSpeed, r_scaleSpeed);
  for(int i = 0; i < TRANSMITBLOCKSIZE; i++)
  {
    digitalWrite(test, HIGH);
    tx_data(transmitBlock[i]);
    digitalWrite(test, LOW);
    delayMicroseconds(280);
  }

  delay(220);
}
