import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, CircularProgress, Box } from '@mui/material';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import LoginPage from './pages/LoginPage';
import ChangePasswordPage from './pages/ChangePasswordPage';
import DashboardPage from './pages/DashboardPage';

// Create Material-UI theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
});

// Protected Route component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height: '100vh',
        }}
      >
        <CircularProgress />
      </Box>
    );
  }
  
  return isAuthenticated ? children : <Navigate to="/login" replace />;
};

// Password Change Route component
const PasswordChangeRoute = ({ children }) => {
  const { isAuthenticated, loading, user } = useAuth();
  
  console.log('DEBUG PasswordChangeRoute:', { isAuthenticated, loading, user });
  console.log('DEBUG PasswordChangeRoute - user.must_change_password:', user?.must_change_password);
  console.log('DEBUG PasswordChangeRoute - isAuthenticated calculation:', !!user && (!!user.token || user?.must_change_password));
  
  if (loading) {
    console.log('DEBUG: Still loading, showing spinner');
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height: '100vh',
        }}
      >
        <CircularProgress />
      </Box>
    );
  }
  
  if (!isAuthenticated) {
    console.log('DEBUG: Not authenticated, redirecting to login');
    return <Navigate to="/login" replace />;
  }
  
  // If user object is not ready yet, show loading
  if (!user) {
    console.log('DEBUG: User object not ready, showing loading');
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height: '100vh',
        }}
      >
        <CircularProgress />
      </Box>
    );
  }
  
  // Show password change page if user exists and must_change_password is true
  if (user.must_change_password === true) {
    console.log('DEBUG: Showing password change page - must_change_password is true');
    return children;
  }
  
  // Only redirect to dashboard if we're sure the user doesn't need password change
  if (user.must_change_password === false) {
    console.log('DEBUG: Password change not required, redirecting to dashboard');
    return <Navigate to="/dashboard" replace />;
  }
  
  // Fallback: if must_change_password is undefined or null, show loading
  console.log('DEBUG: must_change_password is undefined/null, showing loading');
  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
      }}
    >
      <CircularProgress />
    </Box>
  );
};

// Main App component
const AppContent = () => {
  return (
    <Router>
      <CssBaseline />
      <Routes>
        {/* Public routes */}
        <Route path="/login" element={<LoginPage />} />
        
        {/* Protected routes */}
        <Route
          path="/change-password"
          element={
            <PasswordChangeRoute>
              <ChangePasswordPage />
            </PasswordChangeRoute>
          }
        />
        
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <DashboardPage />
            </ProtectedRoute>
          }
        />
        
        {/* Default redirect */}
        <Route path="/" element={<Navigate to="/login" replace />} />
        
        {/* Catch all route */}
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </Router>
  );
};

// Root App component with providers
const App = () => {
  return (
    <ThemeProvider theme={theme}>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </ThemeProvider>
  );
};

export default App;
