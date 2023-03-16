import React, { useEffect, useState } from 'react';
import axios from "axios";
import './App.css'



function App() {
  const [currentTime, setCurrentTime] = useState(getCurrentTime());
  const [data, setData] = useState({
    currentTemp: 0,
    currentSR: 0,
    solarRadiationForecast: [],
    tempForecast: [],
  });

  function getCurrentTime() {
    const currentDate = new Date();
    const estTime = new Date(currentDate.getTime());
    return estTime.toLocaleTimeString();
  }

  function getArrSum(arr){
    let sum = 0;
    arr.forEach(item => {
      sum += item.yhat;
    });
    return Math.round(sum);
  }

  useEffect(() => {
    axios
      .get("https://6xszrst2l5.execute-api.us-east-2.amazonaws.com/main")
      .then((response) => {
        setData(response.data.body)
      });
  }, []);
  useEffect(() => {
    const intervalId = setInterval(() => {
      setCurrentTime(getCurrentTime());
    }, 1000);
    return () => clearInterval(intervalId);
  }, []);

  const formatTime = (datetime) => {
    const date = new Date(datetime);
    return date.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
  };

  const renderForecastColumn = (title, forecastData) => {
    return (
      <div className="forecast-column">
        <h2>{title}</h2>
        <table>
          <thead>
            <tr>
              <th>Future Time</th>
              <th>{title === 'Temperature Forecast' ? 'Predicted Temperature' : 'Predicted Solar Radiation'}</th>
            </tr>
          </thead>
          <tbody>
            {forecastData.map((forecast, index) => (
              <tr key={forecast.ds}>
                <td>
                    <div className="time">
                        {formatTime(forecast.ds)}
                    </div>
                    <div className="hour-offset">
                        (+{index+1} {index === 0 ? 'hr' : 'hrs'})
                    </div>
                </td>
                <td>{forecast.yhat.toFixed(1)} {title === 'Temperature Forecast' ? '°C' : 'W/m²'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  return (
    <div className="app">
        <div className="header">
            <h1>Local Weather Forecast</h1>
            <div className="current-time">{getCurrentTime()} EST</div>
        </div>
      <div className="top-row">
        <div className="box">
          <h2>Current Temperature</h2>
          <p>{data.currentTemp}&deg;C</p>
        </div>
        <div className="box">
          <h2>24 Hour Solar Production</h2>
          <p>{getArrSum(data.solarRadiationForecast)} Wh/m²</p>
        </div>
        <div className="box">
          <h2>Current Solar Radiation</h2>
          <p>{data.currentSR} W/m<sup>2</sup></p>
        </div>
      </div>
      <div className="bottom-row">
        {renderForecastColumn('Temperature Forecast', data.tempForecast)}
        {renderForecastColumn('Solar Radiation Forecast', data.solarRadiationForecast)}
      </div>
    </div>
  );
}

export default App;





