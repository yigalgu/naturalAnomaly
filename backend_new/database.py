from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json

Base = declarative_base()

class VideoAnalysis(Base):
    """Store video analysis results"""
    __tablename__ = "video_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, index=True)
    upload_date = Column(DateTime, default=datetime.utcnow)
    duration = Column(Float)
    fps = Column(Float)
    total_frames = Column(Integer)
    total_vehicles = Column(Integer)
    vehicles_per_hour = Column(Float)
    vehicle_types = Column(JSON)  # Store as JSON
    busiest_segment = Column(JSON)  # Store as JSON
    detections = Column(JSON)  # Store all detections as JSON
    processed = Column(Integer, default=0)  # 0 = pending, 1 = processing, 2 = done

class AnomalyRecord(Base):
    """Store detected anomalies"""
    __tablename__ = "anomalies"
    
    id = Column(Integer, primary_key=True, index=True)
    video_filename = Column(String, index=True)
    timestamp = Column(Float)
    anomaly_type = Column(String)      # "stopped", "speeding", "spike"
    severity = Column(String)          # "low", "medium", "high"
    description = Column(String)
    track_id = Column(Integer, nullable=True)
    anomaly_metadata = Column(JSON)    # Additional details (renamed from 'metadata' which is reserved)

class Database:
    """Database manager"""
    
    def __init__(self, db_url: str = "sqlite+aiosqlite:///./anomaly_detection.db"):
        self.engine = create_engine(
            db_url.replace("aiosqlite", "pysqlite"),
            connect_args={"check_same_thread": False}
        )
        Base.metadata.create_all(bind=self.engine)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def get_session(self):
        """Get database session"""
        return self.SessionLocal()
    
    def save_analysis(self, analysis_data: dict):
        """Save video analysis to database"""
        session = self.get_session()
        try:
            video_info = analysis_data["video_info"]
            stats = analysis_data["statistics"]
            
            analysis = VideoAnalysis(
                filename=video_info["filename"],
                duration=video_info["duration"],
                fps=video_info["fps"],
                total_frames=video_info["total_frames"],
                total_vehicles=stats["total_vehicles"],
                vehicles_per_hour=stats["vehicles_per_hour"],
                vehicle_types=stats["vehicle_types"],
                busiest_segment=stats["busiest_segment"],
                detections=analysis_data["detections"],
                processed=2
            )
            
            session.add(analysis)
            session.commit()
            session.refresh(analysis)
            return analysis
        finally:
            session.close()
    
    def get_analysis(self, filename: str):
        """Get analysis by filename"""
        session = self.get_session()
        try:
            return session.query(VideoAnalysis).filter(VideoAnalysis.filename == filename).first()
        finally:
            session.close()
    
    def get_all_analyses(self):
        """Get all analyses"""
        session = self.get_session()
        try:
            return session.query(VideoAnalysis).all()
        finally:
            session.close()
    
    def save_anomalies(self, filename: str, anomalies: list):
        """Save detected anomalies to database"""
        session = self.get_session()
        try:
            # First, delete any existing anomalies for this video
            session.query(AnomalyRecord).filter(AnomalyRecord.video_filename == filename).delete()
            
            # Add new anomalies
            for anomaly_data in anomalies:
                anomaly = AnomalyRecord(
                    video_filename=filename,
                    timestamp=anomaly_data.get("timestamp"),
                    anomaly_type=anomaly_data.get("anomaly_type"),
                    severity=anomaly_data.get("severity"),
                    description=anomaly_data.get("description"),
                    track_id=anomaly_data.get("track_id"),
                    anomaly_metadata=anomaly_data.get("metadata", {})
                )
                session.add(anomaly)
            
            session.commit()
        finally:
            session.close()
    
    def get_anomalies(self, filename: str):
        """Get all anomalies for a specific video"""
        session = self.get_session()
        try:
            return session.query(AnomalyRecord).filter(AnomalyRecord.video_filename == filename).all()
        finally:
            session.close()
    
    def delete_anomalies(self, filename: str):
        """Delete all anomalies for a specific video"""
        session = self.get_session()
        try:
            session.query(AnomalyRecord).filter(AnomalyRecord.video_filename == filename).delete()
            session.commit()
        finally:
            session.close()
