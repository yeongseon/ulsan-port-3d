import axios from 'axios';
import type { Vessel, Berth, WeatherData } from '@/stores/dataStore';

type BackendBerth = {
  berth_id: string;
  facility_code: string;
  name: string;
  zone_name?: string | null;
  latest_status?: string | null;
  operator_name?: string | null;
  length?: number | null;
  depth?: number | null;
  latitude?: number | null;
  longitude?: number | null;
};

function toBerthStatus(status: BackendBerth['latest_status']): Berth['status'] {
  return status === 'damaged' || status === 'unavailable' || status === 'checking'
    ? status
    : 'normal';
}

const http = axios.create({
  baseURL: '/api/v1',
  timeout: 10_000,
  headers: { 'Content-Type': 'application/json' },
});

export const apiClient = {
  getVessels: () =>
    http.get('/vessels').then((r) =>
      (Array.isArray(r.data) ? r.data : []).map((v: Record<string, unknown>) => ({
        vessel_id: String(v.vessel_id ?? ''),
        name: String(v.name ?? ''),
        call_sign: String(v.call_sign ?? ''),
        lat: Number(v.lat ?? 0),
        lon: Number(v.lon ?? 0),
        speed: Number(v.speed ?? 0),
        course: Number(v.course ?? 0),
        heading: Number(v.heading ?? 0),
        ship_type: String(v.ship_type ?? ''),
        updated_at: String(v.updated_at ?? v.observed_at ?? new Date().toISOString()),
      } as Vessel)),
    ),
  getBerths: () =>
    http.get<BackendBerth[]>('/berths').then((r) =>
      r.data.map(
        (b) =>
          ({
            berth_id: b.berth_id,
            facility_code: b.facility_code,
            name: b.name,
            zone: b.zone_name ?? '',
            status: toBerthStatus(b.latest_status),
            operator: b.operator_name ?? '',
            length: b.length ?? 0,
            depth: b.depth ?? 0,
            lat: b.latitude ?? 0,
            lon: b.longitude ?? 0,
          }) as Berth,
      ),
    ),
  getWeather: () =>
    http.get('/weather/current').then((r) => {
      const obs = (r.data as { observation?: Partial<WeatherData> | null } | null)?.observation;
      if (!obs) return null;

      return {
        wind_speed: obs.wind_speed ?? 0,
        wind_dir: obs.wind_dir ?? 0,
        temperature: obs.temperature ?? 0,
        humidity: obs.humidity ?? 0,
        pressure: obs.pressure ?? 0,
        precipitation: obs.precipitation ?? 0,
        visibility: obs.visibility ?? 0,
        wave_height: obs.wave_height ?? 0,
        observed_at: obs.observed_at ?? new Date().toISOString(),
      } as WeatherData;
    }),
  getVesselById: (id: string) =>
    http.get(`/vessels/${id}`).then((r) => {
      const d = r.data as Record<string, unknown>;
      const pos = (d.latest_position ?? d) as Record<string, unknown>;
      return {
        vessel_id: String(pos.vessel_id ?? d.vessel_id ?? ''),
        name: String(pos.name ?? ''),
        call_sign: String(pos.call_sign ?? ''),
        lat: Number(pos.lat ?? 0),
        lon: Number(pos.lon ?? 0),
        speed: Number(pos.speed ?? 0),
        course: Number(pos.course ?? 0),
        heading: Number(pos.heading ?? 0),
        ship_type: String(pos.ship_type ?? ''),
        updated_at: String(pos.updated_at ?? pos.observed_at ?? new Date().toISOString()),
      } as Vessel;
    }),
  getBerthById: (id: string) =>
    http.get<BackendBerth>(`/berths/${id}`).then((r) => {
      const b = r.data;
      return {
        berth_id: b.berth_id,
        facility_code: b.facility_code,
        name: b.name,
        zone: b.zone_name ?? '',
        status: toBerthStatus(b.latest_status),
        operator: b.operator_name ?? '',
        length: b.length ?? 0,
        depth: b.depth ?? 0,
        lat: b.latitude ?? 0,
        lon: b.longitude ?? 0,
      } as Berth;
    }),
  getInsights: () => http.get('/insights/current').then((r) => r.data),
  getAlerts: () => http.get('/alerts').then((r) => r.data),
  getScenarios: () => http.get('/scenarios').then((r) => r.data),
  getScenarioFrames: (id: string) => http.get(`/scenarios/${id}/frames`).then((r) => r.data),
  getGraph: (type: string, id: string) => http.get(`/graph/${type}/${id}`).then((r) => r.data),
  getStats: () => http.get('/stats/arrivals').then((r) => r.data),
  getCongestion: () => http.get('/stats/congestion').then((r) => r.data),
};

export default http;
