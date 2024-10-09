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
# import PayloadDataBase
import os
from datetime import datetime, timedelta


r = redis.StrictRedis(host='localhost', port=6379, db=0)



# randomDetections = ['Valve Open', 'Valve Closed', None]

# def generateDataBaseData():
#     db = PayloadDataBase.PayloadDataBase()
#     while(True):
#         detection = random.choices(randomDetections, weights=[0.1, 0.1, 0.8])[0]
#         image = None
#         # r.publish('redis_identified_target', json.dumps({'detection': detection}))

#         if detection:
#             image = np.random.randint(0,255,size=(712,712,3),dtype = "uint8")




#         db.dataInsert(time.time(),random.random() * 2000,random.random()*100,
#                       int(random.random() * 100),random.random()*100,
#                       random.random()*2000, random.random() * 2000, random.random() * 2000,
#                       detection, image)
            
#         time.sleep(1)


def main():
    # dbThread = threading.Thread(target=generateDataBaseData)
    # dbThread.start()

    
    count = 0
    while(True):
        currentTime = (datetime.now() - timedelta(seconds=1)).strftime("%H:%M:%S.%f")[:-3]
        image = np.ones((712,712,3)) *255
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 3
        font_color = (0, 0, 0)  
        thickness = 2
        position = (10, 350)  
        cv2.putText(image, currentTime, position, font, font_scale, font_color, thickness, lineType=cv2.LINE_AA)
        image_pkl = pickle.dumps(image)
        image_b64 = base64.b64encode(image_pkl).decode('utf-8')
        data = {'video': image_b64}
        video_feed_data = json.dumps(data)
        r.publish('video_feed', video_feed_data)


        # hazardous_gas_data = {'co2' :count, 'oxidising' : count,
        #                       'ammonia' : count, 'time' : time.time(), 
        #                     'pressure' : count, 'temperature' :count,
        #                     'humidity' : count, 'light' : count
        #                       }


        count += 1

        hazardous_gas_data = {'co2' : random.random()*50, 'oxidising' : random.random()*50 +50 ,
                              'ammonia' : random.random()*50 + 100, 'time' :time.time(), 
                            'pressure' : int(random.random()*2000), 'temperature' : int(random.random()*100),
                            'humidity' : int(random.random() * 100), 'light' : int(random.random() * 100)
                              }

        r.publish('hazardous_gas',json.dumps(hazardous_gas_data))





    # dbThread.join()



if __name__ == "__main__":
    sys.exit(main())



