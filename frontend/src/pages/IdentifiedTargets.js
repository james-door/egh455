import React, { useState, useEffect } from 'react';

const absoulutePath = "images/"; // For debugging, when running nginx use images/1.jpg

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

export default function IdentifiedTargets() {
  const [imageNumber, setImageNumber] = useState(0);
  const [identifiedImages, setIdentifiedImages] = useState([]);

  useEffect(() => {
    const fetchData = () => {
      fetch(`/data/identified`)
        .then((response) => response.json())
        .then((data) => {
          setIdentifiedImages(data);
          setImageNumber(data.length);
        })
        .catch((error) => {
          console.log(error);
        });
    };

    fetchData();
    const interval = setInterval(fetchData, 5000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="identified-targets">
      <div
        className="container"
        style={
          imageNumber > 1
            ? { justifyContent: 'flex-start' }
            : { justifyContent: 'center' }
        }
      >
        {imageNumber === 0 ? (
          <h1>No Identified Images</h1>
        ) : (
          identifiedImages.map((path, index) => (
            <div key={index} className="detected-image">
              <img src={`${absoulutePath}${path.detection_id}`} alt={`Detected ${path.detection_id}`} />
              <h2>
                {getDateFromUNIXTime(path.unix_time)}
                <br/>
                {path.detections}
                </h2>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
