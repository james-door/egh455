# import GasCollection
import st7735
from fonts.ttf import RobotoMedium as UserFont
from PIL import Image, ImageDraw, ImageFont
import os
import argparse
import AQS
import webConnection
from threading import Thread
from gpiozero import Servo
from time import sleep



def drill():
    servo_pin = 13
    servo = Servo(servo_pin)
    servo.value = 1.0
    sleep(60)  # Spin for 2 seconds
    servo.value = -1.0  # Set servo to anticlockwise direction with specific speed
    sleep(60)  # Spin for 2 seconds
    servo.value = 0  # Stop the servo
    servo.detach()  # Stop the servo





if __name__ == "__main__":


    

    # gd = GasCollection.GasCollection()
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--model", help="Provide model path for inference", default='model/best_openvino_2022.1_6shave.blob', type=str)
    args = parser.parse_args()
    yolo_app = AQS.YOLOApp(model_path=args.model)
    yolo_app.initialize()
    webCon = webConnection.webConnection()

    triggeredDrill = False
    drillThread = Thread(target=drill)

    while(True):
        data = yolo_app.process_frame()

        # if(not triggeredDrill ): # and data["angle"] and data["angle"] > 180
        #     triggeredDrill = True
        #     drillThread.start()
        webCon.sendVideoFeed(data["frame"])
        # gasData = gd.getData()
        # webCon.sendGasData(gasData)