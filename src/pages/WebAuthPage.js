import React, { useEffect } from 'react';

const WebAuthPage = () => {
  useEffect(() => {
    // Redirect to the webauth.html file
    window.location.href = '/webauth.html';
  }, []);

  return (
    <div style={{ 
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center', 
      height: '100vh',
      flexDirection: 'column',
      gap: '1rem'
    }}>
      <div style={{ fontSize: '24px' }}>🔐</div>
      <div>Redirecting to authentication page...</div>
    </div>
  );
};

export default WebAuthPage;
