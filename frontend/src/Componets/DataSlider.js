import {React, useEffect, useState} from "react";


function getDateFromUNIXTime(unixTime) {
    const date = new Date(unixTime * 1000); 
    const year = date.getFullYear();
    const month = date.getMonth() + 1;
    const day = date.getDate();

    // Convert to 12-hour format
    let hours = date.getHours();
    const minutes = date.getMinutes().toString().padStart(2, '0'); // Ensures 2 digits for minutes
    const seconds = date.getSeconds().toString().padStart(2, '0'); // Ensures 2 digits for seconds
    const ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12 || 12; // Converts 0 (midnight) or 13-23 to 12-hour format

    const formattedDateTime = `${day}/${month}/${year} ${hours}:${minutes}:${seconds} ${ampm}`;
    return formattedDateTime;
}



export default function DataSlider({minTime, maxTime, onChange}) {
    const [slider1Value, setSlider1Value] = useState(minTime);
    const [slider2Value, setSlider2Value] = useState(maxTime);
    
    var minGap = 0;

    useEffect(() => {
        setSlider1Value(minTime)
        setSlider2Value(maxTime)
        onChange(slider1Value,slider2Value)
    }, [minTime]); 



    function slideOne(e) {
        var newValue = e.target.value
        if (parseInt(slider2Value) - parseInt(e.target.value) <= minGap) 
            setSlider1Value = parseInt(slider2Value) - minGap;
        else 
            newValue = e.target.value
        setSlider1Value(newValue)
        onChange(newValue,slider2Value)
     }
     function slideTwo(e) {
        var newValue = null
        if (parseInt(e.target.value) - parseInt(slider1Value) <= minGap) 
            newValue= parseInt(slider1Value) + minGap;
        else
            newValue = e.target.value

        setSlider2Value(newValue)
        onChange(slider1Value,newValue)

      }


      const trackStyle = {
        background: `linear-gradient(to right, #dadae5 ${((slider1Value - minTime) / (maxTime - minTime)) * 100}% , 
          #3264fe ${((slider1Value - minTime) / (maxTime - minTime)) * 100}% , 
          #3264fe ${((slider2Value - minTime) / (maxTime - minTime)) * 100}%, 
          #dadae5 ${((slider2Value - minTime) / (maxTime - minTime) ) * 100}%)`
      }
      

  return (
    <div className="dataslider-style">
        <div className="values">
            {getDateFromUNIXTime(slider1Value)}
            <br/>
            {getDateFromUNIXTime(slider2Value)}
        </div>

        <div className="container">
            <div className="slider-track" style={trackStyle}></div>
            <input type="range" min={minTime} max={maxTime} value={slider1Value} id="slider-1" onChange={slideOne}/>
            <input type="range" min={minTime} max={maxTime} value={slider2Value} id="slider-2" onChange={slideTwo}/>
        </div>

    </div>
  );
}
