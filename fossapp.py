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
import time


pool = redis.ConnectionPool(host='localhost', port=6379, db=0, max_connections=4)

app = Flask(__name__)
    


def getRandomImage():
    r = redis.Redis(connection_pool=pool)
    p = r.pubsub()
    p.subscribe('video_feed')
    image_buffer = np.random.randint(0,255,size=(712,712,3),dtype = "uint8")

    while(True):
      message = p.get_message(timeout=None)
      if message and message['type'] == 'message':
         data = json.loads(message['data'])
         image_pkl = base64.b64decode(data['video'])
         image_buffer = pickle.loads(image_pkl)
         
      success,encoded_image = cv2.imencode('.jpg', image_buffer)
    
      yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + encoded_image.tobytes() + b'\r\n')

def getRandomFloatData():
   reducingWindow = deque(maxlen=10)
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
        message = p.get_message(timeout=None)
        if message and message['type'] == 'message':
            data = json.loads(message['data'])

            reducingWindow.append(data['reducing'])
            oxidisingWindow.append(data['oxidising'])
            ammoniaWindow.append(data['ammonia'])
            
            time.append(data['time'])
            pressure = data['pressure']
            temperature = data['temperature']
            humidity = data['humidity']
            light = data['light']
            data = {'reducing': list(reducingWindow), 'oxidising' : list(oxidisingWindow),'ammonia' : list(ammoniaWindow),
                    'time' : list(time), 'pressure' : pressure, 'temperature' : temperature,
                    'humidity' : humidity, 'light' : light}
            yield f"data: {json.dumps(data)}\n\n"


def event_stream():
    r = redis.Redis(connection_pool=pool)
    p = r.pubsub()
    p.subscribe('target_identified')
    while True:
        message = p.get_message(timeout=None)
        if message and message['type'] == 'message':
            yield f'data: Notification from server at {time.time()}\n\n'


def getDetectedTarget():
    r = redis.Redis(connection_pool=pool)
    p = r.pubsub()
    p.subscribe('redis_identified_target')
    
    while True:
        message = p.get_message()
        if message and message['type'] == 'message':
            data = json.loads(message['data'])  # Parse the JSON data
    
            # sys.stdout.flush()
            yield f"data: {json.dumps(data)}\n\n"  # Properly serialize the data to JSON



    
@app.route('/data/hazardous_gas_data')
def hazardousGasDataFeed():
    response = Response(getRandomFloatData(), mimetype='text/event-stream')
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['X-Accel-Buffering'] = 'no'  
    return response
   
@app.route('/data')
def videoFeed():
  
    response = Response(getRandomImage(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['X-Accel-Buffering'] = 'no'  

    return response

@app.route('/data/log')
def dataLog():
    startTime = request.args.get('startTime')
    endTime = request.args.get('endTime')
    db = PayloadDataBase.PayloadDataBase()
    data = {'tableData':db.dataRead(startTime, endTime), 'earliestTime':db.earliestTime()}
    return json.dumps(data)

# @app.route('/data/latest_identified_target')
# def latestIdentifiedTarget():
#     time = request.args.get('time')
#     db = PayloadDataBase.PayloadDataBase()

#     data = db.getLatestIdentifiedImage(time)
#     return json.dumps(data)


@app.route('/data/target_identified')
def targetIdentified():
    
    response = Response(event_stream(), content_type='text/event-stream')
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['X-Accel-Buffering'] = 'no'  
    return response





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