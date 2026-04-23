import { create } from 'zustand';

export interface Vessel {
  vessel_id: string;
  name: string;
  call_sign: string;
  lat: number;
  lon: number;
  speed: number;
  course: number;
  heading: number;
  ship_type: string;
  updated_at: string;
}

export interface Berth {
  berth_id: string;
  facility_code: string;
  name: string;
  zone: string;
  status: 'normal' | 'damaged' | 'unavailable' | 'checking';
  operator: string;
  length: number;
  depth: number;
  lat: number;
  lon: number;
}

export interface WeatherData {
  wind_speed: number;
  wind_dir: number;
  temperature: number;
  humidity: number;
  pressure: number;
  precipitation: number;
  visibility: number;
  wave_height: number;
  observed_at: string;
}

interface DataState {
  vessels: Vessel[];
  berths: Berth[];
  weather: WeatherData | null;
  setVessels: (vessels: Vessel[]) => void;
  setBerths: (berths: Berth[]) => void;
  setWeather: (weather: WeatherData) => void;
}

export const useDataStore = create<DataState>((set) => ({
  vessels: [],
  berths: [],
  weather: null,
  setVessels: (vessels) => set({ vessels }),
  setBerths: (berths) => set({ berths }),
  setWeather: (weather) => set({ weather }),
}));
