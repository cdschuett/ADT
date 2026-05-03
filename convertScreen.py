import sys
import binascii
import struct

def get_bytes_parity(data: bytes) -> int:
    """
    Calculates the parity of multiple bytes using XOR.
    Returns 0 for even parity and 1 for odd parity.
    """
    if not data:
        return 0  # No bits, so the number of '1's is zero (even)

    # Use functools.reduce to XOR all bytes together
    from functools import reduce
    total_xor = reduce(lambda x, y: x ^ y, data)

    # Now, calculate the parity of the single resulting byte
    # This loop counts the set bits in the single number
    parity = 0
    while total_xor:
        parity ^= 1
        total_xor &= total_xor - 1  # Magic trick to clear the lowest set bit
    return parity

def findcolor(code):
    if code == 0:
        colortxt = "Black"
    elif code == 1:
        colortxt = "Cyan"
    elif code == 2:
        colortxt = "Red"
    elif code == 3:
        colortxt = "Yellow"
    elif code == 4:
        colortxt = "Green"
    elif code == 5:
        colortxt = "Magenta"
    elif code == 6:
        colortxt = "Amber"
    elif code == 7:
        colortxt = "White"
    else:
        colortxt = "Undefined"
    return(colortxt)

def letterfunction(code):
    if code == 1:
        functiontxt = "Reverse Video"
    elif code == 2:
        functiontxt = "Underscore"
    elif code == 4:
        functiontxt = "Flashing"
    else:
        functiontxt = "Undefined"
    return(functiontxt)

def menufunction(code):
    if code == 0:
        functiontext = "Normal Request"
    elif code == 1:
        functiontext = " Menu Text Request"
    else:
        functiontext = "Undefined"
    return(functiontext)

def encodeControl(mal, linenum, initialchar, color):
    data_word = bytearray()
    data_word.append(mal)
    data_word.append(0x00 + (initialchar & 0x0f))
    data_word.append(0x80 + ((color << 4) & 0x70) + (linenum & 0x0f))
    data_word.append(0x01) #CNTRL word
    parity = get_bytes_parity(data_word)
    if parity == 0:
        data_word[3] = data_word[3] | 0x80
    return(data_word)

def encodeSTX(mal, recCount, recordNum):
    data_word = bytearray()
    data_word.append(mal)
    data_word.append(recCount & 0xff)
    data_word.append(recordNum & 0x0f)
    data_word.append(0x02) #STX word
    parity = get_bytes_parity(data_word)
    if parity == 0:
        data_word[3] = data_word[3] | 0x80
    return(data_word)

def encodeETX(mal, recordNum):
    data_word = bytearray()
    data_word.append(mal)
    data_word.append(0x00)
    data_word.append(recordNum & 0x0f)
    data_word.append(0x03) #ETX word
    parity = get_bytes_parity(data_word)
    if parity == 0:
        data_word[3] = data_word[3] | 0x80
    return(data_word)

def encodeEOT(mal, recordNum):
    data_word = bytearray()
    data_word.append(mal)
    data_word.append(0x00)
    data_word.append(recordNum & 0x0f)
    data_word.append(0x04) #EOT word
    parity = get_bytes_parity(data_word)
    if parity == 0:
        data_word[3] = data_word[3] | 0x80
    return(data_word)

def encodeChar(string,mal):
    new_string = string.replace('+', ' ')
    byte_representation = new_string.encode("utf-8")
    data_word = bytearray()
    data_word.append(mal)
    data_word.extend(byte_representation)
    parity = get_bytes_parity(data_word)
    if parity == 0:
        data_word[3] = data_word[3] | 0x80
    return(data_word)

filename = sys.argv[1]

mal = 0x91
screen_array = []
menu_array = []

with open(filename, "r") as file:
    lines = file.readlines()

out = open("dlkmenu.asc", "w")


for linenum,line in enumerate(lines):
    text = line.strip()
    groups = [text[i:i+3] for i in range(0, len(text), 3)]
    menu_array.append(encodeControl(0x91,(linenum + 1), 1, 7))
    for group in groups:
        # For Alta: menu_array.append(encodeChar(group[::-1],0x91))
        # For Holt
        menu_array.append(encodeChar(group,0x91))

screen_array.append(encodeSTX(mal, (len(menu_array)+2), 1))
screen_array.extend(menu_array)
#screen_array.append(encodeETX(mal, 1))
screen_array.append(encodeEOT(mal, 1))

print(type(screen_array))

out.write(f"[")
for datanum, dataword in enumerate(screen_array):
    # For alta: out.write(f"mainMenuList[{datanum}] = 0x{dataword.hex()};\n")
    # For holt:
    for num, value in enumerate(dataword):
        out.write(f"{value:#04x}, ")
out.write(f"]\n")

out.close

print(screen_array)

out.close()
