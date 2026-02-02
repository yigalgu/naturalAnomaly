from ultralytics import YOLO
import cv2
from pathlib import Path
from typing import List, Dict
import json

class VideoProcessor:
    """Process videos to detect and track vehicles"""
    
    def __init__(self, model_name: str = "yolov8n.pt"):
        """Initialize YOLO model"""
        self.model = YOLO(model_name)
        # Vehicle classes in COCO dataset
        self.vehicle_classes = {
            2: "car",
            3: "motorcycle", 
            5: "bus",
            7: "truck"
        }
    
    def process_video(self, video_path: Path) -> Dict:
        """
        Process video and track vehicles using YOLO tracking
        Returns statistics, detections, and vehicle trajectories
        """
        cap = cv2.VideoCapture(str(video_path))
        
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0
        
        detections = []
        trajectories = {}  # track_id -> trajectory data
        frame_count = 0
        
        print(f"Processing video: {video_path.name}")
        print(f"Total frames: {total_frames}, FPS: {fps}, Duration: {duration:.2f}s")
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Run YOLO tracking every 10 frames (for speed)
            if frame_count % 10 == 0:
                # Use track() instead of simple detection - persist=True maintains track IDs
                results = self.model.track(frame, persist=True, verbose=False)
                
                for result in results:
                    boxes = result.boxes
                    for box in boxes:
                        cls = int(box.cls[0])
                        conf = float(box.conf[0])
                        
                        # Only track vehicles with confidence > 0.5
                        if cls in self.vehicle_classes and conf > 0.5:
                            # Get track ID if available
                            track_id = int(box.id[0]) if box.id is not None else None
                            
                            # Get bounding box coordinates
                            bbox = box.xyxy[0].tolist()
                            center_x = (bbox[0] + bbox[2]) / 2
                            center_y = (bbox[1] + bbox[3]) / 2
                            timestamp = frame_count / fps
                            
                            detection = {
                                "frame": frame_count,
                                "timestamp": timestamp,
                                "track_id": track_id,
                                "class_id": cls,
                                "class_name": self.vehicle_classes[cls],
                                "confidence": conf,
                                "bbox": bbox
                            }
                            detections.append(detection)
                            
                            # Build trajectories for tracked vehicles
                            if track_id is not None:
                                if track_id not in trajectories:
                                    trajectories[track_id] = {
                                        "track_id": track_id,
                                        "class_name": self.vehicle_classes[cls],
                                        "positions": [],
                                        "timestamps": [],
                                        "frames": []
                                    }
                                
                                trajectories[track_id]["positions"].append((center_x, center_y))
                                trajectories[track_id]["timestamps"].append(timestamp)
                                trajectories[track_id]["frames"].append(frame_count)
            
            frame_count += 1
            
            # Progress indicator
            if frame_count % 100 == 0:
                progress = (frame_count / total_frames) * 100
                print(f"Progress: {progress:.1f}%")
        
        cap.release()
        
        # Calculate statistics using unique track IDs
        stats = self._calculate_statistics(detections, trajectories, duration)
        
        return {
            "video_info": {
                "filename": video_path.name,
                "duration": duration,
                "fps": fps,
                "total_frames": total_frames
            },
            "detections": detections,
            "trajectories": trajectories,
            "statistics": stats
        }
    
    def _calculate_statistics(self, detections: List[Dict], trajectories: Dict, duration: float) -> Dict:
        """Calculate statistics from detections and trajectories"""
        if not detections:
            return {
                "total_vehicles": 0,
                "vehicles_per_hour": 0,
                "vehicle_types": {},
                "segments": [0] * 10
            }
        
        # Count unique vehicles based on track IDs
        unique_track_ids = set()
        for det in detections:
            if det.get("track_id") is not None:
                unique_track_ids.add(det["track_id"])
        
        # Use unique track IDs count if available, otherwise fallback to old method
        total_vehicles = len(unique_track_ids) if unique_track_ids else len(detections) // 10
        
        # Vehicles per hour
        hours = duration / 3600 if duration > 0 else 1
        vehicles_per_hour = total_vehicles / hours
        
        # Count by type (count unique track_ids per type)
        vehicle_types = {}
        for track_id, traj in trajectories.items():
            vtype = traj["class_name"]
            vehicle_types[vtype] = vehicle_types.get(vtype, 0) + 1
        
        # Find busiest segment (divide video into 10 segments)
        segments = [0] * 10
        for det in detections:
            segment_idx = min(int((det["timestamp"] / duration) * 10), 9) if duration > 0 else 0
            segments[segment_idx] += 1
        
        busiest_segment = segments.index(max(segments)) if max(segments) > 0 else 0
        
        return {
            "total_vehicles": total_vehicles,
            "vehicles_per_hour": round(vehicles_per_hour, 2),
            "vehicle_types": vehicle_types,
            "segments": segments,
            "busiest_segment": {
                "segment_number": busiest_segment,
                "start_time": (busiest_segment * duration / 10) if duration > 0 else 0,
                "end_time": ((busiest_segment + 1) * duration / 10) if duration > 0 else 0,
                "vehicle_count": segments[busiest_segment]
            }
        }
