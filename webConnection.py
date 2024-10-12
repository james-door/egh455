import redis
import pickle
import base64
import json
class webConnection:
    def __init__(self):
        self.r = redis.StrictRedis(host='localhost', port=6379, db=0)
    
    def sendVideoFeed(self, frame):
        
        image_pkl = pickle.dumps(frame)
        image_b64 = base64.b64encode(image_pkl).decode('utf-8')
        data = {'video': image_b64}
        video_feed_data = json.dumps(data)
        self.r.publish('video_feed', video_feed_data)

    def sendGasData(self,gasData, time):
        gasData["time"] = time
        self.r.publish('hazardous_gas',json.dumps(gasData))
    def sendIdentifiedTarget(self, target):
        self.r.publish('target_identified', json.dumps(target)
)



