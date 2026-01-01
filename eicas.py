import pygame, sys
from pygame.locals import *
import pygame.gfxdraw
#import spidev
#import RPi.GPIO as GPIO
import time
import sys

pygame.init()
pygame.font.init()

font = pygame.font.SysFont('Arial', 30)
 
FPS = 24
FramePerSec = pygame.time.Clock()
 
# Predefined some colors
BLUE  = (0, 0, 255)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

#SPI Configuration 
# Use BCM pi mode for compatibility
# If you switch to BOARD mode be sure to change pin numbers
#GPIO.setmode(GPIO.BCM)

# PIN 27 - READY: Goes high when post initialization is complete
# PIN 22 - MRST: Rests the HI-3220 Must Asset Low for a minimum of 225 ns
# PIN 17 - RUN: Enables the transmit and receive schedulers
#GPIO.setup(27, GPIO.IN)
#GPIO.setup(22, GPIO.OUT)
#GPIO.setup(17, GPIO.OUT)

# Configues SPI. This is configured for MODE 0 CPOL and CPHA 0
# Data sampled on rising edge and shifted out on falling edge
# This uses the default SPIN pins onthe rpi
# = spidev.SpiDev()
#spi.open(0,0)
#spi.mode = 0b00
#spi.max_speed_hz = 1200000


# Screen dimensions
SCREEN_WIDTH = 720
SCREEN_HEIGHT = 1000
RADIUS1 = 55
RADIUS2 = 35
#Alignment Vectors
half = int(SCREEN_WIDTH/2)
quarter = int(SCREEN_WIDTH/4)
t_quarter = int(3*SCREEN_WIDTH/4)
v_y_divider = int(SCREEN_HEIGHT*0.05)
hl_x_divider = int(SCREEN_WIDTH*0.05)
hl_y_divider = int(3*SCREEN_HEIGHT/4)
hr_x_divider = int(SCREEN_WIDTH*0.55)
hr_y_divider = int(2*SCREEN_HEIGHT/3)
col_one = int(SCREEN_WIDTH/8)
col_two = int(3*SCREEN_WIDTH/8)
col_three = int(5*SCREEN_WIDTH/8)
col_four = int(7*SCREEN_WIDTH/8)
row_one = int(3*SCREEN_HEIGHT/24)
row_two = int(7*SCREEN_HEIGHT/24)
row_three = int(11*SCREEN_HEIGHT/24)
row_four = int(15*SCREEN_HEIGHT/24)
row_five = int(19*SCREEN_HEIGHT/24)
row_six = int(22*SCREEN_HEIGHT/24)

DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
DISPLAYSURF.fill(BLACK)
pygame.display.set_caption("EICAS")
pygame.mouse.set_visible(True)

