import React, { useState } from 'react';
import {
  Container,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  Button,
  Chip,
  Divider,
  Alert,
  CircularProgress,
  AppBar,
  Toolbar,
  IconButton,
  Menu,
  MenuItem,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  AdminPanelSettings,
  Security,
  Logout,
  AccountCircle,
  OpenInNew,
  CheckCircle,
  Info
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const DashboardPage = () => {
  const { user, logout, isAdmin } = useAuth();
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = useState(null);
  const [users, setUsers] = useState([]);
  const [loadingUsers, setLoadingUsers] = useState(false);
  const [error, setError] = useState('');

  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleKeycloakAccess = () => {
    // Keycloak admin console requires direct access with master realm admin credentials
    // The JWT token from our app won't work for Keycloak admin console
    window.open('/auth', '_blank');
  };

  const fetchUsers = async () => {
    if (!isAdmin) return;
    
    setLoadingUsers(true);
    setError('');
    
    try {
      const response = await axios.get('/api/admin/users');
      setUsers(response.data);
    } catch (err) {
      setError('Failed to fetch users');
      console.error('Error fetching users:', err);
    } finally {
      setLoadingUsers(false);
    }
  };

  React.useEffect(() => {
    if (isAdmin) {
      fetchUsers();
    }
  }, [isAdmin]);

  return (
    <Box sx={{ flexGrow: 1 }}>
      {/* App Bar */}
      <AppBar position="static">
        <Toolbar>
          <DashboardIcon sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Keycloak Dashboard
          </Typography>
          <IconButton
            size="large"
            edge="end"
            color="inherit"
            onClick={handleMenuOpen}
          >
            <AccountCircle />
          </IconButton>
          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleMenuClose}
          >
            <MenuItem onClick={handleLogout}>
              <ListItemIcon>
                <Logout fontSize="small" />
              </ListItemIcon>
              <ListItemText>Logout</ListItemText>
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        {/* Welcome Section */}
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <CheckCircle sx={{ fontSize: 40, color: 'success.main', mr: 2 }} />
              <Box>
                <Typography variant="h4" component="h1" gutterBottom>
                  Welcome to the Dashboard!
                </Typography>
                <Typography variant="h6" color="text.secondary">
                  Hello, {user?.username}! You are successfully authenticated.
                </Typography>
              </Box>
            </Box>
            
            <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
              {user?.roles?.map((role) => (
                <Chip
                  key={role}
                  label={role}
                  color={role === 'admin' ? 'primary' : 'default'}
                  icon={role === 'admin' ? <AdminPanelSettings /> : <Security />}
                />
              ))}
            </Box>
          </CardContent>
        </Card>

        {/* Keycloak Access Section */}
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h5" gutterBottom>
              <AdminPanelSettings sx={{ mr: 1, verticalAlign: 'middle' }} />
              Keycloak Administration
            </Typography>
            <Typography variant="body1" color="text.secondary" paragraph>
              As an admin user, you can access the Keycloak administration console to manage users, 
              roles, and other security settings. The Keycloak console requires separate authentication 
              with the master realm admin credentials (admin/admin).
            </Typography>
            
            {isAdmin ? (
              <Alert severity="success" sx={{ mb: 2 }}>
                <strong>Admin Access Granted:</strong> You have admin privileges and can access Keycloak.
              </Alert>
            ) : (
              <Alert severity="warning" sx={{ mb: 2 }}>
                <strong>Limited Access:</strong> You don't have admin privileges to access Keycloak.
              </Alert>
            )}

            <Button
              variant="contained"
              color="primary"
              startIcon={<OpenInNew />}
              onClick={handleKeycloakAccess}
              disabled={!isAdmin}
              sx={{ mr: 2 }}
            >
              Open Keycloak Console
            </Button>
            
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          Access URL: <code>/auth</code> (requires master realm admin: admin/admin)
        </Typography>
          </CardContent>
        </Card>

        {/* User Information Section */}
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h5" gutterBottom>
              <AccountCircle sx={{ mr: 1, verticalAlign: 'middle' }} />
              User Information
            </Typography>
            <List>
              <ListItem>
                <ListItemText
                  primary="Username"
                  secondary={user?.username}
                />
              </ListItem>
              <ListItem>
                <ListItemText
                  primary="Email"
                  secondary={user?.email || 'Not provided'}
                />
              </ListItem>
              <ListItem>
                <ListItemText
                  primary="First Name"
                  secondary={user?.first_name || 'Not provided'}
                />
              </ListItem>
              <ListItem>
                <ListItemText
                  primary="Last Name"
                  secondary={user?.last_name || 'Not provided'}
                />
              </ListItem>
              <ListItem>
                <ListItemText
                  primary="Roles"
                  secondary={user?.roles?.join(', ') || 'No roles assigned'}
                />
              </ListItem>
            </List>
          </CardContent>
        </Card>

        {/* Admin Users Section */}
        {isAdmin && (
          <Card>
            <CardContent>
              <Typography variant="h5" gutterBottom>
                <AdminPanelSettings sx={{ mr: 1, verticalAlign: 'middle' }} />
                System Users
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                List of all users in the system (Admin only)
              </Typography>

              {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {error}
                </Alert>
              )}

              <Button
                variant="outlined"
                onClick={fetchUsers}
                disabled={loadingUsers}
                sx={{ mb: 2 }}
              >
                {loadingUsers ? <CircularProgress size={20} /> : 'Refresh Users'}
              </Button>

              {users.length > 0 && (
                <Paper variant="outlined">
                  <List>
                    {users.map((systemUser, index) => (
                      <React.Fragment key={systemUser.id}>
                        <ListItem>
                          <ListItemIcon>
                            <AccountCircle />
                          </ListItemIcon>
                          <ListItemText
                            primary={systemUser.username}
                            secondary={`${systemUser.firstName || ''} ${systemUser.lastName || ''}`.trim() || 'No name provided'}
                          />
                          <ListItemSecondaryAction>
                            <Chip
                              label={systemUser.enabled ? 'Active' : 'Disabled'}
                              color={systemUser.enabled ? 'success' : 'default'}
                              size="small"
                            />
                          </ListItemSecondaryAction>
                        </ListItem>
                        {index < users.length - 1 && <Divider />}
                      </React.Fragment>
                    ))}
                  </List>
                </Paper>
              )}

              {users.length === 0 && !loadingUsers && (
                <Alert severity="info">
                  No users found. This might indicate a connection issue with Keycloak.
                </Alert>
              )}
            </CardContent>
          </Card>
        )}

        {/* System Information */}
        <Card sx={{ mt: 3 }}>
          <CardContent>
            <Typography variant="h5" gutterBottom>
              <Info sx={{ mr: 1, verticalAlign: 'middle' }} />
              System Information
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              This application is integrated with Keycloak for authentication and authorization.
              The system uses JWT tokens for secure API communication and HAProxy for load balancing.
            </Typography>
            <Box sx={{ mt: 2 }}>
              <Typography variant="body2">
                <strong>Authentication Status:</strong> ✅ Authenticated<br />
                <strong>Token Type:</strong> JWT (JSON Web Token)<br />
                <strong>Admin Access:</strong> {isAdmin ? '✅ Granted' : '❌ Not granted'}<br />
                <strong>Keycloak Console:</strong> Available at <code>/auth</code>
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Container>
    </Box>
  );
};

export default DashboardPage;
