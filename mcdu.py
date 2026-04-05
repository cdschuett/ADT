import constants as c
import pygame, sys
from pygame.locals import *
import pygame.gfxdraw
from Graphics import GFXDrawCircleSprite
import spidev
import RPi.GPIO as GPIO
import time
import sys

#pygame.init()
#pygame.font.init()

#font = pygame.font.SysFont('Arial', 30)

#FramePerSec = pygame.time.Clock()

#SPI Configuration 
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

#DISPLAYSURF = pygame.display.set_mode((c.SCREEN_WIDTH, c.SCREEN_HEIGHT))
DISPLAYSURF = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
DISPLAYSURF.fill(c.BLACK)
#pygame.display.set_caption("EICAS")
#pygame.mouse.set_visible(True)


class ARINC():
    ready = False
    false = False
    chipSetup = False
    start_countdown = False

    def __init__(self):
        #Script state machine logic
        # ready - Chip is in ready state
        self.ready = False
        self.false = False
        self.chipSetup = False
        self.start_countdown = False
        self.check_time = time.perf_counter()

        #Initial chip reset
        self.resetChip()

        spi.xfer2([0xE0,0x20,0x00])
        spi.xfer2([0x98,0x80,0x00])
        spi.xfer2([0x88,0xC0])
        mcr_reply = spi.xfer2([0x80,0x00])
        self.formatResponse(mcr_reply, "0xC0 Activates Tx and Rx in MCR")

        if GPIO.input(27):
            GPIO.output(17, GPIO.HIGH)
            self.ready = True
            self.run = True
        else:
            self.ready = False
            self.run = False

        if (self.chipSetup == False) and (self.ready == True) and (self.run == True):
            # Set Rx and Tx active in MCR
            reply = spi.xfer2([0x00,0xC0])
            time.sleep(.01)
            # Check 
            mcr_reply = spi.xfer2([0x04,0x00]) # Desired is 192 dec or C0 which is tx and rx active
            msr_reply = spi.xfer2([0x08,0x00]) #Desired is 48 dec or 30 hex which is ready and active
            self.formatResponse(mcr_reply, "MCR State Should be 0xC0")
            self.formatResponse(msr_reply, "MSR State Should be 0x30")

            zeroStatus = self.enableRxRegister(0)
            oneStatus = self.enableRxRegister(1)
            twoStatus = self.enableRxRegister(2)
            txOneStatus = self.enableTxRegister(1)


            for i in range(256):
                spi.xfer2([0x98,0x6A,((0x00 + i) & 0xFF)])
                spi.xfer2([0x88,0xFF])
                spi.xfer2([0x98,0x68,((0x00 + i) & 0xFF)])
                spi.xfer2([0x88,0xFF])

            if zeroStatus and oneStatus:
                print(f"Chip Setup Complete")
                self.chipSetup == True

    def resetChip(self):
        #Reset chip
        GPIO.output(22, GPIO.LOW)
        time.sleep(.5)
        GPIO.output(22, GPIO.HIGH)
        return

    def enableRxRegister(self, registerNum):
        if 0 <= registerNum <= 15:
            reg = 0x20 + (registerNum & 0x0F)
            spi.xfer2([0x98,0x80,reg])
            spi.xfer2([0x88,0x82]) # Sets enable flag and lowspeed flag
            write = spi.xfer2([0x80,0x00])
            if write != 0x82:
                return False
            else:
                return True
        else:
            return False

    def enableAllRx(self):
        for i in range(16):
            spi.xfer2([0x98,0x80,(0x20 + (i & 0x0F))])
            spi.xfer2([0x88,0x82])
            write = spi.xfer2([0x80,0x00])
            if write != 0x82:
                return False
        return True

    def formatResponse(self, data, msg):
        hex_list = list(map(hex, data))
        print(f"{msg} {hex_list}")

    def enableTxRegister(self, registerNum):
        if 0 <= registerNum <= 7:
            reg = 0x30 + (registerNum & 0x07)
            spi.xfer2([0x98,0x80,reg])
            spi.xfer2([0x88,0x02]) # Sets enable flag and lowspeed flag
            return True
        else:
            return False

    def enableAllTx(self):
        for i in range(8):
            spi.xfer2([0x98,0x80,(0x30 + (i & 0x07))])
            spi.xfer2([0x88,0x02])
            write = spi.xfer2([0x80,0x00])
            if write != 0x02:
                return False
        return True

    def Write_MAP(self, upper,lower):
        rdilut = spi.xfer2([0x98,upper,lower])

    def swap32(self, i):
        return struct.unpack("<I", struct.pack(">I", i))[0]

    def reverse(self, lst):
        new_lst = lst[::-1]
        return new_lst

    def convert(self, word):
        return(binascii.hexlify(bytearray(word)))

    def TxMCDUWords(self):
        spi.xfer2([0xA1, 0x89, 0x01, 0x01, 0x12])

    def ReadMCDUWords(self):
        #0x98 is the address for register access, 0x800D is the Rx 0 Threshold Value Register
        spi.xfer2([0x98,0x80,0x0D])
        #0x80 is the command for reading data, the next two bytes are dummy bytes to clock out the data
        ch0rxreg = spi.xfer2([0x80,0x00,0x00])
        threshold = ch0rxreg[1] + ch0rxreg[2]
        self.formatResponse(ch0rxreg, "Read MCDU Rx 2 Threshold Value Register:")

        #0x98 is the address for register access, 0x806A is the Rx 2 FIFO Count
        spi.xfer2([0x98,0x80,0x6A])
        ch0rxcnt = spi.xfer2([0x80,0x00,0x00])
        datawordcnt = ch0rxcnt[1]
        print(f"Rx 1 Threshold Value Register:{datawordcnt}")


        if datawordcnt > 0:
            self.start_countdown = False
            for i in range(datawordcnt):
                dataword = spi.xfer2([0xC0,0x20,0x00,0x00,0x00,0x00])
                #label = oct(int('{:08b}'.format(dataword[2])[::-1], 2))
                label = oct(dataword[2])
                label = label.replace('0o','')
                print(f"Label: {label} {dataword[3]} {dataword[4]} {dataword[5]}")

                print(label)
                match label:
                    #Subsystem Identifier sent every one second
                    #Identifies the avionics component
                    # The ssi becomes the label that will be returned from the MCDU
                    case "304":
                        print(f"Case 304 which is the CDU address")
                        self.TxMCDUWords()

        else:
            if self.start_countdown == False:
                #print(f"No data received.Starting Countdown")
                self.check_time = time.perf_counter()
            self.start_countdown = True

        if self.start_countdown:

            now_time = time.perf_counter()
            if ((now_time - self.check_time) >= 5):
                #sensorpack.resetData()
                print(f"Resetting Data")

if __name__=="__main__":
    ARINCBOARD = ARINC()

    while True:     
        #for event in pygame.event.get():              
        #    if event.type == QUIT:
        #        pygame.quit()
        #        sys.exit()
        #    # Get keyboard input for movement

        #DISPLAYSURF.fill(c.BLACK)

        ARINCBOARD.ReadMCDUWords()
        time.sleep(.5)

        # Update the display
        #pygame.display.flip()

        #pygame.display.update()
        #FramePerSec.tick(c.FPS)
