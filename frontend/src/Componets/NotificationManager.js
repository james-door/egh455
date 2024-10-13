import React, { useEffect, useState } from 'react';

function NotificationManager() {  // Renamed from App to NotificationManager
  const [notification, setNotification] = useState('');

  useEffect(() => {
    const eventSource = new EventSource('/data/target_identified');

    eventSource.onmessage = function(event) {
      
      const detectionMessage = event.data;
      const value = JSON.parse(detectionMessage)
      console.log(value.detection)
      if(value.detection !== "None")
      {

        const message = new SpeechSynthesisUtterance();
        message.text = value.detection;

        const speechSynthesis = window.speechSynthesis;
        speechSynthesis.speak(message);  

        setNotification(value.detection);

        setTimeout(() => {
          setNotification('');
        }, 5000);
    }
    };

    eventSource.onerror = function(err) {
      console.error('EventSource failed:', err);
      eventSource.close();
    };

    return () => {
      eventSource.close(); 
    };
  }, []);

  return (
    <>
      {notification && (
        <div style={{
          position: 'fixed',
          top: '10px',
          right: '10px',
          backgroundColor: '#FFDF32',
          color: '#000000',
          padding: '10px 20px',
          borderRadius: '5px',
          zIndex: 1000
        }}>
          {notification}
        </div>
      )}
    </>
  );
}

export default NotificationManager;
