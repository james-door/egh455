import GasCollection
import st7735
from fonts.ttf import RobotoMedium as UserFont
from PIL import Image, ImageDraw, ImageFont
import os
import argparse
import AQS
import webConnection
import PayloadDataBase

from threading import Thread
from gpiozero import Servo
import time
import cv2
from datetime import datetime, timedelta

def drill():
    servo_pin = 13
    servo = Servo(servo_pin)
    servo.value = 1.0
    time.sleep(44.5)  # Spin for 2 seconds
    servo.value = -1.0  # Set servo to anticlockwise direction with specific speed
    time.sleep(44.5)  # Spin for 2 seconds
    servo.value = 0  # Stop the servo
    servo.detach()  # Stop the servo


if __name__ == "__main__":


    

    gd = GasCollection.GasCollection()
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--model", help="Provide model path for inference", default='model/best_openvino_2022.1_6shave.blob', type=str)
    args = parser.parse_args()
    yolo_app = AQS.YOLOApp(model_path=args.model)
    yolo_app.initialize()
    webCon = webConnection.webConnection()

    triggeredDrill = False
    drillThread = Thread(target=drill)
    db = PayloadDataBase.PayloadDataBase()
    
    lastTime = time.time()
    while(True):
        currentTime = time.time()
        data = yolo_app.process_frame()

        detections = data["detections"] if data["detections"] else None
        
        if data["angle"]:
            print("Angle: ",data["angle"])
            
        if not triggeredDrill and data["angle"] and data["angle"] > 175:
            print("START DRILL.")
            triggeredDrill = True
            # drillThread.start()

        gasData = gd.getData()
        gd.updateLCD(gasData, data["frame"])
        webCon.sendVideoFeed(data["frame"])
        webCon.sendGasData(gasData, currentTime)

        if currentTime - lastTime > 5 or detections: # Every 5 seconds
            webCon.sendIdentifiedTarget({"test" : 12})
            # db.dataInsert(currentTime,gasData["pressure"],gasData["temperature"],
            # gasData["humidity"],gasData["light"],gasData["oxidising"],
            # gasData["reducing"],gasData["ammonia"],detections,data["frame"])
            # lastTime = currentTime
