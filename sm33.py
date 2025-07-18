#====================================================================
# sm33.py    esp32-C6 for SM33 Pirate Robot Head
#            Uses I2S sound board and SD card for wav files   
#							  
#====================================================================
#
# Uses Mike Teachman waveplayer.py
#
from machine import Pin, RTC, SoftSPI, Timer, I2S, SDCard, ADC, PWM
from umqtt.simple import MQTTClient
import ubinascii
import time
import json
import network
import machine
import os
import random
import micropython
from wavplayer import WavPlayer


#----------------------------------------------------------------------#
# I2S configuration

SCK_PIN = 22
WS_PIN = 23
SD_PIN = 21
I2S_ID = 0
BUFFER_LENGTH_IN_BYTES = 40000
sampbuf_size = 500
samples = []
sound_active = False
sound_topic = ""
sound_payload = ""

#-------------------------------------------------------------------------#
def do_message(topic, msg):  # process incoming messages - callback
    global sound_active
    global sound_topic
    global sound_payload
    
    if pflag :
        print("Topic %s Message %s " % (topic, msg) )
    sound_topic = topic.decode('utf-8')
    sound_payload = msg.decode('utf-8')
    sound_active = True     
    
          
#--------------------------------------------------------------------------#   
def sub_topic(TOPIC) :
    
    c.subscribe(TOPIC)
    if pflag :
        print("Connected to %s, subscribed to %s topic" % (SERVER, TOPIC))        
    


#----------------------------------------------------------------------#
# Read json wifi configuration

with open('config.json') as fptr:
    config = json.load(fptr)
    
SERVER = config["server"]
SSID = config["ssid"]
PWD = config["password"]
pflag = config["printflag"]

if pflag:
    print("Configuration : --------------------------------------- ")
    print(config)
fptr.close()

#----------------------------------------------------------------------#
# Read json soundfiles 

with open('soundfiles.json') as fptr:
    config = json.load(fptr)
    
if pflag:
    print("Sound files : --------------------------------------- ")
    print(config)
fptr.close()

# Default MQTT server to connect to
CLIENT_ID = ubinascii.hexlify(machine.unique_id())

n = network.WLAN(network.STA_IF)
n.active(True)
n.connect(SSID,PWD)
while not n.isconnected() :
    time.sleep(1)

if pflag : print("WLAN:", n.ifconfig())

c = MQTTClient(CLIENT_ID, SERVER)

# Subscribed messages will be delivered to this callback
c.set_callback(do_message)
c.connect()



sub_topic('PIRATE')
sub_topic('SM33')

soundIn = ADC(Pin(1))
eye = Pin(0, Pin.OUT)
soundLevel = soundIn.read_u16()

# Set the ADC width (resolution) to 12 bits
soundIn.width(ADC.WIDTH_12BIT)
# Set the attenuation to 11 dB, allowing input range up to ~3.3V
soundIn.atten(ADC.ATTN_11DB)

sd = SDCard(slot=2, sck=19, cs=17, miso=20, mosi=18)
os.mount(sd, "/sd")


# Main loop -----------------------------------------------------------
#
while 1:
    print("in the main loop")
    try:
        while 1:
            c.check_msg()
            
            
            if sound_active :
               sound_active = False
               eye.off()


               # ======= AUDIO CONFIGURATION =======
                
               WAV_FILE = config[sound_payload][0]
               WAV_SAMPLE_SIZE_IN_BITS = config[sound_payload][1]
               FORMAT = I2S.MONO
               SAMPLE_RATE_IN_HZ = config[sound_payload][3]

               wp = WavPlayer(id=I2S_ID,sck_pin=Pin(SCK_PIN),ws_pin=Pin(WS_PIN),sd_pin=Pin(SD_PIN),ibuf=BUFFER_LENGTH_IN_BYTES,)

               wp.play(WAV_FILE, loop=False)
               # wait until the entire WAV file has been played
               while wp.isplaying() == True:
                    # other actions can be done inside this loop during playback

                    soundLevel = soundIn.read_u16()
                    duty = min(int(84000*soundLevel/10000), 65535)
                    pwm0 = PWM(eye, freq=200, duty_u16=duty)

            
               wp.stop()  # continue playing to the end of the WAV file
               pwm0.deinit()
               eye.off()                              
                              
    finally:
        c.disconnect()
        




