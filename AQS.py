#!/usr/bin/env python3
"""
This code sets up a YOLO-based object detection pipeline using DepthAI,
and performs ArUco marker detection and pose estimation on the same frame.
"""
from pathlib import Path
import sys
import cv2
import depthai as dai
import numpy as np
import time
import argparse
import blobconverter
import math
import warnings
import datetime  # For timestamp logging
import webConnection

# Suppress libpng warnings from OpenCV
warnings.filterwarnings("ignore", category=UserWarning, module="cv2")

# Utility functions
def get_bbox_center(bbox):
    """Calculate the center of a bounding box."""
    x_center = (bbox[0] + bbox[2]) // 2
    y_center = (bbox[1] + bbox[3]) // 2
    return x_center, y_center

def calculate_angle(obj1_center, obj2_center):
    """Calculate the angle from base to needle in degrees, ensuring it is between 0 and 360.
    Adjusts for the image coordinate system where y increases downwards."""
    delta_x = obj1_center[0] - obj2_center[0]  # Swap order: base - needle
    delta_y = obj2_center[1] - obj1_center[1]  # Flipping the y-axis to correct orientation
    angle = math.atan2(delta_y, delta_x) * (180.0 / math.pi)  # Convert to degrees

    if angle < 0:
        angle += 360  # Ensure the angle is between 0 and 360 degrees

    return angle

def frame_norm(frame, bbox):
    """Normalize the bounding box coordinates with respect to the frame size."""
    norm_vals = np.full(len(bbox), frame.shape[0])
    norm_vals[::2] = frame.shape[1]
    return (np.clip(np.array(bbox), 0, 1) * norm_vals).astype(int)

# ArUco detection setup
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_250)
aruco_params = cv2.aruco.DetectorParameters()
aruco_detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)
camera_matrix = np.array([[640, 0, 320], [0, 640, 240], [0, 0, 1]], dtype=np.float32)
dist_coeffs = np.zeros((5, 1), dtype=np.float32)
marker_size = 0.05  # Marker size in meters (5 cm)
axis = np.float32([[marker_size, 0, 0], [0, marker_size, 0], [0, 0, marker_size], [0, 0, 0]]).reshape(-1, 3)

### Web Video Interface (WVI) connection ###
webCon = webConnection.webConnection()

