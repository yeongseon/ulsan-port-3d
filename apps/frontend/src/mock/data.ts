import type { Berth, Vessel, WeatherData } from '@/stores/dataStore';

export type MockAlert = {
  alert_id: string;
  severity: 'info' | 'warning' | 'critical';
  message: string;
};

export type MockArrivalStat = {
  year_month: string;
  vessel_count: number;
};

export type MockCongestionStat = {
  stat_date: string;
  waiting_count: number;
  avg_wait_hours: number;
};

export type MockInsight = {
  insight_id: string;
  category: string;
  title: string;
  description: string;
};

export type EntityGraphResponse = {
  center: { type: 'Vessel'; id: string; label: string };
  relations: Array<{
    predicate: string;
    direction: 'outgoing';
    node: { type: string; id: string; label: string };
  }>;
};

export type MockScenarioSummary = {
  scenario_id: string;
  frame_count: number;
  first_frame_index: number;
  last_frame_index: number;
  first_timestamp: string;
  last_timestamp: string;
  is_simulated: boolean;
  name?: string;
  description?: string;
};

export type MockScenarioFrame = {
  frame_id: string;
  label: string;
  timestamp: string;
  summary: string;
};

const baseTimestamp = '2025-04-24T02:15:00.000Z';

export const mockVessels: Vessel[] = [
  {
    vessel_id: 'vsl-001',
    name: '한진부산',
    call_sign: 'D7HJ1',
    lat: 35.5112,
    lon: 129.3694,
    speed: 1.8,
    course: 82,
    heading: 79,
    ship_type: 'cargo',
    updated_at: baseTimestamp,
  },
  {
    vessel_id: 'vsl-002',
    name: '현대울산',
    call_sign: 'DSHU2',
    lat: 35.5096,
    lon: 129.3732,
    speed: 0.9,
    course: 65,
    heading: 62,
    ship_type: 'container',
    updated_at: baseTimestamp,
  },
  {
    vessel_id: 'vsl-003',
    name: '울산호',
    call_sign: 'D7UL3',
    lat: 35.5078,
    lon: 129.3774,
    speed: 4.3,
    course: 118,
    heading: 121,
    ship_type: 'passenger',
    updated_at: baseTimestamp,
  },
  {
    vessel_id: 'vsl-004',
    name: 'SK에너지1호',
    call_sign: 'DSKE4',
    lat: 35.5008,
    lon: 129.3921,
    speed: 0.5,
    course: 179,
    heading: 183,
    ship_type: 'tanker',
    updated_at: baseTimestamp,
  },
  {
    vessel_id: 'vsl-005',
    name: '대한마리너',
    call_sign: 'DHKM5',
    lat: 35.4987,
    lon: 129.3963,
    speed: 0.3,
    course: 201,
    heading: 198,
    ship_type: 'tanker',
    updated_at: baseTimestamp,
  },
  {
    vessel_id: 'vsl-006',
    name: '태화드림',
    call_sign: 'DTTW6',
    lat: 35.4958,
    lon: 129.3751,
    speed: 2.2,
    course: 37,
    heading: 35,
    ship_type: 'cargo',
    updated_at: baseTimestamp,
  },
  {
    vessel_id: 'vsl-007',
    name: '남항스타',
    call_sign: 'DHNS7',
    lat: 35.4941,
    lon: 129.3803,
    speed: 1.4,
    course: 52,
    heading: 49,
    ship_type: 'cargo',
    updated_at: baseTimestamp,
  },
  {
    vessel_id: 'vsl-008',
    name: '한화터미널호',
    call_sign: 'DHTM8',
    lat: 35.5034,
    lon: 129.3854,
    speed: 3.1,
    course: 147,
    heading: 150,
    ship_type: 'container',
    updated_at: baseTimestamp,
  },
  {
    vessel_id: 'vsl-009',
    name: '문수피닉스',
    call_sign: 'DMSP9',
    lat: 35.5054,
    lon: 129.3811,
    speed: 2.7,
    course: 130,
    heading: 132,
    ship_type: 'cargo',
    updated_at: baseTimestamp,
  },
  {
    vessel_id: 'vsl-010',
    name: '온산퀸',
    call_sign: 'DONQ0',
    lat: 35.5071,
    lon: 129.3598,
    speed: 7.8,
    course: 96,
    heading: 94,
    ship_type: 'passenger',
    updated_at: baseTimestamp,
  },
  {
    vessel_id: 'vsl-011',
    name: '대왕예인',
    call_sign: 'DDWG1',
    lat: 35.5126,
    lon: 129.3628,
    speed: 5.2,
    course: 22,
    heading: 18,
    ship_type: 'tug',
    updated_at: baseTimestamp,
  },
  {
    vessel_id: 'vsl-012',
    name: '방어진예인',
    call_sign: 'DBJE2',
    lat: 35.5144,
    lon: 129.3664,
    speed: 4.6,
    course: 11,
    heading: 14,
    ship_type: 'tug',
    updated_at: baseTimestamp,
  },
  {
    vessel_id: 'vsl-013',
    name: '동해컨테이너',
    call_sign: 'DDHC3',
    lat: 35.5104,
    lon: 129.3678,
    speed: 6.4,
    course: 74,
    heading: 77,
    ship_type: 'container',
    updated_at: baseTimestamp,
  },
  {
    vessel_id: 'vsl-014',
    name: '청해탱커',
    call_sign: 'DCHT4',
    lat: 35.4993,
    lon: 129.3906,
    speed: 1.1,
    course: 214,
    heading: 218,
    ship_type: 'tanker',
    updated_at: baseTimestamp,
  },
  {
    vessel_id: 'vsl-015',
    name: '미포그레이스',
    call_sign: 'DMPG5',
    lat: 35.5062,
    lon: 129.3724,
    speed: 3.9,
    course: 103,
    heading: 106,
    ship_type: 'cargo',
    updated_at: baseTimestamp,
  },
];

