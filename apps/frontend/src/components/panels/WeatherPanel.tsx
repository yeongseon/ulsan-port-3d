import { useDataStore } from '@/stores/dataStore';
import { format } from 'date-fns';
import { ko } from 'date-fns/locale';

function compassDir(deg: number): string {
  const dirs = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'];
  return dirs[Math.round(deg / 22.5) % 16];
}

function Row({ label, value, unit }: { label: string; value: string | number; unit?: string }) {
  return (
    <div className="flex justify-between items-center py-1 border-b border-port-border last:border-0">
      <span className="text-xs text-port-muted">{label}</span>
        <span className="text-sm font-mono text-gray-900">
        {value}
        {unit && <span className="text-port-muted ml-1 text-xs">{unit}</span>}
      </span>
    </div>
  );
}

export function WeatherPanel() {
  const weather = useDataStore((s) => s.weather);

  if (!weather) {
    return (
      <div className="p-3 text-port-muted text-xs animate-pulse">기상 데이터 로딩 중...</div>
    );
  }

  const windBeaufort = Math.min(12, Math.round((weather.wind_speed / 3.6) * 0.82));

  return (
    <div className="p-3 space-y-1">
      <div className="flex items-center gap-2 mb-2">
        <div
          className="w-6 h-6 rounded-full border-2 border-port-accent flex items-center justify-center text-xs"
          style={{ transform: `rotate(${weather.wind_dir}deg)` }}
        >
          ↑
        </div>
        <div>
          <p className="text-sm font-bold text-gray-900">{weather.wind_speed.toFixed(1)} m/s</p>
          <p className="text-xs text-port-muted">{compassDir(weather.wind_dir)} · 뷰포트 {windBeaufort}</p>
        </div>
      </div>

      <Row label="기온" value={weather.temperature.toFixed(1)} unit="°C" />
      <Row label="습도" value={weather.humidity.toFixed(0)} unit="%" />
      <Row label="기압" value={weather.pressure.toFixed(0)} unit="hPa" />
      <Row label="파고" value={weather.wave_height.toFixed(1)} unit="m" />
      <Row label="가시거리" value={(weather.visibility / 1000).toFixed(1)} unit="km" />
      <Row label="강수량" value={weather.precipitation.toFixed(1)} unit="mm" />

      {weather.observed_at && (
        <p className="text-xs text-port-muted pt-1">
          관측: {format(new Date(weather.observed_at), 'HH:mm', { locale: ko })}
        </p>
      )}
    </div>
  );
}
