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
# spi = spidev.SpiDev()
# spi.open(0,0)
# spi.mode = 0b00
# spi.max_speed_hz = 1200000

# Memory map (datasheet p. 11)
RX_DATA_BASE = 0x0000           # 4 bytes per (channel, label): status + 3 data bytes
RX_FIFO_ENABLE_MAP = 0x6800     # 32 bytes per channel, 1 bit per label
RX_INT_MAP = 0x6A00             # 32 bytes per channel, 1 bit per label
TX_FIFO_BASE = 0x6C00
RX_FIFO_BASE = 0x7000
TX_DESC_BASE = (0x4000, 0x4800, 0x5000, 0x5400, 0x5800, 0x5C00, 0x6000, 0x6400)
RAM_TOP = 0x7FFF

# SPI op-codes (datasheet Table 2, p. 44)
OP_READ_AT_MAP = 0x80
OP_WRITE_AT_MAP = 0x88
OP_READ_MAP = 0x90
OP_WRITE_MAP = 0x98
OP_TRANSMIT = 0xA0          # | TTT
OP_READ_RX_FIFO = 0xC0      # + CCCC0000
OP_READ_IV_BLOCK = 0xC8     # + CCCC0000 -> status + 3 data
OP_READ_IV_MESSAGE = 0xD0   # + CCCC0000 -> label + 3 data
OP_WRITE_REG = 0xD8         # 11011AAA AAAA0000
OP_READ_REG = 0xE0          # 1110AAAA AAAA0000
OP_SOFT_RESET = 0xFA        # + 01011mmm
OP_READ_ALL_PENDING = 0x28  # PIR, RPIRL, RPIRH (0x800A, 0x800B, 0x800C)

RX_FIFO_DEPTH = 64
TX_FIFO_DEPTH = 32
FIFO_FLUSH_KEY = 0xA5

LabelLike = int | str

class SpidevTransport:

    def __init__(self, bus: int = 0, device: int = 0, speed_hz: int = 1_200_000, mode: int = 0):
        self._spi = spidev.SpiDev()
        self._spi.open(bus, device)
        self._spi.max_speed_hz = int(speed_hz)
        self._spi.mode = mode          # HI-3223 accepts 0 or 3 but the board is hardwired for 0

    def transfer(self, data: bytes) -> bytes:
        # xfer2 keeps CS asserted for the whole list (required by the HI-3223)
        return bytes(self._spi.xfer2(list(data)))

    def close(self) -> None:
        self._spi.close()

# =============================================================================
# Register map (datasheet pp. 12-14)
# =============================================================================
class Reg(enum.IntEnum):
    MCR = 0x8000        # Master Control (write address; also R/W via direct ops)
    MCR_RD = 0x8001     # Master Control (read address)
    MSR = 0x8002        # Master Status
    PIR = 0x8004        # Pending Interrupt          (clear on read)
    RPIRL = 0x8006      # Rx Pending Interrupt 7-0   (clear on read)
    RPIRH = 0x8008      # Rx Pending Interrupt 15-8  (clear on read)
    PIR_ALT = 0x800A    # alternate addresses used by multi-byte op 0x28
    RPIRL_ALT = 0x800B
    RPIRH_ALT = 0x800C
    FTFL = 0x800D       # Rx FIFO threshold flags 7-0
    FTFH = 0x800E       # Rx FIFO threshold flags 15-8
    TFR = 0x800F        # Tx FIFO threshold flags
    IAR0 = 0x8010       # Rx Interrupt Address (label) ch0..15 -> 0x8010-0x801F
    RXC0 = 0x8020       # Rx Control ch0..15 -> 0x8020-0x802F
    TXC0 = 0x8030       # Tx Control ch0..7 -> 0x8030-0x8037
    TXRR0 = 0x8038      # Tx Repetition Rate ch0..7
    TXSP0 = 0x8040      # Tx Sequence Pointer ch0..7 (read only)
    LOOP = 0x8049       # Loop-back
    PIER = 0x804A       # Pending Interrupt Enable
    RIEL = 0x804B       # Rx Interrupt Enable 7-0
    RIEH = 0x804C       # Rx Interrupt Enable 15-8
    FIEL = 0x804D       # Rx FIFO Interrupt Enable 7-0
    FIEH = 0x804E       # Rx FIFO Interrupt Enable 15-8
    TFIE = 0x804F       # Tx FIFO Interrupt Enable
    FTV0 = 0x8050       # Rx FIFO Threshold Value ch0..15
    TFTV0 = 0x8060      # Tx FIFO Threshold Value ch0..7
    RFC0 = 0x8068       # Rx FIFO Count ch0..15 (write 0xA5 to flush)
    BISTS = 0x8078      # BIST Control / Status
    BISTFL = 0x8079     # BIST fail address low
    BISTFH = 0x807A     # BIST fail address high + MODE[2:0] in bits 7:5
    AIFL = 0x807B       # Auto-init fail address low
    AIFH = 0x807C       # Auto-init fail address high
    WCM = 0x807E        # Watchdog channel mask (1 = masked)
    WTR = 0x807F        # Watchdog timer (LSB = 20 ms)
    TFC0 = 0x8080       # Tx FIFO Count ch0..7 (read only)


