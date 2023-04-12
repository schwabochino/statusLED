# Example using PIO to drive a set of WS2812 LEDs.
import array, time, network, socket
from machine import Pin
import rp2

ssid = 'ssid'
password = 'secret'

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

html = """<!DOCTYPE html>

<!DOCTYPE html>
<html>
<head>
    <title>Status</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        .container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            margin-top: 10%;
            height: 80vh;
        }

        .button {
            background-color: #657383;
            color: #FFFFFF;
            padding: 8px 0;
            width: 70%;
            height: 15%;
            border-radius: 5px;
            margin-bottom: 2%;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.3s ease-in-out;
        }

        .button:hover {
            background-color: #0066CC;
            transform: scale(1.1);
        }

        .button.red {
            background-color: #657383;
        }

        .button.green {
            background-color: #657383;
        }

        .button.grey {
            background-color: #657383;
        }

        .button.purple {
            background-color: #657383;
        }
    </style>
</head>
<body>
    <div class="container">
        <button class="button red" onclick="window.location.href='http://192.168.178.202/light/red'">Rot</button>
        <button class="button green" onclick="window.location.href='http://192.168.178.202/light/green'">Grün</button>
        <button class="button grey" onclick="window.location.href='http://192.168.178.202/light/off'">OFF</button>
        <button class="button purple" onclick="window.location.href='http://192.168.178.202/light/party'">Party</button>
    </div>
</body>
</html>




"""

max_wait = 60
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    print('waiting for connection...')
    time.sleep(1)

if wlan.status() != 3:
    raise RuntimeError('network connection failed')
else:
    print('connected')
    status = wlan.ifconfig()
    print( 'ip = ' + status[0] )

addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

s = socket.socket()
s.bind(addr)
s.listen(1)

# Configure the number of WS2812 LEDs.
NUM_LEDS = 160
PIN_NUM = 6
i=0


@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_LEFT, autopull=True, pull_thresh=24)
def ws2812():
    T1 = 2
    T2 = 5
    T3 = 3
    wrap_target()
    label("bitloop")
    out(x, 1)               .side(0)    [T3 - 1]
    jmp(not_x, "do_zero")   .side(1)    [T1 - 1]
    jmp("bitloop")          .side(1)    [T2 - 1]
    label("do_zero")
    nop()                   .side(0)    [T2 - 1]
    wrap()
        
        
