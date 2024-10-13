import React from "react";

import TempGauge from "../assets/TempGauge";
import PressureGauge from "../assets/PressureGauge";


export default function Gauge({gaugeData}) {

  const maxPressure = 2000

  const pressure = Math.max(0,Math.min(gaugeData.pressure,maxPressure))
  const rotation = (pressure / maxPressure)*300 +30


  return (

    <div className="gauge-container">
      <div >
        <h1>LIGHT</h1>
        <TempGauge temperature={gaugeData.light} barColour={"#f9f871"}/>
        <h2>{gaugeData.light} LUX</h2>
      </div>
      <div >
        <h1>HUMIDITY</h1>
        <TempGauge temperature={gaugeData.humidity} barColour={"#a0f28a"}/>
        <h2>{gaugeData.humidity}%</h2>
      </div>
      <div >
        <h1>TEMP.</h1>
        <TempGauge temperature={gaugeData.temperature} barColour={"#3498db"}/>
        <h2>{gaugeData.temperature}ºC</h2>
      </div>
       <div >
          <h1>PRESSURE</h1>
          <PressureGauge rotation={rotation}/>
          <h2>{pressure}KPa</h2>
      </div>

    </div>

  );
  };


