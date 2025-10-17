import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://lab-test2.safa.nisvcg.comp.net'
  : 'http://localhost:3000';

// Configure axios defaults
axios.defaults.baseURL = API_BASE_URL;

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('access_token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if we're returning from Keycloak authentication
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    const state = urlParams.get('state');
    
    if (code && state) {
      // We're returning from Keycloak, exchange code for token
      exchangeCodeForToken(code, state);
    } else if (token) {
      // We have a token, verify it
      verifyToken();
    } else {
      // No token and no code - user needs to authenticate
      // HAProxy will redirect them to Keycloak automatically
      setLoading(false);
    }
  }, [token]);

  const exchangeCodeForToken = async (code, state) => {
    try {
      setLoading(true);
      
      // Exchange authorization code for access token
      const formData = new URLSearchParams();
      formData.append('grant_type', 'authorization_code');
      formData.append('client_id', 'myapp');
      formData.append('code', code);
      formData.append('redirect_uri', `${window.location.origin}/callback`);
      
      const response = await axios.post('/auth/realms/myrealm/protocol/openid-connect/token', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      });

      const { access_token, refresh_token, expires_in } = response.data;
      
      // Store tokens
      setToken(access_token);
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      localStorage.setItem('token_expires', Date.now() + (expires_in * 1000));
      
      // Set axios default header
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      // Get user info
      await verifyToken();
      
      // Clean up URL
      window.history.replaceState({}, document.title, window.location.pathname);
      
    } catch (error) {
      console.error('Token exchange failed:', error);
      logout();
    } finally {
      setLoading(false);
    }
  };

  const verifyToken = async () => {
    try {
      const response = await axios.get('/api/user/me');
      console.log('DEBUG: User info from API:', response.data);
      
      setUser(response.data);
    } catch (error) {
      console.error('Token verification failed:', error);
      logout();
    } finally {
      setLoading(false);
    }
  };

  const login = () => {
    // Redirect to Keycloak login - this will be handled by HAProxy redirect
    // Users will be automatically redirected to Keycloak when they visit the app
    window.location.href = '/';
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('token_expires');
    localStorage.removeItem('oauth_state');
    delete axios.defaults.headers.common['Authorization'];
    
    // Redirect to Keycloak logout
    const logoutUrl = `${API_BASE_URL}/auth/realms/myrealm/protocol/openid-connect/logout?client_id=myapp&post_logout_redirect_uri=${encodeURIComponent(window.location.origin)}`;
    window.location.href = logoutUrl;
  };

  const value = {
    user,
    token,
    loading,
    login,
    logout,
    isAuthenticated: !!user && !!token,
    isAdmin: user?.roles?.includes('admin') || false
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
