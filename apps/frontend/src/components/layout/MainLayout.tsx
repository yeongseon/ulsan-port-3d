import { useEffect, useMemo, useState } from 'react';
import { apiClient } from '@/api/client';
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

type Scenario = {
  id: string;
  name: string;
  description: string;
};

type ScenarioFrame = {
  id: string;
  label: string;
  timestamp: string;
  summary: string;
};

const LEFT_TABS: { id: LeftTab; label: string }[] = [
  { id: 'filter', label: '필터' },
  { id: 'weather', label: '기상' },
  { id: 'stats', label: '통계' },
  { id: 'ontology', label: '온톨로지' },
];

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null;
}

function getString(value: unknown, fallback = ''): string {
  return typeof value === 'string' ? value : fallback;
}

function normalizeArray(payload: unknown, keys: string[]): unknown[] {
  if (Array.isArray(payload)) return payload;
  if (!isRecord(payload)) return [];

  for (const key of keys) {
    const value = payload[key];
    if (Array.isArray(value)) {
      return value;
    }
  }

  if (isRecord(payload.data)) {
    for (const key of keys) {
      const value = payload.data[key];
      if (Array.isArray(value)) {
        return value;
      }
    }
  }

  return [];
}

function normalizeScenarios(payload: unknown): Scenario[] {
  return normalizeArray(payload, ['scenarios', 'items', 'results', 'data'])
    .map((entry) => {
      if (!isRecord(entry)) return null;

      const id = getString(entry.id ?? entry.scenario_id ?? entry.uid);
      if (!id) return null;

      return {
        id,
        name: getString(entry.name ?? entry.title, id),
        description: getString(entry.description ?? entry.summary),
      };
    })
    .filter((entry): entry is Scenario => entry !== null);
}

function normalizeScenarioFrames(payload: unknown): ScenarioFrame[] {
  return normalizeArray(payload, ['frames', 'items', 'results', 'data'])
    .map((entry, index) => {
      if (!isRecord(entry)) return null;

      const id = getString(entry.id ?? entry.frame_id ?? entry.timestamp, `frame-${index}`);
      const timestamp = getString(entry.timestamp ?? entry.observed_at ?? entry.at);

      return {
        id,
        label: getString(entry.label ?? entry.title, `Frame ${index + 1}`),
        timestamp,
        summary: getString(entry.summary ?? entry.description ?? entry.message),
      };
    })
    .filter((entry): entry is ScenarioFrame => entry !== null);
}

