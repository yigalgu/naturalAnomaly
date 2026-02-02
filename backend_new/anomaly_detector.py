from typing import Dict, List, Optional
from dataclasses import dataclass, field
import math


@dataclass
class Anomaly:
    """Represents a detected anomaly in the video"""
    anomaly_type: str      # "stopped", "speeding", "spike"
    timestamp: float
    severity: str          # "low", "medium", "high"
    description: str
    track_id: Optional[int] = None
    metadata: Dict = field(default_factory=dict)


class AnomalyDetector:
    """Detect anomalies in vehicle trajectories and traffic patterns"""
    
    def __init__(self, 
                 stop_threshold_px: int = 20,
                 stop_duration_sec: float = 3.0,
                 speed_threshold_px: int = 200,
                 spike_multiplier: float = 3.0):
        """
        Initialize anomaly detector with thresholds
        
        Args:
            stop_threshold_px: Maximum movement in pixels to consider vehicle stopped
            stop_duration_sec: Minimum duration for stopped vehicle anomaly
            speed_threshold_px: Minimum pixel movement between frames for high speed
            spike_multiplier: Multiplier for traffic spike detection
        """
        self.stop_threshold_px = stop_threshold_px
        self.stop_duration_sec = stop_duration_sec
        self.speed_threshold_px = speed_threshold_px
        self.spike_multiplier = spike_multiplier
    
    def detect_stopped_vehicle(self, trajectory: Dict) -> Optional[Anomaly]:
        """
        Detect if a vehicle stopped for an unusually long time
        
        Args:
            trajectory: Vehicle trajectory with positions, timestamps, frames
            
        Returns:
            Anomaly object if stopped vehicle detected, None otherwise
        """
        positions = trajectory.get("positions", [])
        timestamps = trajectory.get("timestamps", [])
        track_id = trajectory.get("track_id")
        
        if len(positions) < 2 or len(timestamps) < 2:
            return None
        
        # Check for periods where vehicle barely moves
        for i in range(len(positions) - 1):
            # Calculate distance between consecutive positions
            x1, y1 = positions[i]
            x2, y2 = positions[i + 1]
            distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            
            # If distance is very small, check duration
            if distance < self.stop_threshold_px:
                # Find how long the vehicle stayed in roughly the same position
                stopped_duration = 0
                j = i
                while j < len(positions) - 1:
                    x1, y1 = positions[j]
                    x2, y2 = positions[j + 1]
                    dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                    
                    if dist < self.stop_threshold_px:
                        stopped_duration = timestamps[j + 1] - timestamps[i]
                        j += 1
                    else:
                        break
                
                # If stopped for long enough, report anomaly
                if stopped_duration >= self.stop_duration_sec:
                    severity = "low"
                    if stopped_duration > 10:
                        severity = "high"
                    elif stopped_duration > 5:
                        severity = "medium"
                    
                    return Anomaly(
                        anomaly_type="stopped",
                        timestamp=timestamps[i],
                        severity=severity,
                        description=f"Vehicle stopped for {stopped_duration:.1f} seconds",
                        track_id=track_id,
                        metadata={
                            "duration": stopped_duration,
                            "position": positions[i]
                        }
                    )
        
        return None
    
    def detect_high_speed(self, trajectory: Dict) -> Optional[Anomaly]:
        """
        Detect if a vehicle is moving at unusually high speed
        
        Args:
            trajectory: Vehicle trajectory with positions, timestamps, frames
            
        Returns:
            Anomaly object if high speed detected, None otherwise
        """
        positions = trajectory.get("positions", [])
        timestamps = trajectory.get("timestamps", [])
        track_id = trajectory.get("track_id")
        
        if len(positions) < 2 or len(timestamps) < 2:
            return None
        
        # Check for sudden large movements between consecutive detections
        for i in range(len(positions) - 1):
            x1, y1 = positions[i]
            x2, y2 = positions[i + 1]
            distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            
            # If movement is very large, report high speed
            if distance > self.speed_threshold_px:
                severity = "low"
                if distance > 400:
                    severity = "high"
                elif distance > 300:
                    severity = "medium"
                
                return Anomaly(
                    anomaly_type="speeding",
                    timestamp=timestamps[i],
                    severity=severity,
                    description=f"Vehicle moving at high speed ({distance:.0f} pixels in frame)",
                    track_id=track_id,
                    metadata={
                        "distance_px": distance,
                        "position": positions[i]
                    }
                )
        
        return None
    
    def detect_traffic_spike(self, segments: List[int], duration: float) -> List[Anomaly]:
        """
        Detect sudden spikes in traffic volume
        
        Args:
            segments: List of vehicle counts per segment (10 segments)
            duration: Total video duration in seconds
            
        Returns:
            List of Anomaly objects for traffic spikes
        """
        anomalies = []
        
        if not segments or len(segments) < 2:
            return anomalies
        
        # Calculate average traffic per segment
        avg_traffic = sum(segments) / len(segments)
        
        if avg_traffic == 0:
            return anomalies
        
        # Check each segment for spikes
        for i, count in enumerate(segments):
            # Check if this segment has significantly more traffic than average
            if count > avg_traffic * self.spike_multiplier:
                segment_start = (i * duration / len(segments)) if duration > 0 else 0
                segment_end = ((i + 1) * duration / len(segments)) if duration > 0 else 0
                
                severity = "low"
                multiplier = count / avg_traffic
                if multiplier > 5:
                    severity = "high"
                elif multiplier > 4:
                    severity = "medium"
                
                anomalies.append(Anomaly(
                    anomaly_type="spike",
                    timestamp=segment_start,
                    severity=severity,
                    description=f"Traffic spike: {count} vehicles ({multiplier:.1f}x average)",
                    track_id=None,
                    metadata={
                        "segment_number": i,
                        "segment_start": segment_start,
                        "segment_end": segment_end,
                        "vehicle_count": count,
                        "average_traffic": avg_traffic,
                        "multiplier": multiplier
                    }
                ))
        
        return anomalies
    
    def analyze_all(self, trajectories: Dict, segments: List[int], duration: float) -> List[Anomaly]:
        """
        Analyze all trajectories and segments for anomalies
        
        Args:
            trajectories: Dictionary of all vehicle trajectories
            segments: List of vehicle counts per segment
            duration: Total video duration in seconds
            
        Returns:
            List of all detected anomalies
        """
        all_anomalies = []
        
        # Check each trajectory for stopped vehicles and high speed
        for track_id, trajectory in trajectories.items():
            # Check for stopped vehicle
            stopped_anomaly = self.detect_stopped_vehicle(trajectory)
            if stopped_anomaly:
                all_anomalies.append(stopped_anomaly)
            
            # Check for high speed
            speed_anomaly = self.detect_high_speed(trajectory)
            if speed_anomaly:
                all_anomalies.append(speed_anomaly)
        
        # Check for traffic spikes
        spike_anomalies = self.detect_traffic_spike(segments, duration)
        all_anomalies.extend(spike_anomalies)
        
        # Sort by timestamp
        all_anomalies.sort(key=lambda a: a.timestamp)
        
        return all_anomalies
