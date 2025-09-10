Verified operation on XIAO ESP32-C6 with following pinout. Using Mike Teachmans I2S examples as test cases. I2S Board was generic PCM5102 audio generator with 3.5mm output.

PCM5102 Signal Name	Xiao C6 Signal	Example Code Pin
Vin	3V3	
Gnd	Gnd	
SCK	Gnd	
BCK	GPIO22	SCK_PIN = 22
LCK/RCK	GPIO23	WS_PIN = 23
DIN	GPIO16	SD_PIN = 16
