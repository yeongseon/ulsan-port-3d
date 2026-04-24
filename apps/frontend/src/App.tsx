import { Routes, Route } from 'react-router-dom';
import { useEffect, useCallback } from 'react';
import { Header } from '@/components/layout/Header';
import { MainLayout } from '@/components/layout/MainLayout';
import { useDataStore } from '@/stores/dataStore';
import { apiClient } from '@/api/client';
import { useWebSocket } from '@/hooks/useWebSocket';
import type { Vessel } from '@/stores/dataStore';

const isMock = import.meta.env.VITE_USE_MOCK === 'true';

function PortMonitorApp() {
  const setVessels = useDataStore((s) => s.setVessels);
  const setBerths = useDataStore((s) => s.setBerths);
  const setWeather = useDataStore((s) => s.setWeather);

  useEffect(() => {
    apiClient.getVessels().then(setVessels).catch((err) => {
      console.error('Failed to load vessels:', err);
    });
    apiClient.getBerths().then(setBerths).catch((err) => {
      console.error('Failed to load berths:', err);
    });
    apiClient.getWeather().then((weather) => {
      if (weather) {
        setWeather(weather);
      }
    }).catch((err) => {
      console.error('Failed to load weather:', err);
    });
  }, [setVessels, setBerths, setWeather]);

  const handleWsMessage = useCallback(
    (data: unknown) => {
      const msg = data as { event: string; payload: unknown };
      if (msg.event === 'vessel_update') {
        setVessels(msg.payload as Vessel[]);
      }
    },
    [setVessels],
  );

  // Use mock WebSocket in mock mode, real WebSocket otherwise
  useWebSocket(isMock ? () => {} : handleWsMessage);

  useEffect(() => {
    if (!isMock) return;

    let cleanup: (() => void) | undefined;
    import('./mock/mockWebSocket').then(({ startMockWebSocket }) => {
      cleanup = startMockWebSocket(handleWsMessage);
    });

    return () => {
      cleanup?.();
    };
  }, [handleWsMessage]);

  return (
    <div className="h-screen w-screen bg-port-bg text-white flex flex-col overflow-hidden">
      <Header />
      <MainLayout />
    </div>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<PortMonitorApp />} />
    </Routes>
  );
}
