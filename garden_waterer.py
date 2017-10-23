import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
import Adafruit_DHT
import RPi.GPIO as GPIO 
import time
import requests
from time import gmtime, strftime
import json
import conf

GPIO.setmode(GPIO.BCM)
GPIO.setup(26, GPIO.OUT) 	# set a controlable VCC for sensors, to avoid keeping ON all the time to avoid galvanization
GPIO.output(26, 1)

# constants
time_readings = 0.1 		# time between each reading to compute average

def vcc_sensors_on():
	GPIO.output(26, 0)

def vcc_sensors_off():
	GPIO.output(26, 1)

# Software SPI configuration:
# CLK  = 18
# MISO = 23
# MOSI = 24
# CS   = 25
# mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)

# Hardware SPI configuration:
SPI_PORT   = 0
SPI_DEVICE = 0
mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

sensor = Adafruit_DHT.DHT22

# Main program loop.
while True:
	s, r, l = [], [], []
	h, t = [], []
	vcc_sensors_on()
	time.sleep(1)
	for i in range(0,5): # takes avg 5 points each second
		time.sleep(time_readings)
		h0, t0 = Adafruit_DHT.read_retry(sensor, 16)
		s.append(1023 - mcp.read_adc(0))
		r.append(1023 - mcp.read_adc(1))
		l.append(1023 - mcp.read_adc(2))
		h.append(h0)
		t.append(t0)
		print "Partials: "
		print "Soil Moisture=" + str(1023 - mcp.read_adc(0)) + " Rain=" + str(1023 - mcp.read_adc(1)) + " Luminosity=" + str(1023 - mcp.read_adc(2)) + ' Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(t0, h0)
	vcc_sensors_off()
	soil = sum(s)/len(s)
	rain = sum(r)/len(r)
	luminosity = sum(l)/len(l)
	temperature = sum(t)/len(t)
	humidity = sum(h)/len(h)
	print "Soil Moisture=" + str(soil) + " Rain=" + str(rain) + " Luminosity=" + str(luminosity) + ' Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(temperature, humidity)
	time_now = strftime("%Y-%m-%d %H:%M:%S", gmtime())
	print time_now
	payload = {
		"datetime": time_now,
		"pump": 0,
		"soil": soil,
		"temperature": temperature,
		"humidity": humidity,
		"rain": rain,
		"light": luminosity
	}
	print payload
	r = requests.post('http://ec2-54-186-186-243.us-west-2.compute.amazonaws.com', data = payload, auth=HTTPBasicAuth(conf.auth_user, conf.auth_pass))

	time.sleep(5)
