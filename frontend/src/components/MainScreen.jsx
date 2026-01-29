import React, { useState } from 'react';
import ChatWindow from './ChatWindow.jsx';
import UploadVideo from './UploadVideo.jsx';
import VideoPlayer from './VideoPlayer.jsx';
import { Box, Paper, Typography } from '@mui/material';

const MainScreen = () => {
  const [videoUrl, setVideoUrl] = useState(null);
  const [statistics, setStatistics] = useState(null);
  const [currentFilename, setCurrentFilename] = useState(null);

  const handleVideoUpload = (url) => {
    setVideoUrl(url);
    setStatistics(null); // Reset statistics when new video is uploaded
  };

  const handleProcessingComplete = (stats, filename) => {
    setStatistics(stats);
    setCurrentFilename(filename);
  };

  return (
    <Box
      sx={{
        display: 'flex',
        height: '100vh',
        backgroundColor: '#f0f0f0',
      }}
    >
      {/* אזור הווידאו – צד ימין */}
      <Box
        sx={{
          flex: 2.5,
          display: 'flex',
          flexDirection: 'column',
          padding: '20px',
          gap: '20px',
          overflow: 'hidden',
        }}
      >
        <UploadVideo
          onUpload={handleVideoUpload}
          onProcessingComplete={handleProcessingComplete}
        />

        {statistics && (
          <Paper sx={{ padding: '15px', backgroundColor: '#e3f2fd' }}>
            <Typography variant="h6" gutterBottom>תוצאות ניתוח:</Typography>
            <Typography>🚗 סה"כ כלי רכב: {statistics.total_vehicles}</Typography>
            <Typography>⏱️ כלי רכב לשעה: {statistics.vehicles_per_hour}</Typography>
            <Typography>📊 סוגי רכבים: {JSON.stringify(statistics.vehicle_types)}</Typography>
            {statistics.busiest_segment && (
              <Typography>
                🔥 קטע עמוס ביותר: {statistics.busiest_segment.start_time?.toFixed(1)}s - {statistics.busiest_segment.end_time?.toFixed(1)}s
              </Typography>
            )}
          </Paper>
        )}

        <Box sx={{ flex: 1, overflow: 'hidden' }}>
          <VideoPlayer videoUrl={videoUrl} />
        </Box>
      </Box>

      {/* אזור הצ'אט – צד שמאל */}
      <Box
        sx={{
          flex: 1,
          padding: '20px',
          borderLeft: '1px solid #ccc',
          backgroundColor: '#ffffff',
        }}
      >
        <ChatWindow videoFilename={currentFilename} />
      </Box>
    </Box>
  );
};

export default MainScreen;
