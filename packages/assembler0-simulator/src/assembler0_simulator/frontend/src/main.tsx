import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import 'antd/dist/reset.css';

// Apply cyberpunk background to body
document.body.style.background =
  'linear-gradient(135deg, #0a0a14 0%, #1a0a2a 100%)';
document.body.style.margin = '0';
document.body.style.minHeight = '100vh';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
