import React, { useEffect } from 'react';

function App() {
  useEffect(() => {
    const eventSource = new EventSource('/data/target_identified');
    eventSource.onmessage = function(event) {
      console.log('New event:', event.data);
      // Play the notification sound or trigger any other action here
    //   new Notification('Server Event', {
    //     body: event.data,
    //   });
    };

    eventSource.onerror = function(err) {
      console.error('EventSource failed:', err);
      eventSource.close();
    };

    return () => {
      eventSource.close(); // Cleanup on component unmount
    };
  }, []);

  return (
    <div>
      <h1>Server-Sent Events Notification</h1>
    </div>
  );
}

export default App;
