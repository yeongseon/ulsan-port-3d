export interface Vessel {
  vessel_id: string;
  name: string;
  call_sign: string;
  imo: string | null;
  ship_type: string;
  gross_tonnage: number | null;
  lat: number;
  lon: number;
  speed: number;
  course: number;
  heading: number;
  draft: number | null;
  updated_at: string;
}

export interface Berth {
  berth_id: string;
  facility_code: string;
  name: string;
  zone_id: string;
  zone_name: string;
  status: BerthStatusType;
  status_detail: string | null;
  operator_id: string | null;
  operator_name: string | null;
  length: number;
  depth: number;
  lat: number;
  lon: number;
  updated_at: string;
}

export type BerthStatusType = 'normal' | 'damaged' | 'unavailable' | 'checking';

export interface Zone {
  zone_id: string;
  name: string;
  type: string;
  berth_count: number;
  geometry_bbox: [number, number, number, number] | null;
}

export interface PortOverview {
  name: string;
  zone_count: number;
  berth_count: number;
  active_vessel_count: number;
  alert_count: number;
  last_updated: string | null;
}

export interface WeatherObservation {
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

export interface WeatherForecast {
  forecast_time: string;
  wind_speed: number;
  wind_dir: number;
  wave_height: number;
  description: string;
}

export interface VesselEvent {
  event_id: string;
  vessel_id: string;
  event_type: 'arrival' | 'departure' | 'berthing' | 'unberthing';
  berth_id: string | null;
  timestamp: string;
  detail: string | null;
}

export interface ArrivalStat {
  month: string;
  zone: string;
  berth: string;
  vessel_count: number;
}

export interface LiquidCargoStat {
  month: string;
  zone: string;
  berth: string;
  cargo_type: string;
  volume_ton: number;
}

export interface CongestionStat {
  date: string;
  waiting_count: number;
  avg_wait_hours: number;
}

export interface Alert {
  alert_id: string;
  type: 'weather' | 'berth' | 'congestion' | 'compound';
  severity: 'info' | 'warning' | 'critical';
  message: string;
  related_entity_type: string | null;
  related_entity_id: string | null;
  created_at: string;
}

export interface GraphNode {
  type: string;
  id: string;
  label: string;
}

export interface GraphRelation {
  type: string;
  target: GraphNode;
}

export interface GraphResponse {
  center: GraphNode;
  relations: GraphRelation[];
}

export interface ScenarioFrame {
  frame_id: string;
  timestamp: string;
  vessel_positions: Vessel[];
  berth_statuses: Berth[];
  weather: WeatherObservation | null;
  alerts: Alert[];
  ai_summary: string | null;
}

export interface Scenario {
  scenario_id: string;
  title: string;
  description: string;
  duration_seconds: number;
  frame_count: number;
}