class NeoPixel(object):
    def __init__(self,pin=PIN_NUM,num=NUM_LEDS,brightness=0.8):
        self.pin=pin
        self.num=num
        self.brightness = brightness
        
        # Create the StateMachine with the ws2812 program, outputting on pin
        self.sm = rp2.StateMachine(0, ws2812, freq=8_000_000, sideset_base=Pin(PIN_NUM))

        # Start the StateMachine, it will wait for data on its FIFO.
        self.sm.active(1)

        # Display a pattern on the LEDs via an array of LED RGB values.
        self.ar = array.array("I", [0 for _ in range(self.num)])
        
        self.BLACK = (0, 0, 0)
        self.RED = (0, 255, 0)
        self.ORANGE = (50, 255,0)
        self.YELLOW = (15, 15, 0)
        self.GREEN = (255, 0, 0)
        self.CYAN = (0, 15, 15)
        self.BLUE = (0, 0, 15)
        self.PURPLE = (0, 15, 15)
        self.WHITE = (15, 15, 15)
        self.COLORS = [self.RED, self.YELLOW, self.GREEN, self.CYAN, self.BLUE, self.PURPLE, self.WHITE,self.BLACK ]
        self.lattice = [self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN,
                        self.CYAN, self.CYAN, self.RED, self.RED, self.CYAN, self.CYAN, self.RED, self.RED, self.RED, self.RED, self.CYAN, self.CYAN, self.CYAN, self.RED, self.RED, self.CYAN,
                        self.CYAN, self.RED, self.RED, self.RED, self.CYAN, self.RED, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.RED, self.CYAN, self.RED, self.RED, self.RED, self.CYAN,
                        self.CYAN, self.CYAN, self.RED, self.RED, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.RED, self.RED, self.CYAN, self.CYAN, self.RED, self.RED, self.CYAN,
                        self.CYAN, self.CYAN, self.RED, self.RED, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.RED, self.RED, self.CYAN, self.CYAN, self.CYAN, self.RED, self.RED, self.CYAN,
                        self.CYAN, self.CYAN, self.RED, self.RED, self.CYAN, self.CYAN, self.CYAN, self.RED, self.RED, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.RED, self.RED, self.CYAN,
                        self.CYAN, self.CYAN, self.RED, self.RED, self.CYAN, self.CYAN, self.RED, self.RED, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.RED, self.RED, self.CYAN,
                        self.CYAN, self.CYAN, self.RED, self.RED, self.CYAN, self.RED, self.RED, self.RED, self.RED, self.RED, self.RED, self.CYAN, self.CYAN, self.RED, self.RED, self.CYAN,
                        self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN,
                        self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN]
        
    ##########################################################################
    def pixels_show(self):
        dimmer_ar = array.array("I", [0 for _ in range(self.num)])
        for i,c in enumerate(self.ar):
            r = int(((c >> 8) & 0xFF) * self.brightness)
            g = int(((c >> 16) & 0xFF) * self.brightness)
            b = int((c & 0xFF) * self.brightness)
            dimmer_ar[i] = (g<<16) + (r<<8) + b
        self.sm.put(dimmer_ar, 8)

    def pixels_set(self, i, color):
        self.ar[i] = (color[1]<<16) + (color[0]<<8) + color[2]

    def pixels_fill(self, color):
        for i in range(len(self.ar)):
            self.pixels_set(i, color)

    def color_chase(self, color, length):
        for i in range(self.num):
            self.pixels_set(length, color)
            time.sleep(wait)
            self.pixels_show()
            time.sleep(0.2)
     
    def wheel(self, pos):
        # Input a value 0 to 31 to get a color value.
        # The colours are a transition r - g - b - back to r.
        if pos < 0 or pos > 31:
            return (0, 0, 0)
        if pos < 10:
            return (31 - pos * 3, pos * 3, 0)
        if pos < 15:
            pos -= 10
            return (0, 31 - pos * 3,pos * 3)
        pos -= 15
        return (pos * 3, 0, 31 - pos * 3)
     
     
    def rainbow_cycle(self, wait):
        for j in range(256):
            for i in range(self.num):
                rc_index = (i * 256 // self.num) + j
                self.pixels_set(i, self.wheel(rc_index & 31))
            self.pixels_show()
            time.sleep(wait)
    
    def red_light(self, wait):
        self.pixels_fill(strip.RED)
        self.pixels_show()
        
    def green_light(self, wait):
        self.pixels_fill(strip.GREEN)
        self.pixels_show()
    
    def off(self,wait):
        self.pixels_fill(strip.BLACK)
        self.pixels_show()
    
    def blinker(self, wait):
        self.pixels_fill(strip.ORANGE)
        self.pixels_show()
        
    
     
if __name__=='__main__':
    
    strip = NeoPixel()
    color1 = 0
    color2 = 15
    num1 = 0
    num2 = 1
    num3 = 15

    print("start")
    
    while True:
        try:
            cl, addr = s.accept()
            print('client connected from', addr)
            request = cl.recv(1024)
            print(request)

            request = str(request)
            led_red = request.find('/light/red')
            led_green = request.find('/light/green')
            led_off = request.find('/light/off')
            led_party = request.find('light/party')
#             print( 'led on = ' + str(led_on))
#             print( 'led off = ' + str(led_off))
            
            stateis = "LED is off" # Set default value
            
            if led_red == 6:
                #print("led red")
                strip.red_light(0)
                stateis = "LED is RED"

            if led_green == 6:
                #print("led gree")
                strip.green_light(0)
                stateis = "LED is GREEN"
            
            if led_off == 6:
                strip.off(0)
                stateis = "LED is OFF"
            
            if led_party == 6:
                strip.rainbow_cycle(1)
                stateis = "LED is Party"

            response = html #% stateis

            cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
            cl.send(response)
            cl.close()

        except OSError as e:
            cl.close()
            print('connection closed')
