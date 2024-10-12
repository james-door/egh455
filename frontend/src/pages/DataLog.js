import {React,useState, useEffect} from "react";
import DataSlider from "../Componets/DataSlider";
import DataTable from "../Componets/DataTable";



export default function DataLog()
{

  const handleSliderChange = (lowValue, highValue) => {

    fetch(`/data/log?startTime=${lowValue}&endTime=${highValue}`)
      .then((response) => response.json())
      .then((data) => {
        setLogData(data.tableData);
        setEarliestTime(data.earliestTime);
  
      })
      .catch((error) => {
        console.log(error);
      });
  };

    const [logData, setLogData] = useState(null);
    const [earliestTime, setEarliestTime] = useState(Math.floor(Date.now() / 1000) - 1000)




    return(
    <div className="datatable-style">
        <DataSlider minTime={earliestTime} maxTime={Math.floor(Date.now() / 1000)} onChange={handleSliderChange}/>        
         { logData ? <DataTable data={logData}/> : <h2>Loading...</h2> }
    </div>


)
}