'''
class ARINC():
    self.ready = False
    self.false = False
    self.chipSetup = False

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
        mcr_read = spi.xfer2([0x80,0x00])
        formatResponse(mcr_reply, "0xC0 Activates Tx and Rx in MCR")

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
            formatResponse(mcr_reply, "MCR State Should be 0xC0")
            formatResponse(msr_reply, "MSR State Should be 0x30")

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

    def resetChip():
        #Reset chip
        GPIO.output(22, GPIO.LOW)
        time.sleep(.5)
        GPIO.output(22, GPIO.HIGH)
        return

    def enableRxRegister(registerNum):
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

    def enableAllRx():
        for i in range(16):
            spi.xfer2([0x98,0x80,(0x20 + (i & 0x0F))])
            spi.xfer2([0x88,0x82])
            write = spi.xfer2([0x80,0x00])
            if write != 0x82:
                return False
        return True

    def formatResponse(data, msg):
        hex_list = list(map(hex, data))
        print(f"{msg} {hex_list}")

    def enableTxRegister(registerNum):
        if 0 <= registerNum <= 7:
            reg = 0x30 + (registerNum & 0x07)
            spi.xfer2([0x98,0x80,reg])
            spi.xfer2([0x88,0x02]) # Sets enable flag and lowspeed flag
            return True
        else:
            return False

    def enableAllTx():
        for i in range(8):
            spi.xfer2([0x98,0x80,(0x30 + (i & 0x07))])
            spi.xfer2([0x88,0x02])
            write = spi.xfer2([0x80,0x00])
            if write != 0x02:
                return False
        return True

    def Write_MAP(upper,lower):
        rdilut = spi.xfer2([0x98,upper,lower])

    def swap32(i):
        return struct.unpack("<I", struct.pack(">I", i))[0]

    def reverse(lst):
        new_lst = lst[::-1]
        return new_lst

    def convert(word):
        return(binascii.hexlify(bytearray(word)))

    def ReadDataWords(self, sensorpack):
        spi.xfer2([0x98,0x80,0x0D])
        ch0rxreg = spi.xfer2([0x80,0x00,0x00])
        threshold = ch0rxreg[1] + ch0rxreg[2]
        formatResponse(ch0rxreg, "Rx 0 Threshold Value Register:")

        spi.xfer2([0x98,0x80,0x68])
        ch0rxcnt = spi.xfer2([0x80,0x00,0x00])
        datawordcnt = ch0rxcnt[1]

        if datawordcnt > 0:
            for i in range(datawordcnt):
                dataword = spi.xfer2([0xC0,0x00,0x00,0x00,0x00,0x00])
                label = oct(int('{:08b}'.format(dataword[2])[::-1], 2))
                label = label.replace('0o','')

                #print(label)
                match label:
                    #Subsystem Identifier sent every one second
                    #Identifies the avionics component
                    # The ssi becomes the label that will be returned from the MCDU
                    case "072":
                        side = int(dataword[3]) & 0x20
                        if side > 0:
                            sensorpack.n1LeftVal = ((dataword[3] & 0x1f) << 8) + dataword[4]
                        else:
                            sensorpack.n1RightVal = ((dataword[3] & 0x1f) << 8) + dataword[4]
                    case "321":
                        side = int(dataword[3]) & 0x20
                        if side > 0:
                            sensorpack.egtLeftVal = ((dataword[3] & 0x1f) << 8) + dataword[4]
                        else:
                            sensorpack.egtRightVal = ((dataword[3] & 0x1f) << 8) + dataword[4]
'''

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
        self.FadecStatus = True
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
        self.n2LeftVal += 1
        if self.n2LeftVal > 100:
            self.n2LeftVal = 1
        return(self.n2LeftVal)

    def readN2Right(self):
        self.n2RightVal += 1
        if self.n2RightVal > 100:
            self.n2RightVal = 1
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


