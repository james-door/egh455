import {React,useState, useEffect} from "react";
import { Line } from "react-chartjs-2";
import Chart from "chart.js/auto";
import { CategoryScale } from "chart.js";

Chart.register(CategoryScale);





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
    labels: chartData.time,
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
                text: 'Time (Units)'
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
            text: activeGraph
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



