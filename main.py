import redis
import json
import numpy as np
import pickle
import base64
import random
import time
import sys
import threading
import cv2
import PayloadDataBase
import os


r = redis.StrictRedis(host='localhost', port=6379, db=0)



randomDetections = ['Valve Open', 'Valve Closed', None]

def generateDataBaseData():
    db = PayloadDataBase.PayloadDataBase()
    while(True):
        detection = random.choices(randomDetections, weights=[0.1, 0.1, 0.8])[0]
        image = None
        # r.publish('redis_identified_target', json.dumps({'detection': detection}))

        if detection:
            image = np.random.randint(0,255,size=(712,712,3),dtype = "uint8")




        db.dataInsert(time.time(),random.random() * 2000,random.random()*100,
                      int(random.random() * 100),random.random()*100,
                      random.random()*2000, random.random() * 2000, random.random() * 2000,
                      detection, image)
            
        time.sleep(1)



def main():
    currentTime = 0

    dbThread = threading.Thread(target=generateDataBaseData)
    
    
    dbThread.start()
    while(True):

        # Read Image
        image = np.random.randint(0,255,size=(712,712,3),dtype = "uint8")
        # Read Presssure
        pressure = 50*random.random() + 50


        image_pkl = pickle.dumps(image)
        image_b64 = base64.b64encode(image_pkl).decode('utf-8')
        data = {'video': image_b64}
        video_feed_data = json.dumps(data)


        hazardous_gas_data = {'co2' : random.random()*50, 'oxidising' : random.random()*50 +50 ,
                              'ammonia' : random.random()*50 + 100, 'time' : currentTime, 
                            'pressure' : int(random.random()*2000), 'temperature' : int(random.random()*100),
                            'humidity' : int(random.random() * 100), 'light' : int(random.random() * 100)
                              }

        r.publish('video_feed', video_feed_data)
        r.publish('hazardous_gas',json.dumps(hazardous_gas_data))



        currentTime += 1
        time.sleep(0.1)


    dbThread.join()



if __name__ == "__main__":
    sys.exit(main())



