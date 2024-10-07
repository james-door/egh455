import {React,useState, useEffect} from "react";
import { Line } from "react-chartjs-2";
import Chart from "chart.js/auto";
import { CategoryScale, elements } from "chart.js";

Chart.register(CategoryScale);

function getFormattedTimeFromUNIXTime(unixTime) {

  const date = new Date(unixTime * 1000); 
  const minutes = date.getMinutes().toString().padStart(2, '0'); 
  const seconds = date.getSeconds().toString().padStart(2, '0'); 
  const miliseconds = date.getMilliseconds().toString().padStart(3, '0'); 

  const formattedDateTime = `${minutes}:${seconds}.${miliseconds}`;
  return formattedDateTime;
}

function getDateFromUNIXTime(unixTime) {

  const date = new Date(unixTime * 1000); 
  const year = date.getFullYear();
  const month = date.getMonth() + 1;
  const day = date.getDate();
  let hours = date.getHours();

  const ampm = hours >= 12 ? 'PM' : 'AM';
  hours = hours % 12 || 12; 

  const formattedDateTime = `${day}/${month}/${year} at ${hours}${ampm}`;
  return formattedDateTime;
}

export default function LineGraph({ chartData, name })
{
  const [activeGraph, setActiveGraph] = useState("Reducing");


  function changeGraph(e)
  {
    setActiveGraph(e.target.textContent)
  }
  
  function plotSwitcher()
  {
    const pathNames = ["Reducing", "Oxidising", "Ammonia"]
    const buttons = pathNames.map((path) => {
        const buttonStatus = (path === activeGraph) ? "active" : "inactive";
        return(
                <button className={buttonStatus} onClick={changeGraph} key={path}>{path}</button>
        );
      });
      return(
        <div className="navbar-style" style={{height : "0px", minHeight : "0px"}}>
          {buttons}
        </div>
      )
  }
  function graphData()
  {
    var gasData = null


    if(activeGraph == "Reducing")
      gasData = chartData.reducing
    else if(activeGraph == "Oxidising")
      gasData = chartData.oxidising
    else
      gasData = chartData.ammonia
    return({
    labels:  chartData.time.map(element => {return getFormattedTimeFromUNIXTime(element)}),
    datasets: [
      {
        data: gasData,
        backgroundColor: 'rgba(255, 0, 0, 0)',
        borderColor: 'rgba(255, 0, 0, 1.0)', 
        borderWidth: 2, 
        fill: true, 
      }
    ]
    

    })
  }

    return(
<div className="linegraph-container"> 
  <div className="linegraph-style">
    <div className="plot-switcher">
            {plotSwitcher()}
    </div>
    <Line
      data={graphData()}
      options={{

          scales: {
            x: {
              title: {
                display: true,
                text: 'Time (Minutes : Seconds. Miliseconds)'
              }
            },
            y: {
              title: {
                display: true,
                text: 'Gas Data (Units)'
              }
            }
          },
        plugins: {
          title: {
            display: true,
            text: activeGraph + ` - ${getDateFromUNIXTime(chartData.time.pop())}`
          },
          legend: {
            display: false
          }
        }
      }}
    />
    </div>
  </div>

  );
}



