import { useDataStore } from '@/stores/dataStore';
import { useUiStore } from '@/stores/uiStore';

export function Header() {
  const vessels = useDataStore((s) => s.vessels);
  const toggleLeft = useUiStore((s) => s.toggleLeftPanel);
  const toggleRight = useUiStore((s) => s.toggleRightPanel);
  const leftOpen = useUiStore((s) => s.leftPanelOpen);

  const now = new Date();
  const timeStr = now.toLocaleTimeString('ko-KR', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    timeZone: 'Asia/Seoul',
  });
  const dateStr = now.toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'short',
    timeZone: 'Asia/Seoul',
  });

  return (
    <header className="h-12 bg-port-panel border-b border-port-border flex items-center px-4 gap-4 shrink-0 z-40">
      <button
        type="button"
        onClick={toggleLeft}
        className={`w-7 h-7 flex flex-col justify-center gap-1 rounded transition-colors ${
          leftOpen ? 'text-port-accent' : 'text-port-muted hover:text-white'
        }`}
      >
        <span className="block h-0.5 bg-current" />
        <span className="block h-0.5 bg-current" />
        <span className="block h-0.5 bg-current" />
      </button>

      <div className="flex items-center gap-2">
        <div className="w-2 h-2 rounded-full bg-port-success animate-pulse" />
        <h1 className="text-sm font-bold tracking-wide text-white">울산항 3D 관제 시스템</h1>
        <span className="text-port-muted text-xs">ULSANPORT v1.0</span>
      </div>

      <div className="ml-auto flex items-center gap-6">
        <div className="text-right hidden sm:block">
          <p className="text-xs font-mono text-white">{timeStr}</p>
          <p className="text-xs text-port-muted">{dateStr}</p>
        </div>

        <div className="flex gap-3 text-xs">
          <StatusBadge label="선박" value={vessels.length} color="text-port-accent" />
          <StatusBadge label="경보" value={2} color="text-port-danger" />
        </div>

        <button
          type="button"
          onClick={toggleRight}
          className="px-2 py-1 rounded border border-port-border text-xs text-port-muted hover:border-port-accent hover:text-port-accent transition-colors"
        >
          통계
        </button>
      </div>
    </header>
  );
}

function StatusBadge({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div className="flex items-center gap-1">
      <span className="text-port-muted">{label}</span>
      <span className={`font-bold font-mono ${color}`}>{value}</span>
    </div>
  );
}