function formatFrameTime(frame: ScenarioFrame | null): string {
  if (!frame) return '--:--';
  if (!frame.timestamp) return frame.label;

  const date = new Date(frame.timestamp);
  if (Number.isNaN(date.getTime())) {
    return frame.timestamp;
  }

  return date.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' });
}

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
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [frames, setFrames] = useState<ScenarioFrame[]>([]);
  const [selectedScenarioId, setSelectedScenarioId] = useState<string | null>(null);
  const [scenariosLoading, setScenariosLoading] = useState(false);
  const [framesLoading, setFramesLoading] = useState(false);

  useEffect(() => {
    let isMounted = true;
    setScenariosLoading(true);

    apiClient.getScenarios()
      .then((payload) => {
        if (!isMounted) return;

        const nextScenarios = normalizeScenarios(payload);
        setScenarios(nextScenarios);
        setSelectedScenarioId((current) => current ?? nextScenarios[0]?.id ?? null);
      })
      .catch((err) => {
        console.error('Failed to load scenarios:', err);
        if (isMounted) {
          setScenarios([]);
          setSelectedScenarioId(null);
        }
      })
      .finally(() => {
        if (isMounted) {
          setScenariosLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, []);

  useEffect(() => {
    if (!selectedScenarioId) {
      setFrames([]);
      setTimelinePosition(0);
      return;
    }

    let isMounted = true;
    setFramesLoading(true);
    setIsPlaying(false);

    apiClient.getScenarioFrames(selectedScenarioId)
      .then((payload) => {
        if (!isMounted) return;

        const nextFrames = normalizeScenarioFrames(payload);
        setFrames(nextFrames);
        setTimelinePosition(0);
      })
      .catch((err) => {
        console.error('Failed to load scenario frames:', err);
        if (isMounted) {
          setFrames([]);
          setTimelinePosition(0);
        }
      })
      .finally(() => {
        if (isMounted) {
          setFramesLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [selectedScenarioId, setIsPlaying, setTimelinePosition]);

  const sliderMax = Math.max(frames.length - 1, 0);
  const clampedTimelinePosition = Math.min(timelinePosition, sliderMax);
  const currentFrame = frames[clampedTimelinePosition] ?? null;

  useEffect(() => {
    if (timelinePosition !== clampedTimelinePosition) {
      setTimelinePosition(clampedTimelinePosition);
    }
  }, [clampedTimelinePosition, setTimelinePosition, timelinePosition]);

  useEffect(() => {
    if (!isPlaying || sliderMax === 0) {
      return undefined;
    }

    const intervalId = window.setInterval(() => {
      if (timelinePosition >= sliderMax) {
        setIsPlaying(false);
        return;
      }

      setTimelinePosition(Math.min(timelinePosition + 1, sliderMax));
    }, 1_000);

    return () => {
      window.clearInterval(intervalId);
    };
  }, [isPlaying, setIsPlaying, setTimelinePosition, sliderMax, timelinePosition]);

  const selectedScenario = useMemo(
    () => scenarios.find((scenario) => scenario.id === selectedScenarioId) ?? null,
    [scenarios, selectedScenarioId],
  );

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
            onClick={() => setIsPlaying(!isPlaying && sliderMax > 0)}
            className="text-xs px-2 py-1 rounded bg-port-accent text-white hover:bg-blue-500 transition-colors disabled:opacity-50"
            disabled={sliderMax === 0}
          >
            {isPlaying ? '⏸ 정지' : '▶ 재생'}
          </button>

          <select
            value={selectedScenarioId ?? ''}
            onChange={(e) => setSelectedScenarioId(e.target.value || null)}
            className="max-w-48 bg-port-bg border border-port-border rounded px-2 py-1 text-xs text-white"
          >
            <option value="">시나리오 선택</option>
            {scenarios.map((scenario) => (
              <option key={scenario.id} value={scenario.id}>
                {scenario.name}
              </option>
            ))}
          </select>

          <input
            type="range"
            min={0}
            max={sliderMax}
            value={clampedTimelinePosition}
            onChange={(e) => {
              setIsPlaying(false);
              setTimelinePosition(Number(e.target.value));
            }}
            className="flex-1 accent-port-accent"
          />

          <span className="text-xs text-port-muted font-mono w-20 text-right">
            {formatFrameTime(currentFrame)}
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
            <div className="rounded border border-port-border bg-port-bg p-3">
              <div className="mb-3 flex items-center justify-between gap-3">
                <div>
                  <p className="text-xs text-port-muted">시나리오 재생</p>
                  <p className="text-sm text-white">{selectedScenario?.name ?? '선택된 시나리오 없음'}</p>
                </div>
                <div className="text-right text-[11px] text-port-muted">
                  <p>{scenariosLoading ? '시나리오 불러오는 중...' : `${scenarios.length} scenarios`}</p>
                  <p>{framesLoading ? '프레임 불러오는 중...' : `${frames.length} frames`}</p>
                </div>
              </div>

              <div className="grid grid-cols-[minmax(0,1fr)_220px] gap-3 max-md:grid-cols-1">
                <div className="space-y-2">
                  <div className="h-20 rounded border border-port-border bg-port-panel/40 px-3 py-2">
                    <p className="text-[11px] text-port-muted">현재 프레임</p>
                    <p className="mt-1 text-sm text-white">{currentFrame?.label ?? '프레임 없음'}</p>
                    <p className="mt-1 text-xs text-port-muted">
                      {currentFrame?.summary || selectedScenario?.description || '선택한 시나리오의 프레임을 재생합니다.'}
                    </p>
                  </div>

                  <div className="flex gap-2 overflow-x-auto pb-1">
                    {frames.map((frame, index) => (
                      <button
                        key={frame.id}
                        type="button"
                        onClick={() => {
                          setIsPlaying(false);
                          setTimelinePosition(index);
                        }}
                        className={`min-w-28 rounded border px-3 py-2 text-left transition-colors ${
                          index === clampedTimelinePosition
                            ? 'border-port-accent bg-port-accent/10 text-white'
                            : 'border-port-border bg-port-panel/30 text-port-muted hover:text-white'
                        }`}
                      >
                        <p className="text-[11px] font-mono">{formatFrameTime(frame)}</p>
                        <p className="mt-1 truncate text-xs">{frame.label}</p>
                      </button>
                    ))}
                    {frames.length === 0 && (
                      <div className="flex h-20 flex-1 items-center justify-center rounded border border-dashed border-port-border text-xs text-port-muted">
                        {selectedScenarioId ? '프레임 데이터 없음' : '시나리오를 선택하세요'}
                      </div>
                    )}
                  </div>
                </div>

                <div className="rounded border border-port-border bg-port-panel/30 p-3 text-xs text-port-muted">
                  <p className="mb-2 text-white">Playback</p>
                  <div className="space-y-1">
                    <p>Scenario ID: {selectedScenarioId ?? '-'}</p>
                    <p>Frame Index: {frames.length === 0 ? '-' : clampedTimelinePosition + 1}</p>
                    <p>Status: {isPlaying ? 'playing' : 'paused'}</p>
                  </div>
                </div>
              </div>
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
