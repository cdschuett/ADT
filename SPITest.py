import constants as c
import RPi.GPIO as GPIO
import spidev
import time

# SPI Configuration 
# Use BCM pi mode for compatibility
# If you switch to BOARD mode be sure to change pin numbers
GPIO.setmode(GPIO.BCM)

# PIN 27 - READY: Goes high when post initialization is complete
# PIN 22 - MRST: Rests the HI-3220 Must Asset Low for a minimum of 225 ns
# PIN 17 - RUN: Enables the transmit and receive schedulers
GPIO.setup(27, GPIO.IN)
GPIO.setup(22, GPIO.OUT)
GPIO.setup(17, GPIO.OUT)

# Configues SPI. This is configured for MODE 0 CPOL and CPHA 0
# Data sampled on rising edge and shifted out on falling edge
# This uses the default SPIN pins onthe rpi
spi = spidev.SpiDev()
spi.open(0,0)
spi.mode = 0b00
spi.max_speed_hz = 1200000

ready = False
false = False
chipSetup = False
start_countdown = False
#State machine values
waitForEnquire = False
normalText = True
mal = 0
rc = 0
keyPress = 0
keyPressAction = False

#Script state machine logic
# ready - Chip is in ready state
ready = False
false = False
chipSetup = False
start_countdown = False
keyPress = 0
check_time = time.perf_counter()

def formatResponse(data, msg):
    hex_list = list(map(hex, data))
    print(f"{msg} {hex_list}")

def enableRxRegister(self, registerNum):
    if 0 <= registerNum <= 15:
        reg = 0x20 + (registerNum & 0x0F)
        spi.xfer2([0x98,0x80,reg])
        spi.xfer2([0x88,0x82]) # Sets enable flag and lowspeed flag
        write = spi.xfer2([0x80,0x00])
        if write[1] != 0x82:
            print(f"Receiver {registerNum} Fail {write}")
            return False
        else:
            print(f"Receiver {registerNum} Active")
            return True
    else:
        return False


#Initial chip reset
GPIO.output(22, GPIO.LOW)
time.sleep(.5)
GPIO.output(22, GPIO.HIGH)
print("Reset Chip")

if GPIO.input(27):
    GPIO.output(17, GPIO.HIGH)
    print("Ready")
    #spi.xfer2([0xE0,0x20,0x00])
    spi.xfer2([0x98,0x80,0x00])
    spi.xfer2([0x88,0xC0])
    spi.xfer2([0x98,0x80,0x01])
    mcr_read = spi.xfer2([0x80,0x00,0x00])
    formatResponse(mcr_read, "Master Control Read")
    spi.xfer2([0x98,0x80,0x02])
    msr_reply = spi.xfer2([0x80,0x00,0x00])
    formatResponse(msr_reply, "Master Status Register Read")

    spi.xfer2([0x98,0x80,0x21])
    spi.xfer2([0x88,0x82]) # Sets enable flag and lowspeed flag
    #time.sleep(0.1)
    spi.xfer2([0x98,0x80,0x21])
    ch1_reply = spi.xfer2([0x80,0x00])
    formatResponse(ch1_reply, "Ch1 RX Read")

else:
    print("Not Ready")