class GFXDrawCircleSprite():
    def __init__(self):
        pass

    def dialScale(self, x, orgmin, orgmax, newmin, newmax):
        scaled_x = ((x - orgmin) / (orgmax - orgmin)) * (newmax - newmin) + newmin
        return(scaled_x)

    def eicasComponents(self, screen):
        super().__init__() 

        # Draw Vertical Divider
        pygame.gfxdraw.box(screen, (half, v_y_divider, 3, 750), GREEN)

        # Draw Left Horizontal Divider
        pygame.gfxdraw.box(screen, (hl_x_divider, hl_y_divider, 290, 3), GREEN)

        # Draw Right Horizontal Divider
        pygame.gfxdraw.box(screen, (hr_x_divider, hr_y_divider, 290, 3), GREEN)

        #FADEC Indicator
        pygame.gfxdraw.filled_polygon(screen, [(650,10), (670,10), (670,30), (650,30)], RED)

        # Engine Data
        # Draw N1 Engine 1
        pygame.gfxdraw.arc(screen, col_one, row_one, RADIUS1, 0, 245, WHITE)
        pygame.gfxdraw.rectangle(screen, ((col_one + 10), (row_one - RADIUS1 - 5), 60, 40), WHITE)
        pygame.gfxdraw.hline(screen, (col_one + RADIUS1), (col_one + RADIUS1 + 5), row_one, WHITE)
        pygame.gfxdraw.line(screen, col_one - 24, row_one - 50, col_one - 28, row_one - 60, RED)
        pygame.gfxdraw.line(screen, col_one - 31, row_one - 45, col_one - 36, row_one - 55, YELLOW)


        # Draw N1 Engine 2
        pygame.gfxdraw.arc(screen, col_two, row_one, RADIUS1, 0, 245, WHITE)
        pygame.gfxdraw.rectangle(screen, ((col_two + 10), (row_one - RADIUS1 - 5), 60, 40), WHITE)
        pygame.gfxdraw.hline(screen, (col_two + RADIUS1), (col_two + RADIUS1 + 5), row_one, WHITE)
        pygame.gfxdraw.line(screen, col_two - 24, row_one - 50, col_two - 28, row_one - 60, RED)
        pygame.gfxdraw.line(screen, col_two - 31, row_one - 45, col_two - 36, row_one - 55, YELLOW)


        # Draw EGT Engine 1
        pygame.gfxdraw.arc(screen, col_one, row_two, 55, 0, 245, WHITE)
        pygame.gfxdraw.rectangle(screen, ((col_one + 10), (row_two - RADIUS1 - 5), 60, 40), WHITE)
        pygame.gfxdraw.hline(screen, (col_one + RADIUS1), (col_one + RADIUS1 + 5), row_two, WHITE)
        pygame.gfxdraw.line(screen, col_one - 24, row_two - 50, col_one - 28, row_two - 60, RED)
        pygame.gfxdraw.line(screen, col_one - 31, row_two - 45, col_one - 36, row_two - 55, YELLOW)

        # Draw EGT Engine 2
        pygame.gfxdraw.arc(screen, col_two, row_two, 55, 0, 245, WHITE)
        pygame.gfxdraw.rectangle(screen, ((col_two + 10), (row_two - RADIUS1 - 5), 60, 40), WHITE)
        pygame.gfxdraw.hline(screen, (col_two + RADIUS1), (col_two + RADIUS1 + 5), row_two, WHITE)
        pygame.gfxdraw.line(screen, col_two - 24, row_two - 50, col_two - 28, row_two - 60, RED)
        pygame.gfxdraw.line(screen, col_two - 31, row_two - 45, col_two - 36, row_two - 55, YELLOW)

        # Draw N2 Engine 1
        pygame.gfxdraw.arc(screen, col_one, row_three, 55, 0, 245, WHITE)
        pygame.gfxdraw.rectangle(screen, ((col_one + 10), (row_three - RADIUS1 - 5), 60, 40), WHITE)
        pygame.gfxdraw.hline(screen, (col_one + RADIUS1), (col_one + RADIUS1 + 5), row_three, WHITE)
        pygame.gfxdraw.line(screen, col_one - 24, row_three - 50, col_one - 28, row_three - 60, RED)
        pygame.gfxdraw.line(screen, col_one - 31, row_three - 45, col_one - 36, row_three - 55, YELLOW)

        # Draw N2 Engine 2
        pygame.gfxdraw.arc(screen, col_two, row_three, 55, 0, 245, WHITE)
        pygame.gfxdraw.rectangle(screen, ((col_two + 10), (row_three - RADIUS1 - 5), 60, 40), WHITE)
        pygame.gfxdraw.hline(screen, (col_two + RADIUS1), (col_two + RADIUS1 + 5), row_three, WHITE)
        pygame.gfxdraw.line(screen, col_two - 24, row_three - 50, col_two - 28, row_three - 60, RED)
        pygame.gfxdraw.line(screen, col_two - 31, row_three - 45, col_two - 36, row_three - 55, YELLOW)

        # Draw FF/FU Engine 1
        pygame.gfxdraw.arc(screen, col_one, row_four, 55, 0, 245, WHITE)
        pygame.gfxdraw.rectangle(screen, ((col_one + 10), (row_four - RADIUS1 - 5), 60, 40), WHITE)
        pygame.gfxdraw.hline(screen, (col_one + RADIUS1), (col_one + RADIUS1 + 5), row_four, WHITE)
        pygame.gfxdraw.line(screen, col_one - 24, row_four - 50, col_one - 28, row_four - 60, RED)

        # Draw FF/FU Engine 2
        pygame.gfxdraw.arc(screen, col_two, row_four, 55, 0, 245, WHITE)
        pygame.gfxdraw.rectangle(screen, ((col_two + 10), (row_four - RADIUS1 - 5), 60, 40), WHITE)
        pygame.gfxdraw.hline(screen, (col_two + RADIUS1), (col_two + RADIUS1 + 5), row_four, WHITE)
        pygame.gfxdraw.line(screen, col_two - 24, row_four - 50, col_two - 28, row_four - 60, RED)

        # Oil and Vibration
        # Oil Pressure Left
        pygame.gfxdraw.arc(screen, col_three, row_one, RADIUS2, 40, 320, WHITE)
        pygame.gfxdraw.pie(screen, col_three, row_one, RADIUS2+10, 40, 40, WHITE)
        pygame.gfxdraw.pie(screen, col_three, row_one, RADIUS2+10, 320, 320, WHITE)
        pygame.gfxdraw.filled_trigon(screen, col_three, row_one, col_three+25, row_one+24, col_three+25, row_one-24, BLACK)

        # Oil Pressure Right
        pygame.gfxdraw.arc(screen, col_four, row_one, RADIUS2, 40, 320, WHITE)
        pygame.gfxdraw.pie(screen, col_four, row_one, RADIUS2+10, 40, 40, WHITE)
        pygame.gfxdraw.pie(screen, col_four, row_one, RADIUS2+10, 320, 320, WHITE)
        pygame.gfxdraw.filled_trigon(screen, col_four, row_one, col_four+25, row_one+24, col_four+25, row_one-24, BLACK)

        # Oil Temp Left
        pygame.gfxdraw.arc(screen, col_three, row_two, RADIUS2, 40, 320, WHITE)

        # Oil Temp Right
        pygame.gfxdraw.arc(screen, col_four, row_two, RADIUS2, 40, 320, WHITE)

        # Oil Quantity Left
        pygame.gfxdraw.rectangle(screen, (col_three - RADIUS2, row_three - RADIUS2, 60, 40), WHITE)

        # Oil Quantity Right
        pygame.gfxdraw.rectangle(screen, (col_four - RADIUS2, row_three - RADIUS2, 60, 40), WHITE)

        # Vibration Left
        pygame.gfxdraw.arc(screen, col_three, row_four - 25, 35, 110, 370, WHITE)

        # Vibration Right
        pygame.gfxdraw.arc(screen, col_four, row_four - 25, 35, 110, 370, WHITE)

        # Hydraulic Pressure and Quantity
        # Hyd Press Left
        pygame.gfxdraw.arc(screen, col_three, row_six, RADIUS1, 40, 320, WHITE)

        # Hyd Press Right
        pygame.gfxdraw.arc(screen, col_four, row_six, RADIUS1, 40, 320, WHITE)

        # Hyd Quantity Left
        pygame.gfxdraw.rectangle(screen, (col_three, row_six, 60, 40), WHITE)

        # Hyd Quantity Right
        pygame.gfxdraw.rectangle(screen, (col_four, row_six, 60, 40), WHITE)

        # Fuel Quantity and Balance
        # Fuel Left
        pygame.gfxdraw.arc(screen, col_one, row_six, RADIUS2, 140, 395, WHITE)
        pygame.gfxdraw.pie(screen, col_one, row_six, RADIUS2+10, 140, 395, WHITE)

        # Fuel Center
        pygame.gfxdraw.arc(screen, quarter, (row_six - 60), RADIUS2+10, 140, 395, WHITE)
        pygame.gfxdraw.pie(screen, quarter, (row_six - 60), RADIUS2+20, 140, 395, WHITE)

        # Fuel Right
        pygame.gfxdraw.arc(screen, col_two, row_six, RADIUS2, 140, 395, WHITE)
        pygame.gfxdraw.pie(screen, col_two, row_six, RADIUS2+10, 140, 395, WHITE)


    def draw(self, screen):
        self.eicasComponents(screen)

    def drawDials(self, screen, sensors):
        super().__init__() 

        # Fadec Status
        if sensors.readFadecStatus():
            pygame.gfxdraw.filled_polygon(screen, [(650,10), (670,10), (670,30), (650,30)], GREEN)

        # Engine Data
        # Draw N1 Engine 1
        dial = round(self.dialScale(sensors.readN1Left(), 0, 100, 0, 245))
        pygame.gfxdraw.pie(screen, col_one, row_one, RADIUS1, dial, dial, WHITE) # 0-245

        # Draw N1 Engine 2
        dial = round(self.dialScale(sensors.readN1Right(), 0, 100, 0, 245))
        pygame.gfxdraw.pie(screen, col_two, row_one, RADIUS1, dial, dial, WHITE) #0-245

        # Draw EGT Engine 1
        dial = round(self.dialScale(sensors.readEgtLeft(), 0, 1000, 0, 245))
        pygame.gfxdraw.pie(screen, col_one, row_two, RADIUS1, dial, dial, WHITE)

        # Draw EGT Engine 2
        dial = round(self.dialScale(sensors.readEgtRight(), 0, 1000, 0, 245))
        pygame.gfxdraw.pie(screen, col_two, row_two, RADIUS1, dial, dial, WHITE)

        # Draw N2 Engine 1
        dial = round(self.dialScale(sensors.readN2Left(), 0, 100, 0, 245))
        pygame.gfxdraw.pie(screen, col_one, row_three, RADIUS1, dial, dial, WHITE)

        # Draw N2 Engine 2
        dial = round(self.dialScale(sensors.readN2Right(), 0, 100, 0, 245))
        pygame.gfxdraw.pie(screen, col_two, row_three, RADIUS1, dial, dial, WHITE)

        # Draw FF/FU Engine 1
        dial = round(self.dialScale(sensors.readFFULeft(), 0, 6, 0, 245))
        pygame.gfxdraw.pie(screen, col_one, row_four, RADIUS1, dial, dial, WHITE)


        # Draw FF/FU Engine 2
        dial = round(self.dialScale(sensors.readFFURight(), 0, 6, 0, 245))
        pygame.gfxdraw.pie(screen, col_two, row_four, RADIUS1, dial, dial, WHITE)

        # Oil and Vibration
        # Oil Pressure Left
        dial = round(self.dialScale(sensors.readN2Left(), 0, 100, 40, 320))
        pygame.gfxdraw.pie(screen, col_three, row_one, RADIUS2, dial, dial, WHITE)


        # Oil Pressure Right
        pygame.gfxdraw.arc(screen, col_four, row_one, 35, 40, 320, WHITE)

        # Oil Temp Left
        pygame.gfxdraw.arc(screen, col_three, row_two, 35, 40, 320, WHITE)

        # Oil Temp Right
        pygame.gfxdraw.arc(screen, col_four, row_two, 35, 40, 320, WHITE)

        # Vibration Left
        dial = round(self.dialScale(sensors.readN2Left(), 0, 100, 110, 370))
        pygame.gfxdraw.pie(screen, col_three, row_four - 25, RADIUS2, dial, dial, WHITE)

        # Vibration Right
        dial = round(self.dialScale(sensors.readN2Left(), 0, 100, 110, 370))
        pygame.gfxdraw.pie(screen, col_four, row_four - 25, RADIUS2, dial, dial, WHITE)

        # Hydraulic Pressure and Quantity
        # Hyd Press Left
        pygame.gfxdraw.arc(screen, col_three, row_five, 55, 40, 320, WHITE)

        # Hyd Press Right
        pygame.gfxdraw.arc(screen, col_four, row_five, 55, 40, 320, WHITE)


        # Fuel Quantity and Balance
        # Fuel Left
        dial = round(self.dialScale(sensors.readLeftTank(), 0, 3000, 140, 395))
        pygame.gfxdraw.pie(screen, col_one, row_six, RADIUS2+10, dial, dial, WHITE)

        # Fuel Center
        dial = round(self.dialScale(sensors.readCenterTank(), 0, 10000, 140, 395))
        pygame.gfxdraw.pie(screen, quarter, (row_six - 60), RADIUS2+20, dial, dial, WHITE)

        # Fuel Right
        dial = round(self.dialScale(sensors.readRightTank(), 0, 3000, 140, 395))
        pygame.gfxdraw.pie(screen, col_two, row_six, RADIUS2+10, dial, dial, WHITE)


