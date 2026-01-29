import React, { useState } from 'react';
import ChatWindow from './ChatWindow.jsx';
import UploadVideo from './UploadVideo.jsx';
import VideoPlayer from './VideoPlayer.jsx';
import { Box, Typography, Container, Grid, Paper, Fade } from '@mui/material';
import AutoGraphIcon from '@mui/icons-material/AutoGraph';
import VideoSettingsIcon from '@mui/icons-material/VideoSettings';
import AnalyticsIcon from '@mui/icons-material/Analytics';

const MainScreen = () => {
  const [videoUrl, setVideoUrl] = useState(null);
  const [statistics, setStatistics] = useState(null);
  const [currentFilename, setCurrentFilename] = useState(null);

  const handleVideoUpload = (url) => {
    setVideoUrl(url);
    setStatistics(null);
  };

  const handleProcessingComplete = (stats, filename) => {
    setStatistics(stats);
    setCurrentFilename(filename);
  };

  return (
    <Box sx={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Premium Header */}
      <Box component="header" sx={{
        padding: '20px 40px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        borderBottom: '1px solid rgba(255,255,255,0.05)',
        background: 'rgba(15, 23, 42, 0.8)',
        backdropFilter: 'blur(10px)',
        position: 'sticky',
        top: 0,
        zIndex: 1000
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Box sx={{
            background: 'linear-gradient(135deg, #6366f1 0%, #a855f7 100%)',
            padding: '8px',
            borderRadius: '12px',
            display: 'flex',
            boxShadow: '0 0 20px rgba(99, 102, 241, 0.4)'
          }}>
            <AutoGraphIcon sx={{ color: 'white' }} />
          </Box>
          <Typography variant="h5" sx={{ fontWeight: 800, letterSpacing: '-0.5px' }}>
            NATURAL <span style={{ color: '#6366f1' }}>ANOMALY</span>
          </Typography>
        </Box>
      </Box>

      <Container maxWidth="xl" sx={{ flex: 1, padding: '30px 0' }}>
        <Grid container spacing={3} sx={{ height: 'calc(100vh - 120px)' }}>
          {/* Main Content Area: Upload & Player & Stats */}
          <Grid item xs={12} lg={8.5} sx={{ display: 'flex', flexDirection: 'column', gap: 3, height: '100%' }}>

            {/* Action Bar */}
            <Box className="glass" sx={{ padding: '20px', display: 'flex', alignItems: 'center', gap: 3 }}>
              <UploadVideo
                onUpload={handleVideoUpload}
                onProcessingComplete={handleProcessingComplete}
              />
              <Typography variant="body2" sx={{ color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: 1 }}>
                <VideoSettingsIcon fontSize="small" />
                {videoUrl ? (currentFilename || 'Video Loaded') : 'Upload a video to begin AI Analysis'}
              </Typography>
            </Box>

            {/* Video Player Segment */}
            <Box className="glass" sx={{ flex: 1, overflow: 'hidden', position: 'relative', minHeight: '400px' }}>
              <VideoPlayer videoUrl={videoUrl} />
              {!videoUrl && (
                <Box sx={{
                  position: 'absolute', top: 0, left: 0, right: 0, bottom: 0,
                  display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
                  background: 'rgba(15, 23, 42, 0.4)', color: 'var(--text-muted)'
                }}>
                  <AnalyticsIcon sx={{ fontSize: 60, opacity: 0.2, mb: 2 }} />
                  <Typography variant="h6" sx={{ opacity: 0.5 }}>Waiting for video signal...</Typography>
                </Box>
              )}
            </Box>

            {/* Stats Dashboard */}
            {statistics && (
              <Fade in={!!statistics}>
                <Grid container spacing={2}>
                  {[
                    { label: 'Total Vehicles', val: statistics.total_vehicles, icon: '🚗', color: '#6366f1' },
                    { label: 'Vehicles / Hour', val: statistics.vehicles_per_hour, icon: '⏱️', color: '#a855f7' },
                    { label: 'Peak Density', val: `${statistics.busiest_segment?.vehicle_count || 0} req`, icon: '🔥', color: '#f43f5e' },
                    { label: 'Lead Type', val: Object.keys(statistics.vehicle_types)[0] || 'N/A', icon: '📊', color: '#10b981' }
                  ].map((stat, i) => (
                    <Grid item xs={6} md={3} key={i}>
                      <Paper className="glass" sx={{
                        padding: '15px',
                        textAlign: 'center',
                        background: 'rgba(255,255,255,0.03)',
                        borderBottom: `3px solid ${stat.color} `
                      }}>
                        <Typography variant="caption" sx={{ color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
                          {stat.label}
                        </Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1, mt: 1 }}>
                          <span style={{ fontSize: '1.2rem' }}>{stat.icon}</span>
                          <Typography variant="h5" sx={{ fontWeight: 800 }}>{stat.val}</Typography>
                        </Box>
                      </Paper>
                    </Grid>
                  ))}
                </Grid>
              </Fade>
            )}
          </Grid>

          {/* AI Chat Area */}
          <Grid item xs={12} lg={3.5} sx={{ height: '100%' }}>
            <Box className="glass" sx={{ height: '100%', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
              <Box sx={{ padding: '15px 20px', borderBottom: '1px solid var(--glass-border)', display: 'flex', alignItems: 'center', gap: 1.5 }}>
                <Box sx={{ width: 10, height: 10, borderRadius: '50%', background: '#10b981', boxShadow: '0 0 10px #10b981' }} />
                <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>AI ANALYST</Typography>
              </Box>
              <Box sx={{ flex: 1, overflow: 'hidden' }}>
                <ChatWindow videoFilename={currentFilename} />
              </Box>
            </Box>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
};

export default MainScreen;
