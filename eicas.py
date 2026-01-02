import constants as c
import pygame, sys
from pygame.locals import *
import pygame.gfxdraw
from Graphics import GFXDrawCircleSprite
import spidev
import RPi.GPIO as GPIO
import time
import sys

pygame.init()
pygame.font.init()

font = pygame.font.SysFont('Arial', 30)

FramePerSec = pygame.time.Clock()

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

DISPLAYSURF = pygame.display.set_mode((c.SCREEN_WIDTH, c.SCREEN_HEIGHT))
DISPLAYSURF.fill(c.BLACK)
pygame.display.set_caption("EICAS")
pygame.mouse.set_visible(True)


class ARINC():
    ready = False
    false = False
    chipSetup = False

    def __init__(self):
        #Script state machine logic
        # ready - Chip is in ready state
        self.ready = False
        self.false = False
        self.chipSetup = False

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

    def ReadDataWords(self, sensorpack):
        spi.xfer2([0x98,0x80,0x0D])
        ch0rxreg = spi.xfer2([0x80,0x00,0x00])
        threshold = ch0rxreg[1] + ch0rxreg[2]
        #self.formatResponse(ch0rxreg, "Rx 0 Threshold Value Register:")

        spi.xfer2([0x98,0x80,0x68])
        ch0rxcnt = spi.xfer2([0x80,0x00,0x00])
        datawordcnt = ch0rxcnt[1]
        #print(f"Rx 0 Threshold Value Register:{datawordcnt}")

        if datawordcnt > 0:
            sensorpack.FadecStatus = True
            for i in range(datawordcnt):
                dataword = spi.xfer2([0xC0,0x00,0x00,0x00,0x00,0x00])
                #label = oct(int('{:08b}'.format(dataword[2])[::-1], 2))
                label = oct(dataword[2])
                label = label.replace('0o','')
                #print(f"Label: {label} {dataword[3]} {dataword[4]} {dataword[5]}")

                #print(label)
                match label:
                    #Subsystem Identifier sent every one second
                    #Identifies the avionics component
                    # The ssi becomes the label that will be returned from the MCDU
                    case "72":
                        #print(f"Case 072")
                        side = int(dataword[3]) & 0x1
                        if side > 0:
                            sensorpack.n1LeftVal = (dataword[4] << 6) + ((dataword[3] & 0x1ffc) >> 2)
                        else:
                            sensorpack.n1RightVal = (dataword[4] << 6) + ((dataword[3] & 0x1ffc) >> 2)
                    case "321":
                        side = int(dataword[3]) & 0x1
                        if side > 0:
                            sensorpack.egtLeftVal = (dataword[4] << 6) + ((dataword[3] & 0x1ffc) >> 2)
                        else:
                            sensorpack.egtRightVal = (dataword[4] << 6) + ((dataword[3] & 0x1ffc) >> 2)
                    case "344":
                        side = int(dataword[3]) & 0x1
                        if side > 0:
                            print(f"Case 344 Left Side")
                            sensorpack.n2LeftVal = (dataword[4] << 6) + ((dataword[3] & 0x1ffc) >> 2)
                        else:
                            print(f"Case 344 Right Side")
                            sensorpack.n2RightVal = (dataword[4] << 6) + ((dataword[3] & 0x1ffc) >> 2)

class SensorPack():
    #self.n1LeftVal = 100.0
    #self.n1RightVal = 100.0
    #self.egtLeftVal = 0
    #self.egtRightVal = 0
    #self.n2LeftVal = 100.0
    #self.n2RightVal = 100.0

    def __init__(self):
        #Default Values
        self.tat = 22.0
        self.FadecStatus = False
        self.n1LeftVal = 100.0
        self.n1RightVal = 100.0
        self.egtLeftVal = 0
        self.egtRightVal = 0
        self.n2LeftVal = 100.0
        self.n2RightVal = 100.0
        self.FFULeftVal = 3.0
        self.FFURightVal = 3.0
        self.CenterTank = 10000
        self.LeftTank = 3000
        self.RightTank = 3000

    def readTAT(self):
        return(self.tat)

    def readFadecStatus(self):
        return(self.FadecStatus)

    def readN1Left(self):
        return(self.n1LeftVal)

    def readN1Right(self):
        return(self.n1RightVal)

    def readEgtLeft(self):
        return(self.egtLeftVal)

    def readEgtRight(self):
        return(self.egtRightVal)

    def readN2Left(self):
        return(self.n2LeftVal)

    def readN2Right(self):
        return(self.n2RightVal)

    def readFFULeft(self):
        return(self.FFULeftVal)

    def readFFURight(self):
        return(self.FFURightVal)

    def readCenterTank(self):
        self.CenterTank += 10
        if self.CenterTank > 10000:
            self.CenterTank = 1
        return(self.CenterTank)

    def readLeftTank(self):
        self.LeftTank += 10
        if self.LeftTank > 3000:
            self.LeftTank = 1
        return(self.LeftTank)

    def readRightTank(self):
        self.RightTank += 20
        if self.RightTank > 3000:
            self.RightTank = 1
        return(self.RightTank)




