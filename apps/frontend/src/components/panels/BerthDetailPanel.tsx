import { useDataStore } from '@/stores/dataStore';
import { useMapStore } from '@/stores/mapStore';

const STATUS_LABELS: Record<string, string> = {
  normal: '정상',
  damaged: '손상',
  unavailable: '사용 불가',
  checking: '점검 중',
};

const STATUS_COLORS: Record<string, string> = {
  normal: 'text-port-success',
  damaged: 'text-port-warning',
  unavailable: 'text-port-danger',
  checking: 'text-port-muted',
};

export function BerthDetailPanel() {
  const selectedId = useMapStore((s) => s.selectedEntityId);
  const selectedType = useMapStore((s) => s.selectedEntityType);
  const selectEntity = useMapStore((s) => s.selectEntity);
  const berths = useDataStore((s) => s.berths);

  if (selectedType !== 'berth' || !selectedId) return null;

  const berth = berths.find((b) => b.berth_id === selectedId);
  if (!berth) return null;

  return (
    <div className="absolute right-0 top-0 h-full w-72 bg-port-panel border-l border-port-border flex flex-col shadow-2xl z-30 animate-in slide-in-from-right duration-200">
      <div className="flex items-center justify-between px-4 py-3 border-b border-port-border">
        <div>
          <h3 className="font-bold text-gray-900 text-sm">{berth.name}</h3>
          <p className="text-xs text-port-muted">{berth.facility_code}</p>
        </div>
        <button
          type="button"
          className="text-port-muted hover:text-gray-900 transition-colors text-lg leading-none"
          onClick={() => selectEntity(null, null)}
        >
          ✕
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        <div className="flex items-center gap-2 p-2 bg-port-bg rounded">
          <div
            className={`text-sm font-bold ${STATUS_COLORS[berth.status] ?? 'text-gray-900'}`}
          >
            ●
          </div>
          <span className="text-sm text-gray-900">{STATUS_LABELS[berth.status] ?? berth.status}</span>
        </div>

        <div className="bg-port-bg rounded-lg p-3 space-y-2">
          <p className="text-xs text-port-muted uppercase tracking-wider mb-1">부두 정보</p>
          <InfoRow label="구역" value={berth.zone} />
          <InfoRow label="운영사" value={berth.operator} />
          <InfoRow label="안벽 길이" value={berth.length + ' m'} />
          <InfoRow label="수심" value={berth.depth + ' m'} />
        </div>

        <div className="bg-port-bg rounded-lg p-3 space-y-2">
          <p className="text-xs text-port-muted uppercase tracking-wider mb-1">위치</p>
          <InfoRow label="위도" value={berth.lat.toFixed(4) + '°N'} />
          <InfoRow label="경도" value={berth.lon.toFixed(4) + '°E'} />
        </div>
      </div>
    </div>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between">
      <span className="text-xs text-port-muted">{label}</span>
      <span className="text-xs font-mono text-gray-900">{value}</span>
    </div>
  );
}
