from prophet import Prophet
import pandas as pd
import pickle
import json

def handler(event, context):
    print("Got here")
    weather = pd.read_csv("https://pipesjweatherdata.s3.us-east-2.amazonaws.com/manipulatedWeatherData.csv", dtype={"tempSC":float, "solarradiationSC":float})
    print("Past reading")
    weather["datetime"]=pd.to_datetime(weather["datetime"])
    weather['ds']=pd.DatetimeIndex(weather['datetime'])


    with open('tempModel.pkl', 'rb') as f:
        mT = pickle.load(f)
    with open('solarRadModel.pkl', 'rb') as f:
        mSR = pickle.load(f)

    print("Past pickle")

    lastDay = weather.tail(24)

    forecastTemp=mT.predict(lastDay)
    forecastSR=mSR.predict(lastDay)
    
    forecastSR[['yhat']]=forecastSR[['yhat']].clip(lower=0)
    forecastSR[['yhat']]=forecastSR[['yhat']].astype(float)
     # Convert forecastSR ds column to JSON serializable format
    forecastSR['ds'] = forecastSR['ds'].dt.strftime('%Y-%m-%d %H:%M:%S')

    # Convert forecastTemp ds column to JSON serializable format
    forecastTemp['ds'] = forecastTemp['ds'].dt.strftime('%Y-%m-%d %H:%M:%S')
    forecastTemp[['yhat']] = forecastTemp[['yhat']].astype(float)

    # convert forecastSR to a dictionary
    forecastSR_dict = forecastSR[['ds', 'yhat']].to_dict('records')


    # convert forecastTemp to a dictionary
    forecastTemp_dict = forecastTemp[['ds', 'yhat']].to_dict('records')
    print(type(float(weather['tempSC'].iloc[-1])))
    return {
        'statusCode': 200,
        'body':{"message":'Predictions are in "solarRadiationForecast" & "tempForecast". They are 24 hours predictions at each time for Schenectady. Actual value is in "yhat"',
        'solarRadiationForecast': forecastSR_dict,
        'tempForecast': forecastTemp_dict,
        'currentTemp': float(weather['tempSC'].iloc[-1]),
        'currentSR': int(max(weather['solarradiationSC'].iloc[-1], 0))
    }
    
}




