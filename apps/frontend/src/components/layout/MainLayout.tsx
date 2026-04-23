import { useState } from 'react';
import { PortScene } from '@/components/scene/PortScene';
import { AlertBanner } from '@/components/panels/AlertBanner';
import { FilterPanel } from '@/components/panels/FilterPanel';
import { WeatherPanel } from '@/components/panels/WeatherPanel';
import { StatsPanel } from '@/components/panels/StatsPanel';
import { OntologyGraphPanel } from '@/components/panels/OntologyGraphPanel';
import { VesselDetailPanel } from '@/components/panels/VesselDetailPanel';
import { BerthDetailPanel } from '@/components/panels/BerthDetailPanel';
import { useUiStore } from '@/stores/uiStore';
import { useMapStore } from '@/stores/mapStore';

type LeftTab = 'filter' | 'weather' | 'stats' | 'ontology';

const LEFT_TABS: { id: LeftTab; label: string }[] = [
  { id: 'filter', label: '필터' },
  { id: 'weather', label: '기상' },
  { id: 'stats', label: '통계' },
  { id: 'ontology', label: '온톨로지' },
];

export function MainLayout() {
  const leftPanelOpen = useUiStore((s) => s.leftPanelOpen);
  const bottomPanelOpen = useUiStore((s) => s.bottomPanelOpen);
  const toggleBottomPanel = useUiStore((s) => s.toggleBottomPanel);
  const isPlaying = useUiStore((s) => s.isPlaying);
  const setIsPlaying = useUiStore((s) => s.setIsPlaying);
  const timelinePosition = useUiStore((s) => s.timelinePosition);
  const setTimelinePosition = useUiStore((s) => s.setTimelinePosition);

  const selectedEntityType = useMapStore((s) => s.selectedEntityType);
  const [leftTab, setLeftTab] = useState<LeftTab>('filter');

  return (
    <div className="flex-1 flex overflow-hidden relative">
      {leftPanelOpen && (
        <aside className="w-64 bg-port-panel border-r border-port-border flex flex-col shrink-0 z-20 overflow-hidden">
          <div className="flex border-b border-port-border">
            {LEFT_TABS.map((tab) => (
              <button
                key={tab.id}
                type="button"
                onClick={() => setLeftTab(tab.id)}
                className={`flex-1 py-2 text-xs transition-colors ${
                  leftTab === tab.id
                    ? 'text-port-accent border-b-2 border-port-accent'
                    : 'text-port-muted hover:text-white'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          <div className="flex-1 overflow-y-auto">
            {leftTab === 'filter' && <FilterPanel />}
            {leftTab === 'weather' && <WeatherPanel />}
            {leftTab === 'stats' && <StatsPanel />}
            {leftTab === 'ontology' && <OntologyGraphPanel />}
          </div>
        </aside>
      )}

      <main className="flex-1 relative overflow-hidden">
        <PortScene />

        <AlertBanner />

        <div className="absolute bottom-14 right-3 z-20 flex flex-col gap-1">
          <CameraButton label="↑" title="위로" />
          <div className="flex gap-1">
            <CameraButton label="←" title="좌로" />
            <CameraButton label="⌂" title="기본 뷰" />
            <CameraButton label="→" title="우로" />
          </div>
          <CameraButton label="↓" title="아래로" />
        </div>

        <div className="absolute top-3 right-3 z-20 space-y-1 text-xs text-port-muted">
          <div className="bg-port-panel/80 backdrop-blur px-2 py-1 rounded border border-port-border">
            울산항 35.5°N 129.38°E
          </div>
        </div>

        {selectedEntityType === 'vessel' && <VesselDetailPanel />}
        {selectedEntityType === 'berth' && <BerthDetailPanel />}
      </main>

      <div className="absolute bottom-0 left-0 right-0 z-30 bg-port-panel border-t border-port-border">
        <div className="flex items-center gap-3 px-4 py-2">
          <button
            type="button"
            onClick={() => setIsPlaying(!isPlaying)}
            className="text-xs px-2 py-1 rounded bg-port-accent text-white hover:bg-blue-500 transition-colors"
          >
            {isPlaying ? '⏸ 정지' : '▶ 재생'}
          </button>

          <input
            type="range"
            min={0}
            max={100}
            value={timelinePosition}
            onChange={(e) => setTimelinePosition(Number(e.target.value))}
            className="flex-1 accent-port-accent"
          />

          <span className="text-xs text-port-muted font-mono w-16 text-right">
            -{Math.round((100 - timelinePosition) * 0.24).toString().padStart(2, '0')}:00
          </span>

          <button
            type="button"
            onClick={toggleBottomPanel}
            className="text-xs text-port-muted hover:text-white transition-colors"
          >
            {bottomPanelOpen ? '▼ 타임라인 접기' : '▲ 타임라인 펼치기'}
          </button>
        </div>

        {bottomPanelOpen && (
          <div className="px-4 pb-3">
            <div className="h-20 bg-port-bg rounded border border-port-border flex items-center justify-center">
              <p className="text-port-muted text-xs">과거 이동 궤적 타임라인 — 데이터 로딩 중</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function CameraButton({ label, title }: { label: string; title: string }) {
  return (
    <button
      type="button"
      title={title}
      className="w-7 h-7 bg-port-panel/80 backdrop-blur border border-port-border rounded text-xs text-port-muted hover:text-white hover:border-port-accent transition-colors flex items-center justify-center"
    >
      {label}
    </button>
  );
}
