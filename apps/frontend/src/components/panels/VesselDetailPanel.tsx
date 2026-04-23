import { useDataStore } from '@/stores/dataStore';
import { useMapStore } from '@/stores/mapStore';
import { format } from 'date-fns';
import { ko } from 'date-fns/locale';

const TYPE_LABELS: Record<string, string> = {
  cargo: '화물선',
  tanker: '탱커',
  container: '컨테이너선',
  passenger: '여객선',
  tug: '예인선',
};

export function VesselDetailPanel() {
  const selectedId = useMapStore((s) => s.selectedEntityId);
  const selectedType = useMapStore((s) => s.selectedEntityType);
  const selectEntity = useMapStore((s) => s.selectEntity);
  const vessels = useDataStore((s) => s.vessels);

  if (selectedType !== 'vessel' || !selectedId) return null;

  const vessel = vessels.find((v) => v.vessel_id === selectedId);
  if (!vessel) return null;

  return (
    <div className="absolute right-0 top-0 h-full w-72 bg-port-panel border-l border-port-border flex flex-col shadow-2xl z-30 animate-in slide-in-from-right duration-200">
      <div className="flex items-center justify-between px-4 py-3 border-b border-port-border">
        <div>
          <h3 className="font-bold text-white text-sm">{vessel.name}</h3>
          <p className="text-xs text-port-muted">{vessel.call_sign}</p>
        </div>
        <button
          type="button"
          className="text-port-muted hover:text-white transition-colors text-lg leading-none"
          onClick={() => selectEntity(null, null)}
        >
          ✕
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        <div className="bg-port-bg rounded-lg p-3 space-y-2">
          <p className="text-xs text-port-muted uppercase tracking-wider mb-1">선박 정보</p>
          <InfoRow label="선종" value={TYPE_LABELS[vessel.ship_type] ?? vessel.ship_type} />
          <InfoRow label="호출 부호" value={vessel.call_sign} />
        </div>

        <div className="bg-port-bg rounded-lg p-3 space-y-2">
          <p className="text-xs text-port-muted uppercase tracking-wider mb-1">위치 및 항법</p>
          <InfoRow label="위도" value={vessel.lat.toFixed(4) + '°N'} />
          <InfoRow label="경도" value={vessel.lon.toFixed(4) + '°E'} />
          <InfoRow label="속도" value={vessel.speed.toFixed(1) + ' kn'} />
          <InfoRow label="침로" value={vessel.course.toFixed(0) + '°'} />
          <InfoRow label="선수방향" value={vessel.heading.toFixed(0) + '°'} />
        </div>

        {vessel.updated_at && (
          <p className="text-xs text-port-muted">
            최종 갱신: {format(new Date(vessel.updated_at), 'MM/dd HH:mm:ss', { locale: ko })}
          </p>
        )}
      </div>
    </div>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between">
      <span className="text-xs text-port-muted">{label}</span>
      <span className="text-xs font-mono text-white">{value}</span>
    </div>
  );
}
