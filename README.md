# Natural Anomaly Detection 🚗📊

AI-powered vehicle detection and traffic analysis system using YOLO and intelligent chat interface.

## Features ✨

- **Video Upload & Processing** - Upload traffic videos for automatic analysis
- **Vehicle Detection** - Detect cars, trucks, motorcycles, and buses using YOLOv8
- **Traffic Statistics** - Get insights on:
  - Total vehicles detected
  - Vehicles per hour
  - Vehicle type distribution
  - Busiest time segments
- **AI Chat Interface** - Ask questions about the analyzed video in natural language
- **Real-time Processing** - Background processing with progress tracking

## Tech Stack 🛠️

### Backend
- **FastAPI** - Modern, fast web framework
- **YOLOv8** - State-of-the-art object detection
- **SQLAlchemy** - Database ORM
- **OpenCV** - Video processing
- **Ollama** - Local LLM for intelligent chat (coming soon)

### Frontend
- **React** - UI framework
- **Vite** - Build tool
- **Material-UI** - Component library
- **Axios** - HTTP client

## Installation 🚀

### Prerequisites
- Python 3.12+
- Node.js 18+
- Git

### Backend Setup

```powershell
# Navigate to backend
cd backend_new

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run server
python main.py
```

Server will run on `http://localhost:8000`

### Frontend Setup

```powershell
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend will run on `http://localhost:5173`

## Usage 📖

1. **Start both servers** (backend and frontend)
2. **Open browser** at `http://localhost:5173`
3. **Upload a video** of traffic/vehicles
4. **Wait for processing** - YOLO will analyze the video
5. **View statistics** - See detection results
6. **Ask questions** - Use the chat interface to query the data

## Project Structure 📁

```
naturalAnomaly/
├── backend_new/          # New FastAPI backend
│   ├── main.py          # Main API server
│   ├── video_processor.py  # YOLO video processing
│   ├── database.py      # SQLAlchemy models
│   ├── requirements.txt # Python dependencies
│   ├── uploads/         # Uploaded videos (gitignored)
│   └── processed/       # Processed videos (gitignored)
├── frontend/            # React frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   │   ├── MainScreen.jsx
│   │   │   ├── UploadVideo.jsx
│   │   │   ├── VideoPlayer.jsx
│   │   │   └── ChatWindow.jsx
│   │   └── App.jsx
│   └── package.json
└── README.md
```

## API Endpoints 🔌

- `POST /api/upload-video/` - Upload video for processing
- `GET /api/video-status/{filename}` - Get processing status and results
- `GET /api/videos/` - List all processed videos
- `POST /api/chat/` - Chat about video analysis
- `GET /api/health/` - Health check

## Development Notes 📝

### Video Processing
- Processes every 10th frame for efficiency
- Uses YOLOv8n (nano) model for speed
- Detects: cars, motorcycles, buses, trucks
- Confidence threshold: 0.5

### Performance
- 2-minute video: ~2-5 minutes processing time
- Depends on CPU/GPU availability
- Progress updates every 100 frames

## Roadmap 🗺️

- [x] Video upload and processing
- [x] YOLO vehicle detection
- [x] Statistics calculation
- [x] Database storage
- [x] Basic chat interface
- [ ] Ollama integration for intelligent chat
- [ ] Vehicle tracking (unique vehicle counting)
- [ ] Anomaly detection algorithms
- [ ] Export reports (PDF/CSV)
- [ ] Multi-video comparison

## Contributing 🤝

Feel free to open issues or submit pull requests!

## License 📄

MIT License

---

**Built with ❤️ using FastAPI, React, and YOLOv8**