class MCR(enum.IntFlag):
    A429RX = 0x80    # global receive enable
    A429TX = 0x40    # global transmit enable
    AFLIP = 0x08     # flip label bit order (Rx and Tx)
    TXMSK = 0x04     # suppress external Tx output for channels in loop-back
    TX7OPT = 0x02    # status bit 7 = NEWHOST (1) or NEWTX7 (0)
    TXDL256 = 0x01   # Tx0/Tx1 descriptor tables 256 long instead of 128


class MSR(enum.IntFlag):
    READY = 0x20
    ACTIVE = 0x10      # RUN pin asserted, normal operation
    SAFE = 0x08        # BIST / auto-init failure
    RAM_BUSY = 0x04
    PROGCY = 0x02      # EEPROM programming cycle in progress
    AUTOINIT = 0x01    # loading from auto-init EEPROM


class RXC(enum.IntFlag):
    ENABLE = 0x80
    PARITYEN = 0x20   # bit 32 replaced by parity-error flag (0 = OK / odd)
    DECODER = 0x10    # SDI filtering using SD10/SD9
    SD10 = 0x08
    SD9 = 0x04
    RATE = 0x02       # 1 = low speed (12.5 kb/s)
    K50OPT = 0x01     # 50 kb/s (overrides RATE)


class TXC(enum.IntFlag):
    RUN = 0x80        # scheduler run/stop
    PRESCALE = 0x40   # repetition-rate LSB: 0 = 10 ms, 1 = 1 ms
    PARITY = 0x20     # bit 32 = parity (1) or data (0)
    EVEN = 0x10       # 1 = even parity, 0 = odd parity
    SKIP = 0x08       # wait for repetition-rate rollover before new cycle
    TRISTATE = 0x04   # force TXP/TXN high (line driver high-Z)
    RATE = 0x02       # 1 = low speed
    K50OPT = 0x01     # 50 kb/s


class PIR(enum.IntFlag):
    EEABORTERR = 0x80
    COPYERR = 0x40
    AUTOERR = 0x20
    CHKERR = 0x10
    RAMFAIL = 0x08
    RXRAMNEW = 0x04
    RXFLAG = 0x02
    TXFLAG = 0x01


class PIER(enum.IntFlag):
    RXRAMNEWE = 0x04
    RXFLAGIE = 0x02
    TXFLAGIE = 0x01


