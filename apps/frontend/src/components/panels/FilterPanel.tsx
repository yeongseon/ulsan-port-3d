import { useMapStore } from '@/stores/mapStore';
import { useUiStore } from '@/stores/uiStore';

interface LayerConfig {
  id: string;
  label: string;
  color: string;
}

const LAYERS: LayerConfig[] = [
  { id: 'vessels', label: '선박 레이어', color: '#3b82f6' },
  { id: 'berths', label: '부두 레이어', color: '#22c55e' },
  { id: 'routes', label: '항로 레이어', color: '#f59e0b' },
  { id: 'weather', label: '기상 레이어', color: '#a78bfa' },
];

const VESSEL_TYPES = ['전체', '화물선', '탱커', '컨테이너선', '여객선', '예인선'];
const ZONES = ['전체 구역', '북항', '남항', '오일터미널', '컨테이너부두', '여객터미널'];

export function FilterPanel() {
  const activeLayerIds = useMapStore((s) => s.activeLayerIds);
  const toggleLayer = useMapStore((s) => s.toggleLayer);
  const activeTab = useUiStore((s) => s.activeTab);
  const setActiveTab = useUiStore((s) => s.setActiveTab);

  return (
    <div className="p-3 space-y-4">
      <div>
        <p className="text-xs text-port-muted uppercase tracking-wider mb-2">레이어 제어</p>
        <div className="space-y-1">
          {LAYERS.map((layer) => {
            const active = activeLayerIds.includes(layer.id);
            return (
              <button
                key={layer.id}
                type="button"
                onClick={() => toggleLayer(layer.id)}
                className={`w-full flex items-center gap-2 px-2 py-1.5 rounded text-xs transition-colors ${
                  active
                    ? 'bg-port-border text-white'
                    : 'text-port-muted hover:bg-port-border hover:text-white'
                }`}
              >
                <div
                  className="w-2 h-2 rounded-full flex-shrink-0"
                  style={{ backgroundColor: active ? layer.color : '#374151' }}
                />
                {layer.label}
                <span className="ml-auto text-port-muted">{active ? 'ON' : 'OFF'}</span>
              </button>
            );
          })}
        </div>
      </div>

      <div>
        <p className="text-xs text-port-muted uppercase tracking-wider mb-2">선박 유형 필터</p>
        <div className="flex flex-wrap gap-1">
          {VESSEL_TYPES.map((type) => (
            <button
              key={type}
              type="button"
              className="px-2 py-0.5 rounded text-xs border border-port-border text-port-muted hover:border-port-accent hover:text-port-accent transition-colors"
            >
              {type}
            </button>
          ))}
        </div>
      </div>

      <div>
        <p className="text-xs text-port-muted uppercase tracking-wider mb-2">구역 필터</p>
        <select
          className="w-full bg-port-bg border border-port-border rounded px-2 py-1 text-xs text-white focus:border-port-accent focus:outline-none"
          defaultValue="전체 구역"
        >
          {ZONES.map((z) => (
            <option key={z} value={z}>{z}</option>
          ))}
        </select>
      </div>

      <div>
        <p className="text-xs text-port-muted uppercase tracking-wider mb-2">뷰 모드</p>
        <div className="flex gap-1">
          {(['overview', 'traffic', 'berth'] as const).map((tab) => {
            const labels: Record<string, string> = {
              overview: '개요',
              traffic: '교통',
              berth: '부두',
            };
            return (
              <button
                key={tab}
                type="button"
                onClick={() => setActiveTab(tab)}
                className={`flex-1 py-1 rounded text-xs transition-colors ${
                  activeTab === tab
                    ? 'bg-port-accent text-white'
                    : 'bg-port-bg text-port-muted hover:text-white'
                }`}
              >
                {labels[tab]}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
