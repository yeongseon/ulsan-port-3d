import { useDataStore } from '@/stores/dataStore';
import {
  BarChart, Bar, LineChart, Line,
  XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer,
} from 'recharts';

const ARRIVALS_DATA = [
  { hour: '06', arrivals: 3 },
  { hour: '08', arrivals: 7 },
  { hour: '10', arrivals: 5 },
  { hour: '12', arrivals: 9 },
  { hour: '14', arrivals: 6 },
  { hour: '16', arrivals: 11 },
  { hour: '18', arrivals: 8 },
  { hour: '20', arrivals: 4 },
];

const CONGESTION_DATA = [
  { time: '00:00', value: 42 },
  { time: '04:00', value: 35 },
  { time: '08:00', value: 58 },
  { time: '12:00', value: 72 },
  { time: '16:00', value: 80 },
  { time: '20:00', value: 65 },
  { time: '23:00', value: 50 },
];

const tooltipStyle = {
  backgroundColor: '#111827',
  border: '1px solid #1f2937',
  borderRadius: '4px',
  color: '#fff',
  fontSize: '11px',
};

export function StatsPanel() {
  const vessels = useDataStore((s) => s.vessels);
  const berths = useDataStore((s) => s.berths);

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
          <BarChart data={ARRIVALS_DATA} margin={{ top: 0, right: 0, bottom: 0, left: -20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
            <XAxis dataKey="hour" tick={{ fill: '#6b7280', fontSize: 9 }} />
            <YAxis tick={{ fill: '#6b7280', fontSize: 9 }} />
            <Tooltip contentStyle={tooltipStyle} />
            <Bar dataKey="arrivals" fill="#3b82f6" radius={[2, 2, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div>
        <p className="text-xs text-port-muted mb-2">항만 혼잡도 추이 (%)</p>
        <ResponsiveContainer width="100%" height={90}>
          <LineChart data={CONGESTION_DATA} margin={{ top: 0, right: 0, bottom: 0, left: -20 }}>
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
