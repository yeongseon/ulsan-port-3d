import axios from 'axios';
import type { Vessel, Berth, WeatherData } from '@/stores/dataStore';

const http = axios.create({
  baseURL: '/api/v1',
  timeout: 10_000,
  headers: { 'Content-Type': 'application/json' },
});

export const apiClient = {
  getVessels: () => http.get<Vessel[]>('/vessels').then((r) => r.data),
  getBerths: () => http.get<Berth[]>('/berths').then((r) => r.data),
  getWeather: () => http.get<WeatherData>('/weather/current').then((r) => r.data),
  getVesselById: (id: string) => http.get<Vessel>(`/vessels/${id}`).then((r) => r.data),
  getBerthById: (id: string) => http.get<Berth>(`/berths/${id}`).then((r) => r.data),
};

export default http;
