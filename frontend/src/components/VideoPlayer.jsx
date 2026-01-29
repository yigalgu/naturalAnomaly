import React from 'react';
import ReactPlayer from 'react-player';
import { Box, Typography } from '@mui/material';
import VideocamIcon from '@mui/icons-material/Videocam';

const VideoPlayer = ({ videoUrl }) => {
  if (!videoUrl) return null;

  return (
    <Box sx={{
      position: 'relative',
      width: '100%',
      height: '100%',
      display: 'flex',
      flexDirection: 'column',
      background: '#000'
    }}>
      {/* Overlay Status */}
      <Box sx={{
        position: 'absolute',
        top: 15,
        left: 15,
        zIndex: 10,
        display: 'flex',
        alignItems: 'center',
        gap: 1,
        background: 'rgba(0,0,0,0.6)',
        padding: '6px 12px',
        borderRadius: '8px',
        backdropFilter: 'blur(5px)',
        border: '1px solid rgba(255,255,255,0.1)'
      }}>
        <VideocamIcon sx={{ fontSize: 18, color: '#f43f5e' }} />
        <Typography variant="caption" sx={{ color: 'white', fontWeight: 700, letterSpacing: '1px' }}>
          LIVE ANALYSIS
        </Typography>
      </Box>

      {/* Player Wrapper */}
      <Box sx={{ flex: 1, position: 'relative' }}>
        <ReactPlayer
          url={videoUrl}
          controls
          width="100%"
          height="100%"
          style={{ position: 'absolute', top: 0, left: 0 }}
          playing={true}
          loop={true}
        />
      </Box>
    </Box>
  );
};

export default VideoPlayer;
