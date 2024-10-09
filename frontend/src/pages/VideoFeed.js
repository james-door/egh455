import React from 'react';


function VideoFeed() {

  return (
    <div className="videofeed-style">
    <img
      src={"/data"}
      alt="Detected Image"
      onError={(e) => {
        e.target.onerror = null;
        e.target.style.display = 'none'; 
        e.target.insertAdjacentHTML('afterend', '<h1>No Video Feed Available</h1>'); 
      }}
    />   
 </div>
  );
}

export default VideoFeed;
