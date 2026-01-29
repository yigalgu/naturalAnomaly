from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
import shutil
from pathlib import Path
from typing import Optional
from video_processor import VideoProcessor
from database import Database

app = FastAPI(title="Natural Anomaly Detection API")

# CORS - allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories for uploads and processed videos
UPLOAD_DIR = Path("uploads")
PROCESSED_DIR = Path("processed")
UPLOAD_DIR.mkdir(exist_ok=True)
PROCESSED_DIR.mkdir(exist_ok=True)

# Initialize video processor and database
video_processor = VideoProcessor()
db = Database()

class ChatRequest(BaseModel):
    message: str
    video_filename: Optional[str] = None

def process_video_background(file_path: Path, filename: str):
    """Background task to process video"""
    try:
        print(f"Starting to process video: {filename}")
        result = video_processor.process_video(file_path)
        db.save_analysis(result)
        print(f"Finished processing video: {filename}")
    except Exception as e:
        print(f"Error processing video {filename}: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Natural Anomaly Detection API is running"}

@app.post("/api/upload-video/")
async def upload_video(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """Upload a video file for processing"""
    try:
        # Validate file type
        if not file.content_type.startswith("video/"):
            raise HTTPException(status_code=400, detail="File must be a video")
        
        # Save the uploaded file
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Start processing in background
        background_tasks.add_task(process_video_background, file_path, file.filename)
        
        return JSONResponse(content={
            "message": "Video uploaded successfully and processing started",
            "filename": file.filename,
            "status": "processing"
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading video: {str(e)}")

@app.get("/api/video-status/{filename}")
async def get_video_status(filename: str):
    """Get processing status and results for a video"""
    try:
        analysis = db.get_analysis(filename)
        if not analysis:
            return JSONResponse(content={"status": "not_found"})
        
        return JSONResponse(content={
            "status": "completed" if analysis.processed == 2 else "processing",
            "statistics": {
                "total_vehicles": analysis.total_vehicles,
                "vehicles_per_hour": analysis.vehicles_per_hour,
                "vehicle_types": analysis.vehicle_types,
                "busiest_segment": analysis.busiest_segment,
                "duration": analysis.duration
            }
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting video status: {str(e)}")

@app.get("/api/videos/")
async def list_videos():
    """List all processed videos"""
    try:
        analyses = db.get_all_analyses()
        return JSONResponse(content={
            "videos": [
                {
                    "filename": a.filename,
                    "upload_date": a.upload_date.isoformat(),
                    "total_vehicles": a.total_vehicles,
                    "duration": a.duration
                }
                for a in analyses
            ]
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing videos: {str(e)}")

@app.post("/api/chat/")
async def chat(request: ChatRequest):
    """Chat about video analysis using AI"""
    try:
        # Get video analysis if filename provided
        context = {}
        if request.video_filename:
            analysis = db.get_analysis(request.video_filename)
            if analysis:
                context = {
                    "total_vehicles": analysis.total_vehicles,
                    "vehicles_per_hour": analysis.vehicles_per_hour,
                    "vehicle_types": analysis.vehicle_types,
                    "busiest_segment": analysis.busiest_segment,
                    "duration": analysis.duration
                }
        
        # Use AI assistant to generate response
        from ai_assistant import AIAssistant
        ai = AIAssistant()
        response = ai.ask(request.message, context, request.video_filename)
        
        return JSONResponse(content={
            "response": response
        })
    
    except Exception as e:
        # Fallback to basic response if AI fails
        return JSONResponse(content={
            "response": f"מצטער, אירעה שגיאה: {str(e)}\n\nאנא וודא ש-Ollama מותקן ורץ (ollama serve)"
        })

@app.get("/api/health/")
async def health_check():
    return {"status": "healthy", "service": "Natural Anomaly Detection"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
