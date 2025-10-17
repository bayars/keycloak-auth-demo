import React, { useEffect } from 'react';
import { Box, CircularProgress, Typography } from '@mui/material';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

const CallbackPage = () => {
  const { loading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    // The AuthContext will handle the token exchange
    // Once loading is complete, redirect to dashboard
    if (!loading) {
      navigate('/dashboard');
    }
  }, [loading, navigate]);

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        gap: 2
      }}
    >
      <CircularProgress size={60} />
      <Typography variant="h6" color="text.secondary">
        Processing authentication...
      </Typography>
      <Typography variant="body2" color="text.secondary">
        Please wait while we complete your login.
      </Typography>
    </Box>
  );
};

export default CallbackPage;
