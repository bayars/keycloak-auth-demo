import React, { useState } from 'react';
import {
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Box,
  Alert,
  CircularProgress,
  Card,
  CardContent,
  IconButton
} from '@mui/material';
import { 
  Lock, 
  Visibility, 
  VisibilityOff, 
  CheckCircle,
  ArrowBack 
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

const ChangePasswordPage = () => {
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPasswords, setShowPasswords] = useState({
    old: false,
    new: false,
    confirm: false
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);
  
  const { changePassword, user } = useAuth();
  const navigate = useNavigate();

  const handleTogglePasswordVisibility = (field) => {
    setShowPasswords(prev => ({
      ...prev,
      [field]: !prev[field]
    }));
  };

  const validatePassword = (password) => {
    if (password.length < 8) {
      return 'Password must be at least 8 characters long';
    }
    if (!/(?=.*[a-z])/.test(password)) {
      return 'Password must contain at least one lowercase letter';
    }
    if (!/(?=.*[A-Z])/.test(password)) {
      return 'Password must contain at least one uppercase letter';
    }
    if (!/(?=.*\d)/.test(password)) {
      return 'Password must contain at least one number';
    }
    return null;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess(false);

    // Validation
    if (newPassword !== confirmPassword) {
      setError('New passwords do not match');
      return;
    }

    const passwordError = validatePassword(newPassword);
    if (passwordError) {
      setError(passwordError);
      return;
    }

    setLoading(true);

    try {
      const result = await changePassword(oldPassword, newPassword, confirmPassword);
      
      if (result.success) {
        setSuccess(true);
        setTimeout(() => {
          navigate('/dashboard');
        }, 2000);
      } else {
        setError(result.error);
      }
    } catch (err) {
      setError('An unexpected error occurred');
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <Container component="main" maxWidth="sm">
        <Box
          sx={{
            marginTop: 8,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
          }}
        >
          <Card sx={{ width: '100%', maxWidth: 400 }}>
            <CardContent sx={{ p: 4, textAlign: 'center' }}>
              <CheckCircle sx={{ fontSize: 60, color: 'success.main', mb: 2 }} />
              <Typography variant="h5" gutterBottom>
                Password Changed Successfully!
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Redirecting to dashboard...
              </Typography>
              <CircularProgress sx={{ mt: 2 }} />
            </CardContent>
          </Card>
        </Box>
      </Container>
    );
  }

  return (
    <Container component="main" maxWidth="sm">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Card sx={{ width: '100%', maxWidth: 400 }}>
          <CardContent sx={{ p: 4 }}>
            <Box
              sx={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                mb: 3
              }}
            >
              <Lock sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
              <Typography component="h1" variant="h4" gutterBottom>
                Change Password
              </Typography>
              <Typography variant="body2" color="text.secondary" align="center">
                Welcome {user?.username}! Please update your password to continue.
              </Typography>
            </Box>

            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error}
              </Alert>
            )}

            <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
              <TextField
                margin="normal"
                required
                fullWidth
                name="oldPassword"
                label="Current Password"
                type={showPasswords.old ? 'text' : 'password'}
                id="oldPassword"
                value={oldPassword}
                onChange={(e) => setOldPassword(e.target.value)}
                InputProps={{
                  startAdornment: <Lock sx={{ mr: 1, color: 'action.active' }} />,
                  endAdornment: (
                    <IconButton
                      onClick={() => handleTogglePasswordVisibility('old')}
                      edge="end"
                    >
                      {showPasswords.old ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  )
                }}
                disabled={loading}
              />
              
              <TextField
                margin="normal"
                required
                fullWidth
                name="newPassword"
                label="New Password"
                type={showPasswords.new ? 'text' : 'password'}
                id="newPassword"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                InputProps={{
                  startAdornment: <Lock sx={{ mr: 1, color: 'action.active' }} />,
                  endAdornment: (
                    <IconButton
                      onClick={() => handleTogglePasswordVisibility('new')}
                      edge="end"
                    >
                      {showPasswords.new ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  )
                }}
                disabled={loading}
                helperText="Must be at least 8 characters with uppercase, lowercase, and number"
              />
              
              <TextField
                margin="normal"
                required
                fullWidth
                name="confirmPassword"
                label="Confirm New Password"
                type={showPasswords.confirm ? 'text' : 'password'}
                id="confirmPassword"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                InputProps={{
                  startAdornment: <Lock sx={{ mr: 1, color: 'action.active' }} />,
                  endAdornment: (
                    <IconButton
                      onClick={() => handleTogglePasswordVisibility('confirm')}
                      edge="end"
                    >
                      {showPasswords.confirm ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  )
                }}
                disabled={loading}
              />

              <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
                <Button
                  variant="outlined"
                  fullWidth
                  onClick={() => navigate('/login')}
                  disabled={loading}
                  startIcon={<ArrowBack />}
                >
                  Back to Login
                </Button>
                <Button
                  type="submit"
                  fullWidth
                  variant="contained"
                  disabled={loading || !oldPassword || !newPassword || !confirmPassword}
                >
                  {loading ? (
                    <CircularProgress size={24} color="inherit" />
                  ) : (
                    'Change Password'
                  )}
                </Button>
              </Box>
            </Box>

            <Box sx={{ mt: 3, p: 2, bgcolor: 'info.light', borderRadius: 1 }}>
              <Typography variant="body2" color="info.contrastText" align="center">
                <strong>Password Requirements:</strong><br />
                • At least 8 characters<br />
                • One uppercase letter<br />
                • One lowercase letter<br />
                • One number
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Box>
    </Container>
  );
};

export default ChangePasswordPage;
