#====================================================================
# sm33.py    esp32-C6 for SM33 Pirate Robot Head
#
# scase   	 4/25/22   
#							  
#====================================================================
#
# Uses I2S non-blocking code Copyright (c) 2022 Mike Teachman
# Non-blocking version
# - the write() method is non-blocking.
# - a callback function is called when all sample data has been
#   written to the I2S interface
# - a callback() method sets the callback function

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
SD_PIN = 16
I2S_ID = 0
BUFFER_LENGTH_IN_BYTES = 40000


#----------------------------------------------------------------------#
# Read json wifi configuration

with open('config.json') as fptr:
    config = json.load(fptr)
    
SERVER = config["server"]
SSID = config["ssid"]
PWD = config["password"]
pflag = config["printflag"]

print("Configuration : --------------------------------------- ")
print(config)
fptr.close()

#----------------------------------------------------------------------#
# Read json soundfiles 

with open('soundfiles.json') as fptr:
    config = json.load(fptr)
    
#print(config)
fptr.close()

# Default MQTT server to connect to
CLIENT_ID = ubinascii.hexlify(machine.unique_id())

#----------------------------------------------------------------------#
# mqtt callback

def do_message(client, userdata, message):
  print("message received " ,str(message.payload.decode("utf-8")))
  #sound = str(message.payload.decode("utf-8"))
  print("message topic=", message.topic)
  sound = str(message.payload.decode("utf-8"))  
  if (message.topic == "RP1"):
      GPIO.output(23, True)
      
  elif (message.topic == "RP2"):
      GPIO.output(24, True)
      

  #os.system('omxplayer -o alsa:hw:1,0 ../trick_or_treat/' + sound + '&')
  os.system('omxplayer -o local ../trick_or_treat/' + sound )
  #os.system('omxplayer -o alsa:hw:1,0 ../trick_or_treat/' + sound + '&')
  #os.system('aplay --buffer-size=260000 ../trick_or_treat/' + sound +"&")
  
  print("Topic = ", message.topic)
  print("Payload = ", message.payload)        
  clear_GPIO()

soundIn = ADC(Pin(1))
eye = Pin(0, Pin.OUT)
soundLevel = soundIn.read_u16()

# pwm0 = PWM(eye, freq=200, duty_u16=32768)
# pwm0.duty(256)
eye.on()

# Set the ADC width (resolution) to 12 bits
soundIn.width(ADC.WIDTH_12BIT)
# Set the attenuation to 11 dB, allowing input range up to ~3.3V
soundIn.atten(ADC.ATTN_11DB)
sd = SDCard(slot=2, sck=19, cs=21, miso=20, mosi=18)
os.mount(sd, "/sd")

time.sleep(0.5)
n=network.WLAN(network.STA_IF)
n.active(True)
n.connect(SSID,PWD)
while not n.isconnected() :
    time.sleep(1)

print("WLAN:", n.ifconfig())
server=SERVER
c = MQTTClient(CLIENT_ID, server)


# set the callback for mqtt commands
# 	1. play specific index
# 	2. go into auto/random mode
# 	3. exit auto / random mode
# 	impor4. set random mode time interval
## TODO main
# if random flag set: generate random index into sounds dictionary
#    to pull file attributes for audio configuration
# if specific file index requested pull file attributes
#
# use attribute data and play one file from sd card



for i in range(0,6) :
    # loop thru a few sounds
    # generate a random # between 0 n (test case)
    #r = random.randint(0,5)
    r = i
    print(r)
    eye.off()


    # ======= AUDIO CONFIGURATION =======
    
    WAV_FILE = config["sound"+str(r)][0]
    WAV_SAMPLE_SIZE_IN_BITS = config["sound"+str(r)][1]
    FORMAT = I2S.MONO
    SAMPLE_RATE_IN_HZ = config["sound"+str(r)][3]

    wp = WavPlayer(id=I2S_ID,sck_pin=Pin(SCK_PIN),ws_pin=Pin(WS_PIN),sd_pin=Pin(SD_PIN),ibuf=BUFFER_LENGTH_IN_BYTES,)

    soundMax = 0

    wp.play(WAV_FILE, loop=False)
    # wait until the entire WAV file has been played
    while wp.isplaying() == True:
        # other actions can be done inside this loop during playback
        soundLevel = soundIn.read_u16()
#        eye.toggle()
        if soundLevel > 2500 :
            pwm0 = PWM(eye, freq=200, duty_u16=32000)
        elif soundLevel > 1000 :
            pwm0 = PWM(eye, freq=200, duty_u16=10000)
        elif soundLevel < 500 :
            pwm0 = PWM(eye, freq=200, duty_u16=800)
        elif soundLevel < 200 :
            pwm0.deinit()
            #pwm0 = PWM(eye, freq=200, duty_u16=100)

#        print(soundLevel)

        pass
    pwm0.deinit()

wp.stop()  # continue playing to the end of the WAV file
pwm0.deinit()
eye.off()



