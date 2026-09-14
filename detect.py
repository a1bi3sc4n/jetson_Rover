from ultralytics import YOLO
import torch


class ObjectDetector:
    def __init__(self, model_path="yolov8n.engine"):
        self.model = YOLO(model_path)
        self.device = "cuda"

    def detect(self, source, conf=0.5):
        results = self.model.track(source, conf=conf, device=self.device, persist=True)
        
        return results