export const mockBerths: Berth[] = [
  {
    berth_id: 'berth-001',
    facility_code: 'ULS-B01',
    name: '1부두',
    zone: '북항 일반화물',
    status: 'normal',
    operator: '울산항만공사',
    length: 30,
    depth: 20,
    lat: 35.511,
    lon: 129.37,
  },
  {
    berth_id: 'berth-002',
    facility_code: 'ULS-B02',
    name: '2부두',
    zone: '북항 일반화물',
    status: 'checking',
    operator: '울산항만공사',
    length: 28,
    depth: 22,
    lat: 35.509,
    lon: 129.374,
  },
  {
    berth_id: 'berth-003',
    facility_code: 'ULS-B03',
    name: '3부두',
    zone: '북항 다목적',
    status: 'normal',
    operator: '대한해운터미널',
    length: 32,
    depth: 18,
    lat: 35.507,
    lon: 129.378,
  },
  {
    berth_id: 'berth-004',
    facility_code: 'ULS-B04',
    name: '4부두',
    zone: '북항 다목적',
    status: 'normal',
    operator: '현대항만서비스',
    length: 35,
    depth: 25,
    lat: 35.505,
    lon: 129.382,
  },
  {
    berth_id: 'berth-005',
    facility_code: 'ULS-B05',
    name: '5부두',
    zone: '북항 지원부두',
    status: 'damaged',
    operator: '울산동방물류',
    length: 30,
    depth: 20,
    lat: 35.503,
    lon: 129.386,
  },
  {
    berth_id: 'berth-006',
    facility_code: 'ULS-S01',
    name: '남항 1',
    zone: '남항 벌크',
    status: 'normal',
    operator: '남항벌크터미널',
    length: 40,
    depth: 28,
    lat: 35.495,
    lon: 129.376,
  },
  {
    berth_id: 'berth-007',
    facility_code: 'ULS-S02',
    name: '남항 2',
    zone: '남항 벌크',
    status: 'checking',
    operator: '남항벌크터미널',
    length: 38,
    depth: 26,
    lat: 35.493,
    lon: 129.381,
  },
  {
    berth_id: 'berth-008',
    facility_code: 'ULS-OA1',
    name: '오일터미널 A',
    zone: '액체화물',
    status: 'normal',
    operator: 'SK에너지',
    length: 50,
    depth: 35,
    lat: 35.5,
    lon: 129.393,
  },
  {
    berth_id: 'berth-009',
    facility_code: 'ULS-OB1',
    name: '오일터미널 B',
    zone: '액체화물',
    status: 'normal',
    operator: 'S-OIL',
    length: 50,
    depth: 35,
    lat: 35.498,
    lon: 129.397,
  },
  {
    berth_id: 'berth-010',
    facility_code: 'ULS-KT1',
    name: '케테일러 1',
    zone: '북항 지원시설',
    status: 'normal',
    operator: '울산컨테이너지원',
    length: 60,
    depth: 40,
    lat: 35.514,
    lon: 129.362,
  },
  {
    berth_id: 'berth-011',
    facility_code: 'ULS-KT2',
    name: '케테일러 2',
    zone: '북항 지원시설',
    status: 'normal',
    operator: '울산컨테이너지원',
    length: 60,
    depth: 40,
    lat: 35.512,
    lon: 129.366,
  },
  {
    berth_id: 'berth-012',
    facility_code: 'ULS-P01',
    name: '여객터미널',
    zone: '연안여객',
    status: 'normal',
    operator: '울산연안여객',
    length: 45,
    depth: 30,
    lat: 35.507,
    lon: 129.36,
  },
];

