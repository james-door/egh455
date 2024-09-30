import sys
from flask import Flask, Response, request
import numpy as np
import cv2
import json
import redis
import base64
import pickle
import random
from collections import deque
import PayloadDataBase

pool = redis.ConnectionPool(host='localhost', port=6379, db=0, max_connections=100)

app = Flask(__name__)
    


def getRandomImage():
    r = redis.Redis(connection_pool=pool)
    p = r.pubsub()
    p.subscribe('video_feed')
    image_buffer = np.random.randint(0,255,size=(712,712,3),dtype = "uint8")

    while(True):
      message = p.get_message()
      if message and message['type'] == 'message':
         data = json.loads(message['data'])
         image_pkl = base64.b64decode(data['video'])
         image_buffer = pickle.loads(image_pkl)
         
      success,encoded_image = cv2.imencode('.jpg', image_buffer)

      yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + encoded_image.tobytes() + b'\r\n')

def getRandomFloatData():
   window = deque(maxlen=10)
   oxidisingWindow = deque(maxlen=10)
   ammoniaWindow = deque(maxlen=10)

   time = deque(maxlen=10)
   pressure = 0
   temperature =0
   humidity = 0
   light = 0
   r = redis.Redis(connection_pool=pool)
   p = r.pubsub()
   p.subscribe('hazardous_gas')
   while True:
        message = p.get_message()
        if message and message['type'] == 'message':
            data = json.loads(message['data'])

            window.append(data['co2'])
            oxidisingWindow.append(data['oxidising'])
            ammoniaWindow.append(data['ammonia'])
            
            time.append(data['time'])
            pressure = data['pressure']
            temperature = data['temperature']
            humidity = data['humidity']
            light = data['light']
        data = {'reducing': list(window), 'oxidising' : list(oxidisingWindow),'ammonia' : list(ammoniaWindow),
                'time' : list(time), 'pressure' : pressure, 'temperature' : temperature,
                'humidity' : humidity, 'light' : light}
        print(f"Received data gas: {data}")     # Debugging line to check if data is being received
        print()
        yield f"data: {json.dumps(data)}\n\n"


def getDetectedTarget():
    r = redis.Redis(connection_pool=pool)
    p = r.pubsub()
    p.subscribe('redis_identified_target')
    
    while True:
        message = p.get_message()
        if message and message['type'] == 'message':
            data = json.loads(message['data'])  # Parse the JSON data
    
            yield f"data: {json.dumps(data)}\n\n"  # Properly serialize the data to JSON




    
@app.route('/data/hazardous_gas_data')
def hazardousGasDataFeed():
    return Response(getRandomFloatData(), mimetype='text/event-stream')


   
@app.route('/data')
def videoFeed():
  return Response(getRandomImage(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/data/log')
def dataLog():
    startTime = request.args.get('startTime')
    endTime = request.args.get('endTime')
    db = PayloadDataBase.PayloadDataBase()
    data = {'tableData':db.dataRead(startTime, endTime), 'earliestTime':db.earliestTime()}
    return json.dumps(data)

@app.route('/data/latest_identified_target')
def latestIdentifiedTarget():
    time = request.args.get('time')
    db = PayloadDataBase.PayloadDataBase()

    data = db.getLatestIdentifiedImage(time)
    return json.dumps(data)




@app.route('/data/identified')
def identifiedImagesLog():
    db = PayloadDataBase.PayloadDataBase()
    identified = db.getIdentifiedImages()
    return json.dumps(identified)


# @app.route('/data/flask_identified_target')
# def targetIdentified():
#     return Response(getDetectedTarget(), mimetype='text/event-stream')








    





def main():
    app.run(host='0.0.0.0',debug=True)

if __name__== "__main__":
    main()