class Speed(enum.Enum):
    HIGH = "100k"     # 100 kb/s
    K50 = "50k"       # 50 kb/s (non-standard)
    LOW = "12.5k"     # 12.5 kb/s

    @property
    def bits(self) -> int:
        """RATE / 50KOPT bits (same positions in RXC and TXC)."""
        return {Speed.HIGH: 0x00, Speed.LOW: 0x02, Speed.K50: 0x01}[self]

    @property
    def bit_rate(self) -> float:
        return {Speed.HIGH: 100_000.0, Speed.K50: 50_000.0, Speed.LOW: 12_500.0}[self]

    @property
    def word_time_s(self) -> float:
        """32 bits + 4-bit minimum inter-word gap."""
        return 36.0 / self.bit_rate

    @classmethod
    def from_bits(cls, value: int) -> "Speed":
        if value & 0x01:
            return cls.K50
        return cls.LOW if value & 0x02 else cls.HIGH


class TxOp(enum.IntEnum):
    """Transmit descriptor op-codes (datasheet p. 27)."""
    END = 0x0                 # end of sequence
    DELAY = 0x1               # delay PTP milliseconds
    IMMEDIATE = 0x2           # send descriptor bytes 5-8
    IMMEDIATE_COND = 0x3      # ...only if Rx (chan,label) has new data
    INDEXED = 0x4             # byte5 label + 24 data bits from Rx (chan,label)
    INDEXED_COND = 0x5
    INDEXED_SDI = 0x6         # as INDEXED but SDI replaced by descriptor SS bits
    INDEXED_SDI_COND = 0x7


class RamBist(enum.IntEnum):
    """RBSEL2:0 values for the BIST control register."""
    PATTERN = 0b001
    WRITE_00 = 0b010
    VERIFY_00 = 0b011
    WRITE_FF = 0b100
    VERIFY_FF = 0b101
    INC_DEC = 0b110