export const mockWeather: WeatherData = {
  wind_speed: 5.4,
  wind_dir: 138,
  temperature: 15.6,
  humidity: 63,
  pressure: 1014.2,
  precipitation: 0,
  visibility: 10.4,
  wave_height: 0.8,
  observed_at: baseTimestamp,
};

export const mockAlerts: MockAlert[] = [
  { alert_id: 'alert-001', severity: 'info', message: '2부두 점검 작업 진행 중' },
  { alert_id: 'alert-002', severity: 'warning', message: '남항 구역 풍속 주의보' },
  { alert_id: 'alert-003', severity: 'warning', message: '오일터미널 B 접안 대기 선박 증가' },
  { alert_id: 'alert-004', severity: 'critical', message: '5부두 접안 시설 손상으로 운영 제한' },
];

export const mockArrivalStats: MockArrivalStat[] = [
  { year_month: '2025-01', vessel_count: 182 },
  { year_month: '2025-02', vessel_count: 176 },
  { year_month: '2025-03', vessel_count: 201 },
  { year_month: '2025-04', vessel_count: 214 },
  { year_month: '2025-05', vessel_count: 228 },
  { year_month: '2025-06', vessel_count: 236 },
  { year_month: '2025-07', vessel_count: 247 },
  { year_month: '2025-08', vessel_count: 259 },
  { year_month: '2025-09', vessel_count: 231 },
  { year_month: '2025-10', vessel_count: 218 },
  { year_month: '2025-11', vessel_count: 205 },
  { year_month: '2025-12', vessel_count: 193 },
];

export const mockCongestionStats: MockCongestionStat[] = [
  { stat_date: '2025-04-18', waiting_count: 5, avg_wait_hours: 2.1 },
  { stat_date: '2025-04-19', waiting_count: 6, avg_wait_hours: 2.4 },
  { stat_date: '2025-04-20', waiting_count: 4, avg_wait_hours: 1.8 },
  { stat_date: '2025-04-21', waiting_count: 7, avg_wait_hours: 3.2 },
  { stat_date: '2025-04-22', waiting_count: 8, avg_wait_hours: 3.6 },
  { stat_date: '2025-04-23', waiting_count: 6, avg_wait_hours: 2.9 },
  { stat_date: '2025-04-24', waiting_count: 5, avg_wait_hours: 2.3 },
];

export const mockInsights: MockInsight[] = [
  {
    insight_id: 'insight-001',
    category: 'operations',
    title: '북항 작업 효율 안정',
    description: '북항 일반화물 구역의 선석 회전율이 지난주 대비 개선되어 대기 선박이 감소했습니다.',
  },
  {
    insight_id: 'insight-002',
    category: 'safety',
    title: '남항 풍속 모니터링 필요',
    description: '남항 구역의 순간 풍속이 상승하고 있어 예인선 배치와 접안 속도 조정이 권고됩니다.',
  },
  {
    insight_id: 'insight-003',
    category: 'maintenance',
    title: '5부두 보수 일정 조정',
    description: '5부두 접안 시설 보수로 일부 화물선이 3부두와 남항 1로 분산 배정되고 있습니다.',
  },
];

export const mockGraph: EntityGraphResponse = {
  center: { type: 'Vessel', id: 'vsl-001', label: '한진부산' },
  relations: [
    {
      predicate: 'hasPosition',
      direction: 'outgoing',
      node: { type: 'WeatherObservation', id: 'obs-ulsan-20250424', label: '울산항 기상관측 02:15Z' },
    },
    {
      predicate: 'hasVoyageCall',
      direction: 'outgoing',
      node: { type: 'VoyageCall', id: 'voyagecall-2025-001', label: '2025 입항 호출 001' },
    },
    {
      predicate: 'usesFacility',
      direction: 'outgoing',
      node: { type: 'Berth', id: 'berth-001', label: '1부두' },
    },
    {
      predicate: 'operatedBy',
      direction: 'outgoing',
      node: { type: 'Operator', id: 'operator-hanjin', label: '한진해운터미널' },
    },
    {
      predicate: 'locatedIn',
      direction: 'outgoing',
      node: { type: 'PortZone', id: 'zone-north-harbor', label: '북항 일반화물' },
    },
    {
      predicate: 'carriesCargo',
      direction: 'outgoing',
      node: { type: 'CargoType', id: 'cargo-steel', label: '철강 제품' },
    },
  ],
};

