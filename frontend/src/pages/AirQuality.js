import {React,useState, useEffect} from "react";
import LineGraph from "../Componets/LineGraph";
import Gauge from "../Componets/Gauge"
import NavBar from "../Componets/Navbar"
    
const defaultValue = {
  graphData :{
    time : [0,0,0,0,0,0,0,0,0,0],
    reducing: [0,0,0,0,0,0,0,0,0,0],
    oxidising: [0,0,0,0,0,0,0,0,0,0], 
    ammonia : [0,0,0,0,0,0,0,0,0,0]
  },
  gaugeData: {
  pressure : 0,
  temperature : 0,
  humidity : 0,
  light : 0
  }
}



export default function AirQuality()
{
  const [gasData, setGasData] = useState(defaultValue);
  
  useEffect(() => {
    const eventSource = new EventSource('/data/hazardous_gas_data');
    eventSource.onmessage = (event) => {
      const data =JSON.parse(event.data)
      setGasData(
        {
          graphData: {
                      time : data.time,
                      reducing: data.reducing,
                      oxidising: data.oxidising, 
                      ammonia : data.ammonia
                    },
          gaugeData: {
            pressure : data.pressure,
            temperature : data.temperature,
            humidity : data.humidity,
            light : data.light
          }
        }
    );
    };

    return () => {
      eventSource.close();
    };
  }, []);

    
    return(
    <div className="airquality-style">    
      <LineGraph chartData={gasData.graphData} name={"Carbon Dioxide"}/>
      <Gauge gaugeData={gasData.gaugeData}/>
    </div>
    

)
}


