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
import numpy as np
import json
import os

# ssh mendel@192.168.137.114

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
chan2 = AnalogIn(mcp, MCP.P2)

time_between_readings = 3540000 #59 minutes in ms


kept_columns = ["datetime","temp","feelslike","dew", "humidity", "precip", "precipprob","snow","snowdepth","windspeed","winddir","pressure","cloudcover","visibility","solarradiation","uvindex"]
csv_path = "uploadData.csv"

# Define the API endpoint URL
url = 'https://vbxih78ri8.execute-api.us-east-2.amazonaws.com/Main'

def average_inputs():
    inputs_averaged = [0]*6
    pressure = [0]*6
    temp = [0]*6
    hum = [0]*6
    sR = [0]*6
    print("Averaging current readings!")
    for i in range(6):
        pressure[i] = bme280.pressure
        temp[i] = bme280.temperature
        hum[i] = bme280.relative_humidity
        sR[i] = chan0.voltage((chan0.voltage - chan2.voltage) / 10000 )   #10*10^3 kOhm resistor... V*V/R = VI = Watts
        print("Reading #%d \n Voltage: %f, Power %f, Pressure %f, Temp %f, Humidity %f." %(i, chan0.voltage, sR[i], pressure[i], temp[i],hum[i]))
        time.sleep(5)
    pressure = np.array(pressure)
    temp = np.array(temp)
    hum = np.array(hum)
    sR = np.array(sR)

  
    inputs_averaged[0] = np.mean(pressure)
    inputs_averaged[1] = np.mean(temp)
    inputs_averaged[2] = np.mean(hum)
    inputs_averaged[3] = np.mean(sR)

    return inputs_averaged

while True:
    timeZoneAdjustment = -5 #hours different from UTC to EST
    exactCurrent_datetime = datetime.utcnow()+timedelta(hours=timeZoneAdjustment)
    current_datetime = exactCurrent_datetime.replace(minute=0, second=0, microsecond=0) # Replace with the desired rounding
    target_datetime = current_datetime + timedelta(days=1)

    inputReadings = pd.DataFrame()
    hours_days_addOn = pd.DataFrame()
    
    averaged_inputs = average_inputs()

    inputReadings['datetime'] = [current_datetime]
    inputReadings['sealevelpressureSC'] = [round(averaged_inputs[0],2)]
    inputReadings['tempSC'] = [round(averaged_inputs[1],2)]
    inputReadings['humiditySC'] = [round(averaged_inputs[2],2)]
    inputReadings['solarradiationSC'] = [averaged_inputs[3]]
    

    hours_days_addOn['dayOfYear'] = [current_datetime.timetuple().tm_yday]
    hours_days_addOn['hours'] = [current_datetime.hour]


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

    combined_data = pd.concat([inputReadings.iloc[0] ,hours_days_addOn.iloc[0], hourly_dataSS.loc[target_datetime], hourly_dataGA.loc[target_datetime], hourly_dataCO.loc[target_datetime]], axis=0, ignore_index=False)
    # Convert datetime object to string
    combined_data[0] = combined_data[0].strftime('%Y-%m-%d %H:%M:%S')

    # Convert row to array
    data = combined_data.values.tolist()
    
        
    print(data)
    # Convert the data to a JSON string
    payload = json.dumps(data)

    # Set the headers
    headers = {'Content-Type': 'application/json'}

    # Send the POST request
    response = requests.post(url, headers=headers, data=payload)

    # Print the response from the Lambda function
    print(response.text)


    os.system('systemctl suspend -i 3540')




    