class TextElement:
    def __init__(self):
        self.font = pygame.font.SysFont("Arial", 20)

    def drawScreenLabels(self, screen):
        self.font = pygame.font.SysFont("Arial", 20)

        text_data = [
        {"text": "TAT", "color": c.BLUE, "pos": (260, 20)},
        {"text": "FADEC ENABLED", "color": c.BLUE, "pos": (560, 20)},
        {"text": "N1", "color": c.GREEN, "pos": (c.quarter, c.row_one+50)},
        {"text": "EGT", "color": c.GREEN, "pos": (c.quarter, c.row_two+50)},
        {"text": "N2", "color": c.GREEN, "pos": (c.quarter, c.row_three+50)},
        {"text": "FF/FU", "color": c.BLUE, "pos": (c.quarter, c.row_four+50)},
        {"text": "OIL P", "color": c.GREEN, "pos": (c.t_quarter, c.row_one+30)},
        {"text": "OIL T", "color": c.GREEN, "pos": (c.t_quarter, c.row_two+30)},
        {"text": "OIL Q%", "color": c.GREEN, "pos": (c.t_quarter, c.row_three+30)},
        {"text": "VIB", "color": c.GREEN, "pos": (c.t_quarter, c.row_four+30)},
        {"text": "HYD P", "color": c.GREEN, "pos": (c.t_quarter, (c.row_six - 40))},
        {"text": "HYD Q", "color": c.GREEN, "pos": (c.t_quarter, c.row_six)},
        {"text": "FUEL KG", "color": c.GREEN, "pos": (c.quarter, (c.hl_y_divider + 30))}
        ]
        for item in text_data:
            text_surface = self.font.render(item["text"], True, item["color"])
            text_rect = text_surface.get_rect(center=item["pos"])
            screen.blit(text_surface, text_rect)

    def drawSensorVals(self, screen, sensor):
        self.font = pygame.font.SysFont("Arial", 24)

        text_data = [
        {"text": str(round(sensor.readTAT(),1)), "color": c.WHITE, "pos": (320, 6)},
        {"text": str(round(sensor.readN1Left(),1)), "color": c.WHITE, "pos": (c.col_one + c.RADIUS1 + 8, c.row_one - c.RADIUS1)},
        {"text": str(round(sensor.readN1Right(),1)), "color": c.WHITE, "pos": (c.col_two + c.RADIUS1 + 8, c.row_one - c.RADIUS1)},
        {"text": str(sensor.readEgtLeft()), "color": c.WHITE, "pos": (c.col_one + c.RADIUS1 + 8, c.row_two - c.RADIUS1)},
        {"text": str(sensor.readEgtRight()), "color": c.WHITE, "pos": (c.col_two + c.RADIUS1 + 8, c.row_two - c.RADIUS1)},
        {"text": str(round(sensor.readN1Left(),1)), "color": c.WHITE, "pos": (c.col_one + c.RADIUS1 + 8, c.row_three - c.RADIUS1)},
        {"text": str(round(sensor.readN1Right(),1)), "color": c.WHITE, "pos": (c.col_two + c.RADIUS1 + 8, c.row_three - c.RADIUS1)},
        {"text": str(sensor.readFFULeft()), "color": c.WHITE, "pos": (c.col_one + c.RADIUS1 + 8, c.row_four - c.RADIUS1)},
        {"text": str(sensor.readFFURight()), "color": c.WHITE, "pos": (c.col_two + c.RADIUS1 + 8, c.row_four - c.RADIUS1)}
        ]

        for item in text_data:
            text_surface = self.font.render(item["text"], True, item["color"])
            text_rect = text_surface.get_rect(topright=item["pos"])
            screen.blit(text_surface, text_rect)

    def drawFuelVals(self, screen, sensor):
        WARN = c.BLACK
        WARN_TEXT = c.WHITE
        WARN_LABEL = c.BLUE

        imbalance = sensor.readRightTank() - sensor.readLeftTank()
        if abs(imbalance) > 500:
            WARN = c.RED
            WARN_TEXT = c.RED
            WARN_LABEL = c.RED

        self.font = pygame.font.SysFont("Arial", 19)

        text_data = [
        {"text": "CTR", "color": c.BLUE, "pos": (c.quarter, c.row_six - 45)},
        {"text": "L", "color": WARN_LABEL, "pos": (c.col_one, c.row_six + 15)},
        {"text": "R", "color": WARN_LABEL, "pos": (c.col_two, c.row_six + 15)},
        {"text": "IMBALANCE", "color": WARN, "pos": (c.col_one, c.row_six + 35)},
        {"text": "IMBALANCE", "color": WARN, "pos": (c.col_two, c.row_six + 35)},
        {"text": str(sensor.readCenterTank()), "color": c.WHITE, "pos": (c.quarter, c.row_six - 65)},
        {"text": str(sensor.readRightTank()), "color": WARN_TEXT, "pos": (c.col_one, c.row_six - 5)},
        {"text": str(sensor.readLeftTank()), "color": WARN_TEXT, "pos": (c.col_two, c.row_six - 5)}
        ]

        for item in text_data:
            text_surface = self.font.render(item["text"], True, item["color"])
            text_rect = text_surface.get_rect(center=item["pos"])
            screen.blit(text_surface, text_rect)


    def drawDialNums(self, screen):
        self.font = pygame.font.SysFont("Arial", 12)
        text_data = [
        {"text": "1", "color": c.WHITE, "pos": (c.col_one + c.RADIUS1 + 2, c.row_one)},
        {"text": "1", "color": c.WHITE, "pos": (c.col_two + c.RADIUS1 + 2, c.row_one)},
        {"text": "1", "color": c.WHITE, "pos": (c.col_one + c.RADIUS1 + 2, c.row_two)},
        {"text": "1", "color": c.WHITE, "pos": (c.col_two + c.RADIUS1 + 2, c.row_two)},
        {"text": "1", "color": c.WHITE, "pos": (c.col_one + c.RADIUS1 + 2, c.row_three)},
        {"text": "1", "color": c.WHITE, "pos": (c.col_two + c.RADIUS1 + 2, c.row_three)},
        {"text": "1", "color": c.WHITE, "pos": (c.col_one + c.RADIUS1 + 2, c.row_four)},
        {"text": "1", "color": c.WHITE, "pos": (c.col_two + c.RADIUS1 + 2, c.row_four)}
        ]
        for item in text_data:
            text_surface = self.font.render(item["text"], True, item["color"])
            text_rect = text_surface.get_rect(topleft=item["pos"])
            screen.blit(text_surface, text_rect)

if __name__=="__main__":
    EICAS = GFXDrawCircleSprite()
    EICASTEXT = TextElement()
    EICASSENSOR = SensorPack()
    ARINCBOARD = ARINC()

    while True:     
        for event in pygame.event.get():              
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            # Get keyboard input for movement

        DISPLAYSURF.fill(c.BLACK)

        ARINCBOARD.ReadDataWords(EICASSENSOR)
        EICAS.draw(DISPLAYSURF)
        EICASTEXT.drawScreenLabels(DISPLAYSURF)
        EICASTEXT.drawDialNums(DISPLAYSURF)
        EICASTEXT.drawSensorVals(DISPLAYSURF, EICASSENSOR)
        EICASTEXT.drawFuelVals(DISPLAYSURF, EICASSENSOR)
        EICAS.drawDials(DISPLAYSURF, EICASSENSOR)

        # Update the display
        pygame.display.flip()

        pygame.display.update()
        FramePerSec.tick(c.FPS)