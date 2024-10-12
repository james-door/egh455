import React, { useEffect } from "react";

export default function DetectionNotification() {
    useEffect(() => {

        fetch(`/data/latest_identified_target?time=${Date.now() / 1000}`)
        .then((response) => response.json())
        .then((data) => {
            console.log(data)
        })
        

        const message = new SpeechSynthesisUtterance();
        message.text = "Hello World!";
        const speechSynthesis = window.speechSynthesis;

        const speakMessage = () => {
            speechSynthesis.speak(message);
        };

        const interval = setInterval(() => {
            speakMessage();
        }, 1000);

        return () => {
            clearInterval(interval); 
            speechSynthesis.cancel(); 
        };
    }, []); 

    return (
        <div>
            <p>Speech notification should play: "Hello World!" every 2 seconds</p>
        </div>
    );
}
