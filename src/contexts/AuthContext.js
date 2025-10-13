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
    if (token) {
      // Set axios default header
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      
      // Verify token and get user info
      verifyToken();
    } else {
      setLoading(false);
    }
  }, [token]);

  const verifyToken = async () => {
    try {
      const response = await axios.get('/api/user/me');
      console.log('DEBUG: User info from API:', response.data);
      
      // Preserve must_change_password flag if it exists
      setUser(prevUser => {
        const newUserData = response.data;
        if (prevUser && prevUser.must_change_password !== undefined) {
          newUserData.must_change_password = prevUser.must_change_password;
        }
        console.log('DEBUG: Setting user in verifyToken:', newUserData);
        return newUserData;
      });
    } catch (error) {
      console.error('Token verification failed:', error);
      logout();
    } finally {
      setLoading(false);
    }
  };

  const login = async (username, password) => {
    try {
      const response = await axios.post('/api/login', {
        username,
        password
      });
      
      const { access_token, roles, must_change_password } = response.data;
      
      // If must_change_password is true, we don't have a valid token yet
      if (must_change_password) {
        // Create a minimal user object for password change flow
        const userData = {
          username: username,
          must_change_password: true,
          roles: roles || []
        };
        console.log('DEBUG: Setting user data for password change:', userData);
        console.log('DEBUG: About to set user state...');
        setUser(userData);
        console.log('DEBUG: User state set, returning success');
        return { success: true, must_change_password: true };
      }
      
      // Only proceed with token and user info if password change is not required
      setToken(access_token);
      localStorage.setItem('access_token', access_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      console.log('DEBUG: Token set, calling /api/user/me');
      // Get user info
      const userResponse = await axios.get('/api/user/me');
      const userData = {
        ...userResponse.data,
        must_change_password,
        roles
      };
      console.log('DEBUG: Setting user data:', userData);
      
      // Set user data BEFORE returning
      setUser(userData);
      
      // Add a small delay to ensure the state is properly set before navigation
      await new Promise(resolve => setTimeout(resolve, 200));
      
      return { success: true, must_change_password };
    } catch (error) {
      console.error('Login failed:', error);
      return { 
        success: false, 
        error: error.response?.data?.error || 'Login failed' 
      };
    }
  };

  const changePassword = async (oldPassword, newPassword, confirmPassword) => {
    try {
      await axios.post('/api/change-password', {
        username: user.username,
        old_password: oldPassword,
        new_password: newPassword,
        confirm_password: confirmPassword
      });
      
      // Update user to remove must_change_password flag
      setUser(prev => ({ ...prev, must_change_password: false }));
      
      return { success: true };
    } catch (error) {
      console.error('Password change failed:', error);
      return { 
        success: false, 
        error: error.response?.data?.error || 'Password change failed' 
      };
    }
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('access_token');
    delete axios.defaults.headers.common['Authorization'];
  };

  const value = {
    user,
    token,
    loading,
    login,
    changePassword,
    logout,
    isAuthenticated: !!user && (!!token || user.must_change_password),
    isAdmin: user?.roles?.includes('admin') || false
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
