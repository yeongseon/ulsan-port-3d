import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import './index.css';

const basename = import.meta.env.BASE_URL.replace(/\/$/, '') || '/';

async function boot() {
  if (import.meta.env.VITE_USE_MOCK === 'true') {
    const { enableMocks } = await import('./mock');
    enableMocks();
  }

  ReactDOM.createRoot(document.getElementById('root')!).render(
    <React.StrictMode>
      <BrowserRouter basename={basename}>
        <App />
      </BrowserRouter>
    </React.StrictMode>,
  );
}

boot();
