import sqlite3
import time
import datetime
import cv2
import os

import stat
import pwd
import grp
from functools import reduce

tableName = "payloadData"

# dataBaseAbsoloutePath = "/var/www/egh455/payloadDB.sqlite3"
dataBaseAbsoloutePath = "/var/www/egh455/database/payloadDB.sqlite3"
detectedImagePath = "/var/www/egh455/database/detectedImages"


# create and pass data to redis
class PayloadDataBase:
    def __init__(self):        

        db_directory = os.path.dirname(dataBaseAbsoloutePath)
        os.makedirs(db_directory, exist_ok=True)
        self.set_permissions(db_directory)
        self.conn=sqlite3.connect(dataBaseAbsoloutePath)
        
        QueryTables = """SELECT name FROM sqlite_master  
        WHERE type='table';"""
        createTable = f'''
                    CREATE TABLE {tableName} (
                    unix_time INTEGER NOT NULL,
                    pressure FLOAT,
                    temperature FLOAT,
                    humidity FLOAT,
                    light FLOAT,
                    oxidising FLOAT,
                    reducing FLOAT,
                    ammonia FLOAT,
                    detections TEXT,
                    detection_id TEXT
                    );
                    '''
        self.cur = self.conn.cursor()
        


        self.cur.execute(QueryTables)
        tables = [table[0] for table in self.cur.fetchall()]
        if tableName not in tables:
            self.cur.execute(createTable)
          
            print("Create new table.")

    def __del__(self):
        self.conn.close()

    def set_permissions(self, path):
        uid = pwd.getpwnam('455G16').pw_uid
        gid = grp.getgrnam('www-data').gr_gid
        os.chown(path, uid, gid)
        os.chmod(path, stat.S_IRWXU | stat.S_IRWXG)
    def earliestTime(self):
        writeQuery = f"""
                         SELECT MIN(unix_time) from {tableName}
                         """
        self.cur.execute(writeQuery)

        result = self.cur.fetchone()
        return result[0]

    def dataInsert(self, unixTime, pressure, temperature, humidity, light, oxidising,
                    reducing, ammonia, detections, image):
        detectionID = None
        if detections:
            countQuery = f"SELECT COUNT(*) FROM {tableName} WHERE detections != 'None'"
            self.cur.execute(countQuery)
            nDetections = self.cur.fetchone()[0]

            detectionID = f"{nDetections +1}.jpg"

            os.makedirs(detectedImagePath, exist_ok=True)
            cv2.imwrite(f"{detectedImagePath}/{detectionID}",image)
            detections = reduce(lambda x, y: x + " " + y, detections)
 

        writeQuery = f"INSERT INTO {tableName} VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        data = (
            int(unixTime), pressure, temperature, humidity, light, oxidising, 
            reducing, ammonia, detections, detectionID)
        
        self.cur.execute(writeQuery, data)
        self.conn.commit()

    def dataRead(self, startTime, endTime):
        writeQuery = f"""
                        SELECT * FROM {tableName} WHERE unix_time >= {startTime} AND unix_time <= {endTime}
                         """
        self.cur.execute(writeQuery)
        column_names = [description[0] for description in self.cur.description]
        rows = self.cur.fetchall()

        result = [dict(zip(column_names, row)) for row in rows]

        return result
    
    def getIdentifiedImages(self):
        query = f"SELECT detection_id, detections FROM {tableName} WHERE detection_id IS NOT NULL"
        self.cur.execute(query)
        rows = self.cur.fetchall() 
        column_names = [description[0] for description in self.cur.description]
        result = [dict(zip(column_names, row)) for row in rows]
        return result
    

    def getLatestIdentifiedImage(self, unix_time):
        query = f"SELECT unix_time, detections FROM {tableName} WHERE detections IS NOT NULL AND unix_time >={unix_time - 1000}"
        self.cur.execute(query)
        rows = self.cur.fetchall() 
        column_names = [description[0] for description in self.cur.description]
        result = [dict(zip(column_names, row)) for row in rows]
        return result

    def debugDisplay(self, data):
        for row in data:
            print(f"{datetime.datetime.fromtimestamp(row['unix_time'])}, \
                   Pressure : {row['pressure']}, Humidity : {row['humidity']} \
                    Temperature : {row['temperature']}, Light : {row['light']}")
            



