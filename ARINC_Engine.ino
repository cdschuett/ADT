#include <math.h>

//values used to derive engine parameters
long y_scale_l = 0;
long y_scale_r = 0;
long x_val_l = 0;
long x_val_r = 0;
double y_value = 0;
int i = 0;
float e=2.71828;

// Data word and sensor parameters
const int TRANSMITBLOCKSIZE = 6;
uint32_t transmitBlock[TRANSMITBLOCKSIZE];
int Hi_429 = 5;
int Lo_429 = 4;
int test = 7;
int power = 6;
byte end = 0xff;

//Controls
int CF_L = 11;
int CF_R = 10;
int ENG_L = 9;
int ENG_R= 8;
int cf_l_state = 0;
int cf_r_state = 0;
int eng_l_state = 0;
int eng_r_state = 0;

union ArraytoInt
{
  byte txchunks[4];
  uint32_t txword;
} n1Left_w, n1Right_w, egtLeft_w, egtRight_w, n2Left_w, n2Right_w;

//labels
byte n1Label = 0x5c; //Label 072
byte egtLabel = 0x8b; //Label 321
byte n2Label = 0x27; //Label 344

//parameters
int n1SpeedLeft = 0;
int n1SpeedRight = 0;
int egtLeft = 0;
int egtRight = 0;
int n2SpeedLeft = 0;
int n2SpeedRight = 0;


void setup() {
  // put your setup code here, to run once:
  pinMode(Hi_429, OUTPUT);
  pinMode(Lo_429, OUTPUT);
  pinMode(test, OUTPUT);
  pinMode(power, OUTPUT);

  pinMode(CF_L = 11, INPUT_PULLUP);
  pinMode(CF_R = 10, INPUT_PULLUP);
  pinMode(ENG_L = 9, INPUT_PULLUP);
  pinMode(ENG_R= 8, INPUT_PULLUP);

  digitalWrite(power, HIGH);
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

long sigmoid(long x_val)
{
  //Should return a value between zero and 80 depending on x
  float x = 0;
  x = x_val;
  y_value = (1.00 / (.012 + pow(e,(-.08 * x))));
  //Serial.println(x_val);
  //Serial.println(y_value);
  return(long(y_value));
}

long level()
{
  long engineValue = random(79, 81);
  return engineValue;
}

void buildWords(uint32_t *dataBlock, int y_l, int y_r)
{
  n1SpeedLeft = y_l;
  n1SpeedRight = y_r;
  egtLeft = y_l * 10;
  egtRight = y_r * 10;
  n2SpeedLeft = y_l;
  n2SpeedRight = y_r;

  n1SpeedLeft = (0x01) + ((n1SpeedLeft & 0x1fff) << 2);
  n1SpeedRight = (0x00) + ((n1SpeedRight & 0x1fff) << 2);
  egtLeft = (0x01) + ((egtLeft & 0x1fff) << 2);
  egtRight = (0x00) + ((egtRight & 0x1fff) << 2);

  n1Left_w.txchunks[0] = n1Label;
  n1Left_w.txchunks[1] = (byte)(n1SpeedLeft & 0xff);
  n1Left_w.txchunks[2] = (byte)((n1SpeedLeft >> 8) & 0xff);
  n1Left_w.txchunks[3] = 0x00;
  n1Right_w.txchunks[0] = n1Label;
  n1Right_w.txchunks[1] = (byte)(n1SpeedRight & 0xff);
  n1Right_w.txchunks[2] = (byte)((n1SpeedRight >> 8) & 0xff);
  n1Right_w.txchunks[3] = 0x00;
  egtLeft_w.txchunks[0] = egtLabel;
  egtLeft_w.txchunks[1] = (byte)(egtLeft & 0xff);
  egtLeft_w.txchunks[2] = (byte)((egtLeft >> 8) & 0xff);
  egtLeft_w.txchunks[3] = 0x00;
  egtRight_w.txchunks[0] = egtLabel;
  egtRight_w.txchunks[1] = (byte)(egtRight & 0xff);
  egtRight_w.txchunks[2] = (byte)((egtRight >> 8) & 0xff);
  egtRight_w.txchunks[3] = 0x00;
  n2Left_w.txchunks[0] = n2Label;
  n2Left_w.txchunks[1] = (byte)(n1SpeedLeft & 0xff);
  n2Left_w.txchunks[2] = (byte)((n1SpeedLeft >> 8) & 0xff);
  n2Left_w.txchunks[3] = 0x00;
  n2Right_w.txchunks[0] = n2Label;
  n2Right_w.txchunks[1] = (byte)(n1SpeedRight & 0xff);
  n2Right_w.txchunks[2] = (byte)((n1SpeedRight >> 8) & 0xff);
  n2Right_w.txchunks[3] = 0x00;


  dataBlock[0] = n1Left_w.txword;
  dataBlock[1] = n1Right_w.txword;
  dataBlock[2] = egtLeft_w.txword;
  dataBlock[3] = egtRight_w.txword;
  dataBlock[4] = n2Left_w.txword;
  dataBlock[5] = n2Right_w.txword;

  return;
}


void loop() {
  // Receive data to transmit over serial
  // Parity bit will be ignored on whatever is sent and recalculated
  // Sent word includes the label, SDI, Data, and SSM
  // delayMicroseconds(320); 4 bit times between words

  cf_l_state = digitalRead(CF_L);
  cf_r_state = digitalRead(CF_R);
  eng_l_state = digitalRead(ENG_L);
  eng_r_state = digitalRead(ENG_R);
  //Serial.print("ENGINE LEFT: ");
  //Serial.print(eng_l_state);
  //Serial.print(" ENGINE RIGHT: ");
  //Serial.println(eng_r_state);

  if(eng_l_state == 1)
  {
    x_val_l = 0;
  }

  if(eng_r_state == 1)
  {
    x_val_r = 0;
  }


  if(eng_l_state == 0)
  {
    x_val_l++;
  }

  if(eng_r_state == 0)
  {
    x_val_r++;
  }

  if(y_scale_l > 78)
  {
    y_scale_l = level();
  }
  else
  {
    y_scale_l = sigmoid(x_val_l);
  }

  if(y_scale_r > 78)
  {
    y_scale_r = level();
  }
  else
  {
    y_scale_r = sigmoid(x_val_r);
  }

  memset(transmitBlock, 0, TRANSMITBLOCKSIZE);
  buildWords(transmitBlock, y_scale_l, y_scale_r);
  for(i = 0; i < TRANSMITBLOCKSIZE; i++)
  {
    digitalWrite(test, HIGH);
    tx_data(transmitBlock[i]);
    digitalWrite(test, LOW);
    delayMicroseconds(320);
  }

  delay(240);
}