# Pose estimation function using solvePnP
def estimate_pose(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    corners, ids, _ = aruco_detector.detectMarkers(gray)
    pos = (0,0,0)
    if ids is not None:
        cv2.aruco.drawDetectedMarkers(frame, corners, ids)
        for i, corner in enumerate(corners):
            obj_points = np.array([
                [-marker_size / 2, marker_size / 2, 0],
                [marker_size / 2, marker_size / 2, 0],
                [marker_size / 2, -marker_size / 2, 0],
                [-marker_size / 2, -marker_size / 2, 0]
            ], dtype=np.float32)

            retval, rvec, tvec = cv2.solvePnP(obj_points, corner, camera_matrix, dist_coeffs)

            if retval:
                rvec_str = "Rvec: [{:.2f}, {:.2f}, {:.2f}]".format(rvec[0][0], rvec[1][0], rvec[2][0])
                x_pos, y_pos, z_pos = tvec[0][0], tvec[1][0], tvec[2][0]
                pos = (x_pos, y_pos, z_pos)
                position_str = "Position (X, Y, Z): [{:.2f}, {:.2f}, {:.2f}]".format(x_pos, y_pos, z_pos)

                cv2.putText(frame, rvec_str, (10, 30 + i * 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
                cv2.putText(frame, position_str, (10, 50 + i * 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                # Print ArUco marker position and timestamp to console
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[{timestamp}] Detected ArUco marker ID {ids[i][0]} at position (X: {x_pos:.2f}, Y: {y_pos:.2f}, Z: {z_pos:.2f})")
                imgpts, _ = cv2.projectPoints(axis, rvec, tvec, camera_matrix, dist_coeffs)
                imgpts = np.int32(imgpts).reshape(-1, 2)
                frame = cv2.line(frame, tuple(imgpts[3]), tuple(imgpts[0]), (255, 0, 0), 2)
                frame = cv2.line(frame, tuple(imgpts[3]), tuple(imgpts[1]), (0, 255, 0), 2)
                frame = cv2.line(frame, tuple(imgpts[3]), tuple(imgpts[2]), (0, 0, 255), 2)



    return frame,pos, 

class YOLOPipeline:
    def __init__(self, model_path, input_size=(640, 640), num_classes=5):
        self.model_path = model_path
        self.W, self.H = input_size
        self.num_classes = num_classes
        self.confidence_threshold = 0.5
        self.iou_threshold = 0.5
        self.pipeline = None
        self.device = None
        self.anchors = [10.0, 13.0, 16.0, 30.0, 33.0, 23.0, 30.0, 61.0, 62.0, 45.0, 59.0, 119.0, 
                        116.0, 90.0, 156.0, 198.0, 373.0, 326.0]
        self.anchor_masks = {"side80": [0, 1, 2], "side40": [3, 4, 5], "side20": [6, 7, 8]}

    def create_pipeline(self):
        pipeline = dai.Pipeline()

        camRgb = pipeline.create(dai.node.ColorCamera)
        detectionNetwork = pipeline.create(dai.node.YoloDetectionNetwork)
        xoutRgb = pipeline.create(dai.node.XLinkOut)
        nnOut = pipeline.create(dai.node.XLinkOut)

        xoutRgb.setStreamName("rgb")
        nnOut.setStreamName("nn")

        camRgb.setPreviewSize(self.W, self.H)
        camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
        camRgb.setInterleaved(False)
        camRgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)
        camRgb.setFps(40)

        detectionNetwork.setConfidenceThreshold(self.confidence_threshold)
        detectionNetwork.setNumClasses(self.num_classes)
        detectionNetwork.setCoordinateSize(4)
        detectionNetwork.setBlobPath(self.model_path)
        detectionNetwork.setNumInferenceThreads(2)
        detectionNetwork.input.setBlocking(False)

        detectionNetwork.setAnchors(self.anchors)
        detectionNetwork.setAnchorMasks(self.anchor_masks)
        detectionNetwork.setIouThreshold(self.iou_threshold)

        camRgb.preview.link(detectionNetwork.input)
        detectionNetwork.passthrough.link(xoutRgb.input)
        detectionNetwork.out.link(nnOut.input)

        self.pipeline = pipeline

    def connect_device(self):
        if not self.pipeline:
            self.create_pipeline()

        self.device = dai.Device(self.pipeline)
        qRgb = self.device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
        qDet = self.device.getOutputQueue(name="nn", maxSize=4, blocking=False)
        return qRgb, qDet

class ObjectDetector:
    """Class to handle object detection and calculations of centers and angles."""
    def __init__(self, labels):
        self.labels = labels
        self.centers = {label: None for label in labels}

        # Define a color map for each label
        self.color_map = {
            "needle": (0, 255, 0),  # Green
            "base": (255, 0, 0),    # Blue
            "gauge": (0, 0, 255),   # Red
            "open": (255, 255, 0),  # Yellow
            "closed": (0, 255, 255) # Cyan
        }

    def process_detections(self, frame, detections):
        """Process detections, calculate object centers, and display them."""
        self.centers = {label: None for label in self.labels}
        angle = None
        detectedObjects = []
        for detection in detections:
            bbox = frame_norm(frame, (detection.xmin, detection.ymin, detection.xmax, detection.ymax))
            label = self.labels[detection.label]

            detectedObjects.append(label)

            # Calculate the center of the detected object and store it
            center = get_bbox_center(bbox)
            self.centers[label] = center

            # Get the current timestamp
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Print detected object information to console
            print(f"[{timestamp}] Detected {label} at position {center}")

            self.draw_label(frame, bbox, label, detection.confidence)

        # Calculate and display angle between needle and base if both are detected
        if self.centers["needle"] is not None and self.centers["base"] is not None:
            angle = calculate_angle(self.centers["needle"], self.centers["base"])
            cv2.putText(frame, f"Angle B->N: {angle:.2f} deg", (20, 40), cv2.FONT_HERSHEY_TRIPLEX, 0.7, (0, 255, 0), 2)


        return (frame, angle, detectedObjects)

    def draw_label(self, frame, bbox, label, confidence):
        """Draw bounding box and label on the frame with specific colors."""
        color = self.color_map.get(label, (255, 255, 255))  # Fetch the color from the color_map
        cv2.putText(frame, label, (bbox[0] + 10, bbox[1] + 20), cv2.FONT_HERSHEY_TRIPLEX, 0.5, color)
        cv2.putText(frame, f"{int(confidence * 100)}%", (bbox[0] + 10, bbox[1] + 40), cv2.FONT_HERSHEY_TRIPLEX, 0.5, color)
        cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)

class YOLOApp:
    """Main YOLO Application Class"""
    def __init__(self, model_path):
        self.labels = ["base", "closed", "gauge", "needle", "open"]
        self.detector = ObjectDetector(self.labels)
        self.yolo_pipeline = YOLOPipeline(model_path=model_path)
        self.webCon = webConnection.webConnection()
        self.qRgb = None
        self.qDet = None

    def initialize(self):
        """Initialize the pipeline and set up device connections."""
        self.qRgb, self.qDet = self.yolo_pipeline.connect_device()
    
    def process_frame(self):
        """Process one frame at a time."""
        inRgb = self.qRgb.get()
        inDet = self.qDet.get()

        if inRgb is not None:
            frame = inRgb.getCvFrame()
            frame, angle, labels = self.detector.process_detections(frame, inDet.detections)
            frame, pos = estimate_pose(frame)
            
            detections = []
            if "needle" in labels or "base" in labels or "gauge" in labels:
                detections.append("Gauge")
            if "open" in labels or "closed" in labels:
                detections.append("Valve")

            return {"frame" : frame , "pos" : pos, "angle" : angle, "detections" : detections}
            # frame = estimate_pose(frame)
            # self.webCon.sendVideoFeed(frame)
            # cv2.imshow("YOLO and ArUco", frame)

        # return cv2.waitKey(1) == ord('q')

    def renameDetection(self, detection):
        if detection == "needle" or detection == "base" or  detection == "gauge":
            return "Gauge"
        else:
            return "Valve"

    def cleanup(self):
        """Cleanup and close the application."""
        cv2.destroyAllWindows()

 