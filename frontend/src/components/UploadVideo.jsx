import React, { useState } from 'react';
import { Button, CircularProgress, Typography, Box, IconButton } from '@mui/material';
import axios from 'axios';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';

const UploadVideo = ({ onUpload, onProcessingComplete }) => {
  const [uploading, setUploading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [percent, setPercent] = useState(0);

  const handleFileChange = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    try {
      setUploading(true);
      setPercent(0);

      const videoURL = URL.createObjectURL(file);
      onUpload(videoURL);

      const formData = new FormData();
      formData.append('file', file);

      const response = await axios.post('http://localhost:8000/api/upload-video/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (progressEvent) => {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setPercent(progress);
        }
      });

      setUploading(false);
      setProcessing(true);
      checkProcessingStatus(response.data.filename);

    } catch (error) {
      console.error('Error uploading video:', error);
      setUploading(false);
      alert('Error uploading video');
    }
  };

  const checkProcessingStatus = async (filename) => {
    try {
      const response = await axios.get(`http://localhost:8000/api/video-status/${filename}`);
      if (response.data.status === 'completed') {
        setProcessing(false);
        if (onProcessingComplete) onProcessingComplete(response.data.statistics, filename);
      } else {
        setTimeout(() => checkProcessingStatus(filename), 2000);
      }
    } catch (error) {
      console.error('Error checking status:', error);
      setProcessing(false);
    }
  };

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
      <Button
        variant="contained"
        component="label"
        startIcon={processing ? <CircularProgress size={20} color="inherit" /> : <CloudUploadIcon />}
        sx={{
          background: 'linear-gradient(135deg, #6366f1 0%, #a855f7 100%)',
          borderRadius: '12px',
          padding: '10px 24px',
          fontWeight: 700,
          textTransform: 'none',
          boxShadow: '0 4px 15px rgba(99, 102, 241, 0.3)',
          '&:hover': {
            background: 'linear-gradient(135deg, #4f46e5 0%, #9333ea 100%)',
            boxShadow: '0 6px 20px rgba(99, 102, 241, 0.5)',
          }
        }}
        disabled={uploading || processing}
      >
        {uploading ? `Uploading ${percent}%` : processing ? 'AI Processing...' : 'Upload New Stream'}
        <input type="file" accept="video/*" hidden onChange={handleFileChange} />
      </Button>

      {processing && (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Typography variant="caption" sx={{ color: '#10b981', fontWeight: 600, display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <CheckCircleIcon sx={{ fontSize: 16 }} /> Server Received
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default UploadVideo;
