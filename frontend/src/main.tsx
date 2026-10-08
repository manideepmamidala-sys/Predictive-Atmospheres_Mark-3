import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider } from './design/ThemeProvider';
import App from './App';
import './design/tokens.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode><ThemeProvider><BrowserRouter><App /></BrowserRouter></ThemeProvider></React.StrictMode>,
);
