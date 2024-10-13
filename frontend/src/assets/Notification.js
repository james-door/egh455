import React, { useEffect, useState } from 'react';

const Notification = ({ message }) => {
  const [visible, setVisible] = useState(false);


  const showSystemNotification = (message) => {
      new Notification(message);
  };

  useEffect(() => {

    if (message) {
      setVisible(true);

      showSystemNotification(message);

      const timer = setTimeout(() => {
        setVisible(false);
      }, 3000);

      return () => clearTimeout(timer);
    }
  }, [message]);

  return (
    visible && (
      <div style={styles.notification}>
        <p>{message}</p>
      </div>
    )
  );
};

const styles = {
  notification: {
    position: 'fixed',
    top: '10px',
    left: '50%',
    transform: 'translateX(-50%)',
    backgroundColor: '#ffcc00',
    color: '#000',
    padding: '10px 20px',
    borderRadius: '5px',
    boxShadow: '0px 4px 6px rgba(0, 0, 0, 0.1)',
    zIndex: 1000,
  },
};

export default Notification;
