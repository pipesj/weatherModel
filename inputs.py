import time
from adafruit_bme280 import basic as adafruit_bme280
import board
import busio
import digitalio
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import pandas as pd
import requests
from pandas.io.json import json_normalize
import os.path
from datetime import datetime, timedelta

kept_columns = ["datetime","temp","feelslike","dew", "humidity", "precip", "precipprob","snow","snowdepth","windspeed","winddir","pressure","cloudcover","visibility","solarradiation","uvindex"]
csv_path = "uploadData.csv"

print("Successful imports")
i2c = busio.I2C(board.I2C1_SCL, board.I2C1_SDA)
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)

#hPa
SchenectadySeaLevelPressure = 1004

bme280.sea_level_pressure = SchenectadySeaLevelPressure

# create the SPI bus
spi = busio.SPI(clock=board.SPI_CLK, MISO=board.SPI_MI, MOSI=board.SPI_MO)

# create the chip select
cs = digitalio.DigitalInOut(board.SPI_CSB)

# create the MCP3008 object
mcp = MCP.MCP3008(spi, cs)

# create an analog input channel on CH0
chan0 = AnalogIn(mcp, MCP.P0)

minutes = 60
time_between_readings = 60*minutes


kept_columns = ["datetime","temp","feelslike","dew", "humidity", "precip", "precipprob","snow","snowdepth","windspeed","winddir","pressure","cloudcover","visibility","solarradiation","uvindex"]
csv_path = "uploadData.csv"






while True:
    current_datetime = datetime.now().replace(minute=0, second=0, microsecond=0) # Replace with the desired rounding
    target_datetime = current_datetime + timedelta(days=1)

    inputReadings = pd.DataFrame()
    hours_days_addOn = pd.DataFrame()
    

    inputReadings['datetime'] = [current_datetime]
    inputReadings['solarradiationSC'] = [chan0.voltage]
    inputReadings['tempSC'] = [bme280.temperature]
    inputReadings['humiditySC'] = [bme280.relative_humidity]
    inputReadings['pressureSC'] = [bme280.relative_humidity]

    hours_days_addOn['hours'] = [current_datetime.timetuple().tm_yday]
    hours_days_addOn['dayOfYear'] = [current_datetime.hour]



    coxsackieURL = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/Coxsackie%2C%20NY/next7days?unitGroup=metric&include=hours&key=9RGSNMG7YSS4ZZ8PMSVTGUGRX&contentType=json"
    coxR = requests.get(coxsackieURL)
    jsonCO = coxR.json()
    hourly_dataCO = json_normalize(jsonCO, record_path=['days', 'hours'])
    hourly_dataCO['datetime'] = pd.to_datetime(hourly_dataCO['datetimeEpoch'], unit='s')
    hourly_dataCO.index = hourly_dataCO['datetime']

    hourly_dataCO = hourly_dataCO.loc[:,kept_columns[1:]]
    hourly_dataCO = hourly_dataCO.rename(columns={'pressure':'sealevelpressure'})
    hourly_dataCO = hourly_dataCO.add_suffix("CO")


    gansevoortURL = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/Gansevoort%2C%20Ny?unitGroup=metric&key=9RGSNMG7YSS4ZZ8PMSVTGUGRX&contentType=json"
    gaR = requests.get(gansevoortURL)
    jsonGA = gaR.json()
    hourly_dataGA = json_normalize(jsonGA, record_path=['days', 'hours'])
    hourly_dataGA['datetime'] = pd.to_datetime(hourly_dataGA['datetimeEpoch'], unit='s')
    hourly_dataGA.index = hourly_dataGA['datetime']

    hourly_dataGA = hourly_dataGA.loc[:,kept_columns[1:]]
    hourly_dataGA = hourly_dataGA.rename(columns={'pressure':'sealevelpressure'})
    hourly_dataGA = hourly_dataGA.add_suffix("GA")


    sharonSpringsURL = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/Sharon%20Springs%2C%20NY?unitGroup=metric&key=9RGSNMG7YSS4ZZ8PMSVTGUGRX&contentType=json"
    ssR = requests.get(sharonSpringsURL)
    jsonSS = ssR.json()
    hourly_dataSS = json_normalize(jsonSS, record_path=['days', 'hours'])

    hourly_dataSS['datetime'] = pd.to_datetime(hourly_dataSS['datetimeEpoch'], unit='s')
    hourly_dataSS.index = hourly_dataSS['datetime']

    hourly_dataSS = hourly_dataSS.loc[:,kept_columns[1:]]
    hourly_dataSS = hourly_dataSS.rename(columns={'pressure':'sealevelpressure'})
    hourly_dataSS = hourly_dataSS.add_suffix("SS")


    if os.path.isfile(csv_path) and os.path.getsize(csv_path) > 0:
        combined_data = pd.concat([inputReadings.iloc[0] ,hourly_dataSS.loc[target_datetime], hourly_dataGA.loc[target_datetime], hourly_dataCO.loc[target_datetime],hours_days_addOn.iloc[0]], axis=0, ignore_index=False)
        combined_data = combined_data.to_frame().transpose()
        combined_data.to_csv(csv_path, mode='a', index=False, header=False)
    else:

        combined_data = pd.concat([inputReadings.iloc[0] ,hourly_dataSS.loc[target_datetime], hourly_dataGA.loc[target_datetime], hourly_dataCO.loc[target_datetime], hours_days_addOn.iloc[0]], axis=0, ignore_index=False)
        combined_data = combined_data.to_frame().transpose()
        combined_data.to_csv(csv_path, mode='w', index=False, header=True)
    
        
    print(combined_data.iloc[0])
    time.sleep(time_between_readings)




    