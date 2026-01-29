import React, { useState } from 'react';
import { Button, CircularProgress, Typography, Box } from '@mui/material';
import axios from 'axios';

const UploadVideo = ({ onUpload, onProcessingComplete }) => {
  const [uploading, setUploading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [currentFile, setCurrentFile] = useState(null);

  const handleFileChange = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    try {
      setUploading(true);

      // Create local URL for preview
      const videoURL = URL.createObjectURL(file);
      onUpload(videoURL);

      // Upload to server
      const formData = new FormData();
      formData.append('file', file);

      const response = await axios.post('http://localhost:8000/api/upload-video/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setCurrentFile(response.data.filename);
      setUploading(false);
      setProcessing(true);

      // Poll for processing status
      checkProcessingStatus(response.data.filename);

    } catch (error) {
      console.error('Error uploading video:', error);
      setUploading(false);
      alert('שגיאה בהעלאת הוידאו');
    }
  };

  const checkProcessingStatus = async (filename) => {
    try {
      const response = await axios.get(`http://localhost:8000/api/video-status/${filename}`);

      if (response.data.status === 'completed') {
        setProcessing(false);
        if (onProcessingComplete) {
          onProcessingComplete(response.data.statistics, filename);
        }
      } else {
        // Check again in 2 seconds
        setTimeout(() => checkProcessingStatus(filename), 2000);
      }
    } catch (error) {
      console.error('Error checking status:', error);
      setProcessing(false);
    }
  };

  return (
    <Box>
      <Button
        variant="contained"
        component="label"
        disabled={uploading || processing}
      >
        {uploading ? 'מעלה...' : processing ? 'מעבד...' : 'העלה וידאו'}
        <input
          type="file"
          accept="video/*"
          hidden
          onChange={handleFileChange}
          disabled={uploading || processing}
        />
      </Button>

      {(uploading || processing) && (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mt: 2 }}>
          <CircularProgress size={24} />
          <Typography variant="body2">
            {uploading ? 'מעלה וידאו...' : 'מעבד וידאו עם AI...'}
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default UploadVideo;