class TextElement:
    def __init__(self):
        self.font = pygame.font.SysFont("Arial", 20)

    def drawScreenLabels(self, screen):
        self.font = pygame.font.SysFont("Arial", 20)

        text_data = [
        {"text": "TAT", "color": BLUE, "pos": (260, 20)},
        {"text": "FADEC ENABLED", "color": BLUE, "pos": (560, 20)},
        {"text": "N1", "color": GREEN, "pos": (quarter, row_one+50)},
        {"text": "EGT", "color": GREEN, "pos": (quarter, row_two+50)},
        {"text": "N2", "color": GREEN, "pos": (quarter, row_three+50)},
        {"text": "FF/FU", "color": BLUE, "pos": (quarter, row_four+50)},
        {"text": "OIL P", "color": GREEN, "pos": (t_quarter, row_one+30)},
        {"text": "OIL T", "color": GREEN, "pos": (t_quarter, row_two+30)},
        {"text": "OIL Q%", "color": GREEN, "pos": (t_quarter, row_three+30)},
        {"text": "VIB", "color": GREEN, "pos": (t_quarter, row_four+30)},
        {"text": "HYD P", "color": GREEN, "pos": (t_quarter, (row_six - 40))},
        {"text": "HYD Q", "color": GREEN, "pos": (t_quarter, row_six)},
        {"text": "FUEL KG", "color": GREEN, "pos": (quarter, (hl_y_divider + 30))}
        ]
        for item in text_data:
            text_surface = self.font.render(item["text"], True, item["color"])
            text_rect = text_surface.get_rect(center=item["pos"])
            screen.blit(text_surface, text_rect)

    def drawSensorVals(self, screen, sensor):
        self.font = pygame.font.SysFont("Arial", 24)

        text_data = [
        {"text": str(round(sensor.readTAT(),1)), "color": WHITE, "pos": (320, 6)},
        {"text": str(round(sensor.readN1Left(),1)), "color": WHITE, "pos": (col_one + RADIUS1 + 8, row_one - RADIUS1)},
        {"text": str(round(sensor.readN1Right(),1)), "color": WHITE, "pos": (col_two + RADIUS1 + 8, row_one - RADIUS1)},
        {"text": str(sensor.readEgtLeft()), "color": WHITE, "pos": (col_one + RADIUS1 + 8, row_two - RADIUS1)},
        {"text": str(sensor.readEgtRight()), "color": WHITE, "pos": (col_two + RADIUS1 + 8, row_two - RADIUS1)},
        {"text": str(round(sensor.readN1Left(),1)), "color": WHITE, "pos": (col_one + RADIUS1 + 8, row_three - RADIUS1)},
        {"text": str(round(sensor.readN1Right(),1)), "color": WHITE, "pos": (col_two + RADIUS1 + 8, row_three - RADIUS1)},
        {"text": str(sensor.readFFULeft()), "color": WHITE, "pos": (col_one + RADIUS1 + 8, row_four - RADIUS1)},
        {"text": str(sensor.readFFURight()), "color": WHITE, "pos": (col_two + RADIUS1 + 8, row_four - RADIUS1)}
        ]

        for item in text_data:
            text_surface = self.font.render(item["text"], True, item["color"])
            text_rect = text_surface.get_rect(topright=item["pos"])
            screen.blit(text_surface, text_rect)

    def drawFuelVals(self, screen, sensor):
        WARN = BLACK
        WARN_TEXT = WHITE
        WARN_LABEL = BLUE

        imbalance = sensor.readRightTank() - sensor.readLeftTank()
        if abs(imbalance) > 500:
            WARN = RED
            WARN_TEXT = RED
            WARN_LABEL = RED

        self.font = pygame.font.SysFont("Arial", 19)

        text_data = [
        {"text": "CTR", "color": BLUE, "pos": (quarter, row_six - 45)},
        {"text": "L", "color": WARN_LABEL, "pos": (col_one, row_six + 15)},
        {"text": "R", "color": WARN_LABEL, "pos": (col_two, row_six + 15)},
        {"text": "IMBALANCE", "color": WARN, "pos": (col_one, row_six + 35)},
        {"text": "IMBALANCE", "color": WARN, "pos": (col_two, row_six + 35)},
        {"text": str(sensor.readCenterTank()), "color": WHITE, "pos": (quarter, row_six - 65)},
        {"text": str(sensor.readRightTank()), "color": WARN_TEXT, "pos": (col_one, row_six - 5)},
        {"text": str(sensor.readLeftTank()), "color": WARN_TEXT, "pos": (col_two, row_six - 5)}
        ]

        for item in text_data:
            text_surface = self.font.render(item["text"], True, item["color"])
            text_rect = text_surface.get_rect(center=item["pos"])
            screen.blit(text_surface, text_rect)


    def drawDialNums(self, screen):
        self.font = pygame.font.SysFont("Arial", 12)
        text_data = [
        {"text": "1", "color": WHITE, "pos": (col_one + RADIUS1 + 2, row_one)},
        {"text": "1", "color": WHITE, "pos": (col_two + RADIUS1 + 2, row_one)},
        {"text": "1", "color": WHITE, "pos": (col_one + RADIUS1 + 2, row_two)},
        {"text": "1", "color": WHITE, "pos": (col_two + RADIUS1 + 2, row_two)},
        {"text": "1", "color": WHITE, "pos": (col_one + RADIUS1 + 2, row_three)},
        {"text": "1", "color": WHITE, "pos": (col_two + RADIUS1 + 2, row_three)},
        {"text": "1", "color": WHITE, "pos": (col_one + RADIUS1 + 2, row_four)},
        {"text": "1", "color": WHITE, "pos": (col_two + RADIUS1 + 2, row_four)}
        ]
        for item in text_data:
            text_surface = self.font.render(item["text"], True, item["color"])
            text_rect = text_surface.get_rect(topleft=item["pos"])
            screen.blit(text_surface, text_rect)

if __name__=="__main__":
    EICAS = GFXDrawCircleSprite()
    EICASTEXT = TextElement()
    EICASSENSOR = SensorPack()
    #ARINCBOARD = ARINC()

    while True:     
        for event in pygame.event.get():              
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            # Get keyboard input for movement

        DISPLAYSURF.fill(BLACK)

        #ARINCBOARD.ReadDataWords(EICASSENSOR)
        EICAS.draw(DISPLAYSURF)
        EICASTEXT.drawScreenLabels(DISPLAYSURF)
        EICASTEXT.drawDialNums(DISPLAYSURF)
        EICASTEXT.drawSensorVals(DISPLAYSURF, EICASSENSOR)
        EICASTEXT.drawFuelVals(DISPLAYSURF, EICASSENSOR)
        EICAS.drawDials(DISPLAYSURF, EICASSENSOR)

        # Update the display
        pygame.display.flip()

        pygame.display.update()
        FramePerSec.tick(FPS)