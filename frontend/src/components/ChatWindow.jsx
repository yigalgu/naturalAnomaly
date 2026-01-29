import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Box, TextField, Paper, Typography, IconButton, InputBase, Fade } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import PersonIcon from '@mui/icons-material/Person';

const ChatWindow = ({ videoFilename }) => {
  const [messages, setMessages] = useState([
    { sender: 'bot', content: 'Hello! I am your AI traffic analyst. Upload a video, and I can answer any questions about the detected objects and patterns.' }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  const sendMessage = useCallback(() => {
    if (inputMessage.trim() === '') return;

    const userMsg = { sender: 'user', content: inputMessage };
    setMessages((prev) => [...prev, userMsg]);
    setInputMessage('');

    fetch('http://localhost:8000/api/chat/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: inputMessage,
        video_filename: videoFilename
      }),
    })
      .then((res) => res.json())
      .then((data) => {
        setMessages((prev) => [...prev, { sender: 'bot', content: data.response }]);
      })
      .catch((error) => {
        setMessages((prev) => [...prev, { sender: 'bot', content: 'Connection error. Is the backend running?' }]);
      });
  }, [inputMessage, videoFilename]);

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column', background: 'transparent' }}>
      {/* Messages Area */}
      <Box sx={{ flex: 1, overflowY: 'auto', padding: '20px', display: 'flex', flexDirection: 'column', gap: 2 }}>
        {messages.map((msg, i) => (
          <Fade in key={i}>
            <Box sx={{
              alignSelf: msg.sender === 'user' ? 'flex-end' : 'flex-start',
              maxWidth: '85%',
              display: 'flex',
              flexDirection: 'column',
              alignItems: msg.sender === 'user' ? 'flex-end' : 'flex-start',
              gap: 0.5
            }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                {msg.sender === 'bot' && <SmartToyIcon sx={{ fontSize: 16, color: 'var(--primary)' }} />}
                <Typography variant="caption" sx={{ color: 'var(--text-muted)', fontWeight: 600 }}>
                  {msg.sender === 'bot' ? 'AI ANALYST' : 'YOU'}
                </Typography>
                {msg.sender === 'user' && <PersonIcon sx={{ fontSize: 16, color: 'var(--secondary)' }} />}
              </Box>

              <Box sx={{
                padding: '12px 16px',
                borderRadius: msg.sender === 'user' ? '18px 4px 18px 18px' : '4px 18px 18px 18px',
                background: msg.sender === 'user'
                  ? 'linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)'
                  : 'rgba(255,255,255,0.07)',
                border: msg.sender === 'bot' ? '1px solid var(--glass-border)' : 'none',
                boxShadow: msg.sender === 'user' ? '0 4px 15px rgba(99, 102, 241, 0.3)' : 'none'
              }}>
                <Typography variant="body2" sx={{ lineHeight: 1.6, color: 'white' }}>
                  {msg.content}
                </Typography>
              </Box>
            </Box>
          </Fade>
        ))}
        <div ref={messagesEndRef} />
      </Box>

      {/* Input Area */}
      <Box sx={{
        padding: '15px 20px',
        background: 'rgba(15, 23, 42, 0.4)',
        borderTop: '1px solid var(--glass-border)'
      }}>
        <Paper sx={{
          display: 'flex',
          alignItems: 'center',
          padding: '4px 12px',
          background: 'rgba(255,255,255,0.05)',
          borderRadius: '12px',
          border: '1px solid var(--glass-border)'
        }}>
          <InputBase
            sx={{ ml: 1, flex: 1, color: 'white', fontSize: '0.9rem' }}
            placeholder="Ask about traffic patterns..."
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          />
          <IconButton sx={{ color: 'var(--primary)' }} onClick={sendMessage}>
            <SendIcon />
          </IconButton>
        </Paper>
      </Box>
    </Box>
  );
};

export default ChatWindow;
