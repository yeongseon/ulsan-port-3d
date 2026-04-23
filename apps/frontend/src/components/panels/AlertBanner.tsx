import { useEffect, useState } from 'react';
import { apiClient } from '@/api/client';

interface Alert {
  id: string;
  level: 'warning' | 'danger' | 'info';
  message: string;
}

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

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null;
}

function getString(value: unknown, fallback = ''): string {
  return typeof value === 'string' ? value : fallback;
}

function toAlertLevel(value: unknown): Alert['level'] {
  if (value === 'warning') return 'warning';
  if (value === 'danger' || value === 'critical') return 'danger';
  return 'info';
}

function normalizeAlerts(payload: unknown): Alert[] {
  const source = isRecord(payload) ? payload.data ?? payload.items ?? payload.results ?? payload.alerts ?? payload : payload;
  if (!Array.isArray(source)) return [];

  return source
    .map((entry) => {
      if (!isRecord(entry)) return null;

      const id = getString(entry.id ?? entry.alert_id ?? entry.code);
      const message = getString(entry.message ?? entry.title ?? entry.description);
      if (!id || !message) return null;

      return {
        id,
        level: toAlertLevel(entry.level ?? entry.severity),
        message,
      };
    })
    .filter((entry): entry is Alert => entry !== null);
}

export function AlertBanner() {
  const [dismissed, setDismissed] = useState<Set<string>>(new Set());
  const [alerts, setAlerts] = useState<Alert[]>([]);

  useEffect(() => {
    let isMounted = true;

    const loadAlerts = () => {
      apiClient.getAlerts()
        .then((payload) => {
          if (isMounted) {
            setAlerts(normalizeAlerts(payload));
          }
        })
        .catch((err) => {
          console.error('Failed to load alerts:', err);
          if (isMounted) {
            setAlerts([]);
          }
        });
    };

    loadAlerts();
    const intervalId = window.setInterval(loadAlerts, 30_000);

    return () => {
      isMounted = false;
      window.clearInterval(intervalId);
    };
  }, []);

  const visible = alerts.filter((a) => !dismissed.has(a.id));

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