class ARINC():
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

    #Static Data
    functionMenu = [0x91, 0x05, 0x01, 0x02, 0x91, 0x01, 0xf3, 0x01, 0x91, 0x3c, 0x51, 0x45, 0x91, 0x44, 0x20, 0x20, 0x91, 0x00, 0x01, 0x04]
    configMenu = [0x91, 0x6e, 0x01, 0x82, 0x91, 0x01, 0xf1, 0x81, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x43, 0xcf, 0x91, 0x4e, 0x46, 0x49, 0x91, 0x47, 0x20, 0x20, 0x91, 0x20, 0x4d, 0x45, 0x91, 0x4e, 0x55, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x01, 0xf2, 0x81, 0x91, 0x54, 0x48, 0x49, 0x91, 0x53, 0x20, 0x49, 0x91, 0x53, 0x20, 0xc1, 0x91, 0x20, 0x50, 0x4c, 0x91, 0x41, 0x43, 0x45, 0x91, 0x48, 0x4f, 0x4c, 0x91, 0x44, 0x45, 0x52, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x01, 0xf3, 0x01, 0x91, 0x46, 0x4f, 0xd2, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x01, 0xf4, 0x81, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x01, 0xf5, 0x01, 0x91, 0x41, 0x20, 0x20, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x01, 0xf6, 0x01, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x01, 0xf7, 0x81, 0x91, 0x43, 0x4f, 0x4e, 0x91, 0x46, 0x49, 0x47, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x01, 0xf8, 0x81, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x01, 0xf9, 0x01, 0x91, 0x4d, 0x45, 0xce, 0x91, 0x55, 0x20, 0x20, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x01, 0xfa, 0x01, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x01, 0xfb, 0x81, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x01, 0xfc, 0x01, 0x91, 0x3c, 0x42, 0x41, 0x91, 0x43, 0x4b, 0x20, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x00, 0x01, 0x04]
    happyFaceMenu = [0x91, 0x6e, 0x01, 0x82, 0x91, 0x01, 0xf1, 0x81, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x48, 0x45, 0x91, 0x4c, 0x4c, 0xcf, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x4d, 0x45, 0x91, 0x4e, 0x55, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x01, 0xf2, 0x81, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x4d, 0xcd, 0x91, 0x4d, 0x4d, 0x4d, 0x91, 0x4d, 0x4d, 0x4d, 0x91, 0x4d, 0x20, 0x20, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x01, 0xf3, 0x01, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x4d, 0x20, 0x20, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x4d, 0x20, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x01, 0xf4, 0x81, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0x4d, 0x91, 0x20, 0x4f, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x4f, 0x20, 0x4d, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x01, 0xf5, 0x01, 0x91, 0x41, 0x20, 0x20, 0x91, 0x20, 0x4d, 0x20, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x4d, 0x20, 0x20, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x01, 0xf6, 0x01, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x4d, 0x20, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0x56, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x4d, 0x20, 0x20, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x01, 0xf7, 0x81, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x4d, 0x20, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x4d, 0x20, 0x20, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x01, 0xf8, 0x81, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x4d, 0x20, 0x91, 0x20, 0x58, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x58, 0x20, 0xa0, 0x91, 0x4d, 0x20, 0x20, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x01, 0xf9, 0x01, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0x4d, 0x91, 0x20, 0x20, 0xd8, 0x91, 0x58, 0x58, 0xd8, 0x91, 0x58, 0x58, 0xd8, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x4d, 0x20, 0x20, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x01, 0xfa, 0x01, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x4d, 0x20, 0x20, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0x4d, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x01, 0xfb, 0x81, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x4d, 0xcd, 0x91, 0x4d, 0x4d, 0x4d, 0x91, 0x4d, 0x4d, 0x4d, 0x91, 0x4d, 0x4d, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x01, 0xfc, 0x01, 0x91, 0x3c, 0x42, 0x41, 0x91, 0x43, 0x4b, 0x20, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x20, 0x20, 0xa0, 0x91, 0x00, 0x01, 0x04]


    def __init__(self):
        #Script state machine logic
        # ready - Chip is in ready state
        self.ready = False
        self.false = False
        self.chipSetup = False
        self.start_countdown = False
        self.keyPress = 0
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
            threeStatus = self.enableRxRegister(3)
            txOneStatus = self.enableTxRegister(1)


            for i in range(256):
                spi.xfer2([0x98,0x6A,((0x00 + i) & 0xFF)])
                spi.xfer2([0x88,0xFF])
                spi.xfer2([0x98,0x68,((0x00 + i) & 0xFF)])
                spi.xfer2([0x88,0xFF])

            if zeroStatus and oneStatus and twoStatus:
                print(f"Chip Setup Complete")
                self.chipSetup == True
            else:
                print(f"Chip Setup Failure")

    def isChipReady(self):
        return self.ready

    def isChipSetupComplete(self):
        return self.chipSetup

    def resetChip(self):
        #Reset chip
        GPIO.output(22, GPIO.LOW)
        time.sleep(.5)
        GPIO.output(22, GPIO.HIGH)
        return

    def checkRxRegister(self, registerNum):
        if 0 <= registerNum <= 15:
            reg = 0x20 + (registerNum & 0x0F)
            spi.xfer2([0x98,0x80,reg])
            write = spi.xfer2([0x80,0x00])
            if write[1] != 0x82:
                #print(f"Receiver {registerNum} Fail {write}")
                return False
            else:
                #print(f"Receiver {registerNum} Active")
                return True
        else:
            return False

    def checkTxRegister(self, registerNum):
        if 0 <= registerNum <= 3:
            reg = 0x30 + (registerNum & 0x03)
            spi.xfer2([0x98,0x80,reg])
            write = spi.xfer2([0x80,0x00])
            if write[1] != 0x02:
                #print(f"Transmitter {registerNum} Fail {write}")
                return False
            else:
                #print(f"Transmitter {registerNum} Active")
                return True
        else:
            return False

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
            print(f"TX {registerNum} Active")
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

    def TxMCDUMaintWords(self):
        #spi.xfer2([0xA1, 0xff, 0x09, 0x00, 0x80, 0x17, 0xf8, 0xfd, 0x8f, 0x5e, 0x23, 0x00, 0xe0, 0x7d, 0x00, 0xbc, 0x82, 0x1d, 0x08, 0x0f, 0x00])
        spi.xfer2([0xa1, 0xff, 0x90, 0x00, 0x80, 0xe8, 0xf8, 0xfd, 0x8f, 0x7a, 0x23, 0x00, 0xe0])

    def TxMCDUArbitraryWords(self, wordarray, chunk_size):
        immTx = 0xa1
        command = []
        #wa = memoryview(wordarray)
        wait = True

        for i in range(0, len(wordarray), chunk_size):
            while wait:
                spi.xfer2([0x98,0x80,0x81])
                txCount = spi.xfer2([0x80,0x00])
                #print(f"Queue Size {txCount[1]}")
                if txCount[1] == 0:
                    wait = False

            chunk = wordarray[i:i + chunk_size]
            command.append(immTx)
            command.extend(chunk)
            #print(f"{command}")
            spi.xfer2(command)
            command.clear()
            wait = True


    def ReadMCDUWords(self):
        #0x98 is the address for register access, 0x800D is the Rx 0 Threshold Value Register
        spi.xfer2([0x98,0x80,0x0D])
        #0x80 is the command for reading data, the next two bytes are dummy bytes to clock out the data
        ch0rxreg = spi.xfer2([0x80,0x00,0x00])
        threshold = ch0rxreg[1] + ch0rxreg[2]
        #self.formatResponse(ch0rxreg, "Read MCDU Rx 2 Threshold Value Register:")

        #0x98 is the address for register access, 0x806A is the Rx 2 FIFO Count
        spi.xfer2([0x98,0x80,0x6A])
        ch0rxcnt = spi.xfer2([0x80,0x00,0x00])
        datawordcnt = ch0rxcnt[1]
        #print(f"Rx 2 Threshold Value Register:{datawordcnt}")


        if datawordcnt > 0:
            self.start_countdown = False
            for i in range(datawordcnt):
                dataword = spi.xfer2([0xC0,0x20,0x00,0x00,0x00,0x00])
                #label = oct(int('{:08b}'.format(dataword[2])[::-1], 2))
                label = oct(dataword[2])
                character = dataword[5] & 0x7f
                upperData = dataword[4]
                subData =   dataword[3]
                label = label.replace('0o','')
                localKeyPress = self.keyPress
                #print(f"Label: {label} {dataword[3]} {dataword[4]} {dataword[5]}")

                #print(label)
                match label:
                    #Subsystem Identifier sent every one second
                    #Identifies the avionics component
                    # The ssi becomes the label that will be returned from the MCDU
                    case "304":
                        #print(f"Case 304 which is the CDU address")
                        #self.TxMCDUWords()
                        if(character == 0x05):
                            if(upperData == 0x01):
                                print(f"Enquire received from MAL: {dataword[4]}")
                                self.waitForEnquire = True
                                self.normalText = False
                                self.TxMCDUArbitraryWords([0x91, 0x01, 0x01, 0x12], 128)
                                print(f"RTS Sent.")
                            elif(upperData == 0x00):
                                print(f"Normal Request Received")
                                self.normalText = True
                                self.TxMCDUArbitraryWords([0x91, 0x01, 0x00, 0x92], 128)
                        elif((character == 0x06) and (self.waitForEnquire == True)):
                            print(f"ACK Received RC: {upperData}")
                        elif(character == 0x15):
                            print(f"NACK Received RC: {upperData}")
                        elif((character == 0x13) and (subData == 0x00) and (self.waitForEnquire == True) and (self.normalText == False)):
                            print(f"Function Menu CTS Received: {upperData} Sending menu")
                            self.TxMCDUArbitraryWords(self.functionMenu, 128)
                        elif((character == 0x13) and (self.normalText == True) and (self.keyPressAction == False)):
                            print(f"Main menu CTS Received: {upperData}")
                            self.TxMCDUArbitraryWords(self.configMenu, 128)
                        elif((character == 0x13) and (self.normalText == True) and (self.keyPressAction == True)):
                            self.keyPressAction == False;
                            print(f"Sub menu CTS Received: {upperData}")
                            match localKeyPress:
                                case 0x7c:
                                    print(f"7c keypress")
                                    self.TxMCDUArbitraryWords(self.happyFaceMenu, 128)
                                case 0x72:
                                    print(f"72 keypress")
                                    self.TxMCDUArbitraryWords(self.happyFaceMenu, 128)
                                case 0x75:
                                    print(f"75 keypress")
                                    self.TxMCDUArbitraryWords(self.happyFaceMenu, 128)
                                case 0x74:
                                    print(f"74 keypress")
                                    self.TxMCDUArbitraryWords(self.happyFaceMenu, 128)
                                case 0x78:
                                    print(f"78 keypress")
                                    self.TxMCDUArbitraryWords(self.happyFaceMenu, 128)

                        elif(character == 0x11):
                            print(f"Menu {upperData}")
                            self.keyPress = 0;
                            self.keyPressAction = True
                            self.keyPress = upperData
                            self.TxMCDUArbitraryWords([0x91, 0x00, 0x00, 0x06], 128)
                            self.TxMCDUArbitraryWords([0x91, 0x01, 0x00, 0x92], 128)


                    case "377":
                        continue
                        #print(f"Device Identifier")
                    #case _:
                        #print(f"Label: {label} {dataword[3]} {dataword[4]} {dataword[5]}")

        if self.start_countdown == False:
            #print(f"Starting Countdown")
            self.check_time = time.perf_counter()
            self.start_countdown = True

        if self.start_countdown:

            now_time = time.perf_counter()
            if ((now_time - self.check_time) >= .24):
                self.TxMCDUMaintWords()
                #print(f"Sending maintenance words")
                self.start_countdown = False

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
            self.start_countdown = False
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
                            #print(f"Case 344 Left Side")
                            sensorpack.n2LeftVal = (dataword[4] << 6) + ((dataword[3] & 0x1ffc) >> 2)
                        else:
                            #print(f"Case 344 Right Side")
                            sensorpack.n2RightVal = (dataword[4] << 6) + ((dataword[3] & 0x1ffc) >> 2)
                    case "255":
                        side = int(dataword[3]) & 0x03
                        if side == 0:
                            #print(f"Case 255 Fuel Center")
                            sensorpack.CenterTank = (dataword[4] << 6) + ((dataword[3] & 0x1ffc) >> 2)
                        elif side == 1:
                            #print(f"Case 255 Fuel Left")
                            sensorpack.LeftTank = (dataword[4] << 6) + ((dataword[3] & 0x1ffc) >> 2)
                        elif side == 2:
                            #print(f"Case 255 Fuel Right")
                            sensorpack.RightTank = (dataword[4] << 6) + ((dataword[3] & 0x1ffc) >> 2)
                    case "317":
                        side = int(dataword[3]) & 0x1
                        if side > 0:
                            #print(f"Case 317 Left Side")
                            sensorpack.oilPLeftVal = (dataword[4] << 6) + ((dataword[3] & 0x1ffc) >> 2)
                        else:
                            #print(f"Case 317 Right Side")
                            sensorpack.oilPRightVal = (dataword[4] << 6) + ((dataword[3] & 0x1ffc) >> 2)

        else:
            if self.start_countdown == False:
                #print(f"No data received.Starting Countdown")
                self.check_time = time.perf_counter()
            self.start_countdown = True

        if self.start_countdown:
            
            now_time = time.perf_counter()
            if ((now_time - self.check_time) >= 5):
                sensorpack.resetData()
                #print(f"Resetting Data")

