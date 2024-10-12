import React, { useState, useEffect } from 'react';

const absoulutePath = "images/"; // For debugging, when running nginx use images/1.jpg



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
              <h2>{path.detections}</h2>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
