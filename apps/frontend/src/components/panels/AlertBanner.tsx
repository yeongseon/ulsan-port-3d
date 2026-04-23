import { useState } from 'react';

interface Alert {
  id: string;
  level: 'warning' | 'danger' | 'info';
  message: string;
}

const SAMPLE_ALERTS: Alert[] = [
  { id: '1', level: 'warning', message: '4부두 안벽 균열 점검 필요 — 진입 제한' },
  { id: '2', level: 'danger', message: '태풍 예비 주의보 발령 — 24시간 내 접근 예상' },
  { id: '3', level: 'info', message: '컨테이너 2부두 야간 작업 완료 예정 02:00' },
];

const LEVEL_CLASSES: Record<Alert['level'], string> = {
  warning: 'bg-port-warning/10 border-port-warning text-port-warning',
  danger: 'bg-port-danger/10 border-port-danger text-port-danger',
  info: 'bg-port-accent/10 border-port-accent text-port-accent',
};

const LEVEL_ICON: Record<Alert['level'], string> = {
  warning: '⚠',
  danger: '🚨',
  info: 'ℹ',
};

export function AlertBanner() {
  const [dismissed, setDismissed] = useState<Set<string>>(new Set());

  const visible = SAMPLE_ALERTS.filter((a) => !dismissed.has(a.id));

  if (visible.length === 0) return null;

  return (
    <div className="absolute top-12 left-1/2 -translate-x-1/2 z-50 flex flex-col gap-1 w-full max-w-2xl px-4 pointer-events-none">
      {visible.map((alert) => (
        <div
          key={alert.id}
          className={`flex items-center gap-2 px-3 py-2 rounded border text-xs pointer-events-auto backdrop-blur-sm ${LEVEL_CLASSES[alert.level]}`}
        >
          <span className="flex-shrink-0">{LEVEL_ICON[alert.level]}</span>
          <span className="flex-1">{alert.message}</span>
          <button
            type="button"
            className="ml-2 opacity-60 hover:opacity-100 transition-opacity"
            onClick={() => setDismissed((prev) => new Set([...prev, alert.id]))}
          >
            ✕
          </button>
        </div>
      ))}
    </div>
  );
}
