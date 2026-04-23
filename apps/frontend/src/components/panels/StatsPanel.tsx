import { useEffect, useState } from 'react';
import { useDataStore } from '@/stores/dataStore';
import { apiClient } from '@/api/client';
import {
  BarChart, Bar, LineChart, Line,
  XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer,
} from 'recharts';

type ArrivalDatum = {
  hour: string;
  arrivals: number;
};

type CongestionDatum = {
  time: string;
  value: number;
};

const tooltipStyle = {
  backgroundColor: '#111827',
  border: '1px solid #1f2937',
  borderRadius: '4px',
  color: '#fff',
  fontSize: '11px',
};

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null;
}

function getString(value: unknown, fallback = ''): string {
  return typeof value === 'string' ? value : fallback;
}

function getNumber(value: unknown, fallback = 0): number {
  return typeof value === 'number' && Number.isFinite(value) ? value : fallback;
}

function normalizeArray(payload: unknown): unknown[] {
  if (Array.isArray(payload)) return payload;
  if (!isRecord(payload)) return [];

  const nested = payload.data ?? payload.items ?? payload.results ?? payload.series;
  return Array.isArray(nested) ? nested : [];
}

function normalizeArrivals(payload: unknown): ArrivalDatum[] {
  return normalizeArray(payload)
    .map((entry) => {
      if (!isRecord(entry)) return null;

      return {
        hour: getString(entry.hour ?? entry.year_month ?? entry.time ?? entry.label, '00'),
        arrivals: getNumber(entry.arrivals ?? entry.vessel_count ?? entry.value ?? entry.count),
      };
    })
    .filter((entry): entry is ArrivalDatum => entry !== null);
}

function normalizeCongestion(payload: unknown): CongestionDatum[] {
  return normalizeArray(payload)
    .map((entry) => {
      if (!isRecord(entry)) return null;

      return {
        time: getString(entry.time ?? entry.stat_date ?? entry.hour ?? entry.label, '00:00'),
        value: getNumber(entry.value ?? entry.waiting_count ?? entry.avg_wait_hours ?? entry.congestion ?? entry.rate),
      };
    })
    .filter((entry): entry is CongestionDatum => entry !== null);
}

export function StatsPanel() {
  const vessels = useDataStore((s) => s.vessels);
  const berths = useDataStore((s) => s.berths);
  const [arrivalsData, setArrivalsData] = useState<ArrivalDatum[]>([]);
  const [congestionData, setCongestionData] = useState<CongestionDatum[]>([]);

  useEffect(() => {
    let isMounted = true;

    apiClient.getStats()
      .then((payload) => {
        if (isMounted) {
          setArrivalsData(normalizeArrivals(payload));
        }
      })
      .catch((err) => {
        console.error('Failed to load arrival stats:', err);
        if (isMounted) {
          setArrivalsData([]);
        }
      });

    apiClient.getCongestion()
      .then((payload) => {
        if (isMounted) {
          setCongestionData(normalizeCongestion(payload));
        }
      })
      .catch((err) => {
        console.error('Failed to load congestion stats:', err);
        if (isMounted) {
          setCongestionData([]);
        }
      });

    return () => {
      isMounted = false;
    };
  }, []);

  const totalVessels = vessels.length;
  const normalBerths = berths.filter((b) => b.status === 'normal').length;
  const occupancyRate = berths.length > 0 ? Math.round((normalBerths / berths.length) * 100) : 0;

  return (
    <div className="p-3 space-y-4">
      <div className="grid grid-cols-3 gap-2">
        <StatCard label="입항 선박" value={totalVessels} unit="척" color="text-port-accent" />
        <StatCard label="정상 부두" value={normalBerths} unit="개" color="text-port-success" />
        <StatCard label="부두 가동률" value={occupancyRate} unit="%" color="text-port-warning" />
      </div>

      <div>
        <p className="text-xs text-port-muted mb-2">시간대별 입항 (척)</p>
        <ResponsiveContainer width="100%" height={100}>
          <BarChart data={arrivalsData} margin={{ top: 0, right: 0, bottom: 0, left: -20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
            <XAxis dataKey="hour" tick={{ fill: '#6b7280', fontSize: 9 }} />
            <YAxis tick={{ fill: '#6b7280', fontSize: 9 }} />
            <Tooltip contentStyle={tooltipStyle} />
            <Bar dataKey="arrivals" fill="#3b82f6" radius={[2, 2, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
        {arrivalsData.length === 0 && <p className="mt-1 text-[11px] text-port-muted">입항 통계 데이터 없음</p>}
      </div>

      <div>
        <p className="text-xs text-port-muted mb-2">항만 혼잡도 추이 (%)</p>
        <ResponsiveContainer width="100%" height={90}>
          <LineChart data={congestionData} margin={{ top: 0, right: 0, bottom: 0, left: -20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
            <XAxis dataKey="time" tick={{ fill: '#6b7280', fontSize: 9 }} />
            <YAxis tick={{ fill: '#6b7280', fontSize: 9 }} domain={[0, 100]} />
            <Tooltip contentStyle={tooltipStyle} />
            <Line
              type="monotone"
              dataKey="value"
              stroke="#f59e0b"
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
        {congestionData.length === 0 && <p className="mt-1 text-[11px] text-port-muted">혼잡도 데이터 없음</p>}
      </div>
    </div>
  );
}

function StatCard({ label, value, unit, color }: {
  label: string;
  value: number;
  unit: string;
  color: string;
}) {
  return (
    <div className="bg-port-bg rounded p-2 text-center">
      <p className={`text-lg font-bold font-mono ${color}`}>{value}</p>
      <p className="text-xs text-port-muted">{unit}</p>
      <p className="text-xs text-port-muted mt-0.5 leading-tight">{label}</p>
    </div>
  );
}
