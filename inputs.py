import time
from adafruit_bme280 import basic as adafruit_bme280
import board
import busio
import digitalio
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

print("Successful imports")
i2c = busio.I2C(board.I2C1_SCL, board.I2C1_SDA)
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)

#hPa
SchenectadySeaLevelPressure = 1004

bme280.sea_level_pressure = SchenectadySeaLevelPressure

# create the SPI bus
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

# create the chip select
cs = digitalio.DigitalInOut(board.CE0)

# create the MCP3008 object
mcp = MCP.MCP3008(spi, cs)

# create an analog input channel on CH0
chan0 = AnalogIn(mcp, MCP.P0)

# read the voltage and current
voltage = chan0.voltage


while True:
    print("\nTemperature: %0.1f C" % bme280.temperature)
    print("Humidity: %0.1f %%" % bme280.relative_humidity)
    print("Pressure: %0.1f hPa" % bme280.pressure)
    #print("Altitude = %0.2f meters" % bme280.altitude)
    print("Voltage: %0.2f V" % voltage)
    time.sleep(2)
