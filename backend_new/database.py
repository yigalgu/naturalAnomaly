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