export const mockScenarios: MockScenarioSummary[] = [
  {
    scenario_id: 'scenario-eta-surge',
    frame_count: 6,
    first_frame_index: 0,
    last_frame_index: 5,
    first_timestamp: '2025-04-24T01:00:00.000Z',
    last_timestamp: '2025-04-24T03:30:00.000Z',
    is_simulated: true,
    name: '입항 집중 대응',
    description: '북항과 남항에 입항 수요가 몰릴 때 선석과 예인선 배치를 조정하는 시뮬레이션입니다.',
  },
  {
    scenario_id: 'scenario-southwind-response',
    frame_count: 5,
    first_frame_index: 0,
    last_frame_index: 4,
    first_timestamp: '2025-04-24T04:00:00.000Z',
    last_timestamp: '2025-04-24T06:00:00.000Z',
    is_simulated: true,
    name: '남항 강풍 대응',
    description: '남항 강풍 시 접안 제한과 대체 선석 배정을 검토하는 운영 시나리오입니다.',
  },
];

export const mockScenarioFrames: Record<string, MockScenarioFrame[]> = {
  'scenario-eta-surge': [
    {
      frame_id: 'scenario-eta-surge-0',
      label: '접안 수요 증가 감지',
      timestamp: '2025-04-24T01:00:00.000Z',
      summary: '북항 입항 예정 선박이 집중되며 1부두와 3부두 대기 수요가 증가합니다.',
    },
    {
      frame_id: 'scenario-eta-surge-1',
      label: '예인선 재배치',
      timestamp: '2025-04-24T01:30:00.000Z',
      summary: '대왕예인과 방어진예인이 북항 지원을 위해 재배치됩니다.',
    },
    {
      frame_id: 'scenario-eta-surge-2',
      label: '남항 분산 운영',
      timestamp: '2025-04-24T02:00:00.000Z',
      summary: '일부 벌크 화물선을 남항 1로 분산 배정하여 혼잡을 완화합니다.',
    },
    {
      frame_id: 'scenario-eta-surge-3',
      label: '오일터미널 우선순위 조정',
      timestamp: '2025-04-24T02:30:00.000Z',
      summary: '탱커 접안 우선순위를 조정해 오일터미널 대기 시간을 최소화합니다.',
    },
    {
      frame_id: 'scenario-eta-surge-4',
      label: '북항 회전율 회복',
      timestamp: '2025-04-24T03:00:00.000Z',
      summary: '2부두 점검 범위 축소 후 북항 선석 회전율이 안정권으로 돌아옵니다.',
    },
    {
      frame_id: 'scenario-eta-surge-5',
      label: '대기 해소',
      timestamp: '2025-04-24T03:30:00.000Z',
      summary: '집중 입항 구간이 종료되며 평균 대기 시간이 2시간 이하로 내려갑니다.',
    },
  ],
  'scenario-southwind-response': [
    {
      frame_id: 'scenario-southwind-response-0',
      label: '남항 강풍 예보',
      timestamp: '2025-04-24T04:00:00.000Z',
      summary: '남항 구역 남동풍이 강해질 것으로 예보되어 접안 제한 검토가 시작됩니다.',
    },
    {
      frame_id: 'scenario-southwind-response-1',
      label: '풍속 경보 발령',
      timestamp: '2025-04-24T04:30:00.000Z',
      summary: '남항 2 접안 작업을 점검 상태로 전환하고 예인선 대기를 확대합니다.',
    },
    {
      frame_id: 'scenario-southwind-response-2',
      label: '여객터미널 안전 통제',
      timestamp: '2025-04-24T05:00:00.000Z',
      summary: '연안여객 선박의 접근 속도를 낮추고 터미널 주변 안전 반경을 확장합니다.',
    },
    {
      frame_id: 'scenario-southwind-response-3',
      label: '대체 선석 배정',
      timestamp: '2025-04-24T05:30:00.000Z',
      summary: '남항 대기 선박 일부를 3부두와 4부두로 전환 배정합니다.',
    },
    {
      frame_id: 'scenario-southwind-response-4',
      label: '운영 정상화 준비',
      timestamp: '2025-04-24T06:00:00.000Z',
      summary: '풍속 약화가 확인되어 남항 선석 운영 정상화 준비에 들어갑니다.',
    },
  ],
};
