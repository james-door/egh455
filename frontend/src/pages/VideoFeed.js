import React, { useEffect, useRef } from 'react';

function VideoFeed() {
  const imgRef = useRef(null);

  useEffect(() => {
    return () => {
      if (imgRef.current) {
        console.log("DISMOUNT")
        imgRef.current.src = '';
      }
    };
  }, []); 

  return (
    <div className="videofeed-style">
      <img
        ref={imgRef}
        src="/data"
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
