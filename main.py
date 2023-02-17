import pandas as pd
import requests
from pandas.io.json import json_normalize
import prophet as fb

coxsackieURL = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/Coxsackie%2C%20NY/next7days?unitGroup=metric&include=hours&key=9RGSNMG7YSS4ZZ8PMSVTGUGRX&contentType=json"
r = requests.get(coxsackieURL)
json = r.json()
hourly_data = json_normalize(json, record_path=['days', 'hours'])
print(fb.__version__)

kept_columns = ["datetime","temp","feelslike","dew", "humidity", "precip", "precipprob","snow","snowdepth","windspeed","winddir","pressure","cloudcover","visibility","solarradiation","uvindex"]
hourly_data['datetime'] = pd.to_datetime(hourly_data['datetimeEpoch'], unit='s')

hourly_data = hourly_data.loc[:,kept_columns]
hourly_data = hourly_data.rename(columns={'pressure':'sealevelpressure'})
hourly_data = hourly_data.add_suffix("CO")

print("Ran!")
# hourly_data.set_index('datetime', inplace=True)
