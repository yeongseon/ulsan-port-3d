import { Routes, Route } from 'react-router-dom';
import { useEffect, useCallback } from 'react';
import { Header } from '@/components/layout/Header';
import { MainLayout } from '@/components/layout/MainLayout';
import { useDataStore } from '@/stores/dataStore';
import { apiClient } from '@/api/client';
import { useWebSocket } from '@/hooks/useWebSocket';
import type { Vessel } from '@/stores/dataStore';

function PortMonitorApp() {
  const setVessels = useDataStore((s) => s.setVessels);
  const setBerths = useDataStore((s) => s.setBerths);
  const setWeather = useDataStore((s) => s.setWeather);

  useEffect(() => {
    apiClient.getVessels().then(setVessels).catch(() => {
      setVessels(MOCK_VESSELS);
    });
    apiClient.getBerths().then(setBerths).catch(() => {
      setBerths(MOCK_BERTHS);
    });
    apiClient.getWeather().then(setWeather).catch(() => {
      setWeather(MOCK_WEATHER);
    });
  }, [setVessels, setBerths, setWeather]);

  const handleWsMessage = useCallback(
    (data: unknown) => {
      const msg = data as { type: string; payload: unknown };
      if (msg.type === 'vessel_update') {
        setVessels(msg.payload as Vessel[]);
      }
    },
    [setVessels],
  );

  useWebSocket(handleWsMessage);

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

const MOCK_VESSELS = [
  {
    vessel_id: 'v001',
    name: '대한상선 1호',
    call_sign: 'HLAA1',
    lat: 35.503,
    lon: 129.382,
    speed: 3.2,
    course: 145,
    heading: 148,
    ship_type: 'cargo',
    updated_at: new Date().toISOString(),
  },
  {
    vessel_id: 'v002',
    name: '현대타이거',
    call_sign: 'HLBB2',
    lat: 35.498,
    lon: 129.393,
    speed: 0,
    course: 270,
    heading: 270,
    ship_type: 'tanker',
    updated_at: new Date().toISOString(),
  },
  {
    vessel_id: 'v003',
    name: '포스코케미칼 3',
    call_sign: 'HLCC3',
    lat: 35.514,
    lon: 129.365,
    speed: 6.8,
    course: 200,
    heading: 202,
    ship_type: 'container',
    updated_at: new Date().toISOString(),
  },
  {
    vessel_id: 'v004',
    name: '울산항 예인 A',
    call_sign: 'HLDD4',
    lat: 35.506,
    lon: 129.375,
    speed: 4.1,
    course: 90,
    heading: 88,
    ship_type: 'tug',
    updated_at: new Date().toISOString(),
  },
];

const MOCK_BERTHS = [
  {
    berth_id: 'b001',
    facility_code: 'ULS-N1',
    name: '1부두',
    zone: '북항',
    status: 'normal' as const,
    operator: '현대상선',
    length: 250,
    depth: 14,
    lat: 35.511,
    lon: 129.370,
  },
  {
    berth_id: 'b002',
    facility_code: 'ULS-N2',
    name: '2부두',
    zone: '북항',
    status: 'checking' as const,
    operator: '현대상선',
    length: 220,
    depth: 12,
    lat: 35.509,
    lon: 129.374,
  },
  {
    berth_id: 'b003',
    facility_code: 'ULS-S1',
    name: '남항 1부두',
    zone: '남항',
    status: 'damaged' as const,
    operator: '동방항운',
    length: 300,
    depth: 16,
    lat: 35.495,
    lon: 129.376,
  },
  {
    berth_id: 'b004',
    facility_code: 'ULS-OIL-A',
    name: '오일터미널 A',
    zone: '오일터미널',
    status: 'normal' as const,
    operator: 'SK에너지',
    length: 400,
    depth: 20,
    lat: 35.500,
    lon: 129.393,
  },
  {
    berth_id: 'b005',
    facility_code: 'ULS-CT1',
    name: '컨테이너 1부두',
    zone: '컨테이너부두',
    status: 'unavailable' as const,
    operator: '한진해운',
    length: 500,
    depth: 18,
    lat: 35.514,
    lon: 129.362,
  },
];

const MOCK_WEATHER = {
  wind_speed: 7.3,
  wind_dir: 225,
  temperature: 18.4,
  humidity: 71,
  pressure: 1013.2,
  precipitation: 0,
  visibility: 12000,
  wave_height: 0.8,
  observed_at: new Date().toISOString(),
};
