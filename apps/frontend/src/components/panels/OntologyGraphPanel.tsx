import { useEffect, useRef } from 'react';

interface GraphNode {
  id: string;
  label: string;
  type: 'vessel' | 'berth' | 'operator' | 'zone';
  x?: number;
  y?: number;
  vx?: number;
  vy?: number;
}

interface GraphEdge {
  source: string;
  target: string;
  label: string;
}

const SAMPLE_NODES: GraphNode[] = [
  { id: 'v1', label: '대한상선', type: 'vessel' },
  { id: 'v2', label: '현대타이거', type: 'vessel' },
  { id: 'v3', label: '포스코케미칼', type: 'vessel' },
  { id: 'b1', label: '1부두', type: 'berth' },
  { id: 'b2', label: '오일터미널A', type: 'berth' },
  { id: 'o1', label: '현대상선', type: 'operator' },
  { id: 'z1', label: '북항구역', type: 'zone' },
];

const SAMPLE_EDGES: GraphEdge[] = [
  { source: 'v1', target: 'b1', label: '정박' },
  { source: 'v2', target: 'b2', label: '정박' },
  { source: 'v3', target: 'z1', label: '진입' },
  { source: 'o1', target: 'v1', label: '운영' },
  { source: 'o1', target: 'v2', label: '운영' },
  { source: 'b1', target: 'z1', label: '속함' },
];

const NODE_COLORS: Record<string, string> = {
  vessel: '#3b82f6',
  berth: '#22c55e',
  operator: '#f59e0b',
  zone: '#a78bfa',
};

const W = 360;
const H = 280;

function initPositions(nodes: GraphNode[]) {
  nodes.forEach((n, i) => {
    const angle = (i / nodes.length) * Math.PI * 2;
    n.x = W / 2 + Math.cos(angle) * 90;
    n.y = H / 2 + Math.sin(angle) * 90;
    n.vx = 0;
    n.vy = 0;
  });
}

function tick(nodes: GraphNode[], edges: GraphEdge[]) {
  const k = 0.05;
  const repulsion = 800;
  const linkDist = 80;

  for (let i = 0; i < nodes.length; i++) {
    for (let j = i + 1; j < nodes.length; j++) {
      const a = nodes[i];
      const b = nodes[j];
      const dx = (b.x ?? 0) - (a.x ?? 0);
      const dy = (b.y ?? 0) - (a.y ?? 0);
      const dist = Math.sqrt(dx * dx + dy * dy) || 1;
      const force = repulsion / (dist * dist);
      a.vx = (a.vx ?? 0) - (dx / dist) * force;
      a.vy = (a.vy ?? 0) - (dy / dist) * force;
      b.vx = (b.vx ?? 0) + (dx / dist) * force;
      b.vy = (b.vy ?? 0) + (dy / dist) * force;
    }
  }

  const nodeMap = Object.fromEntries(nodes.map((n) => [n.id, n]));
  for (const edge of edges) {
    const a = nodeMap[edge.source];
    const b = nodeMap[edge.target];
    if (!a || !b) continue;
    const dx = (b.x ?? 0) - (a.x ?? 0);
    const dy = (b.y ?? 0) - (a.y ?? 0);
    const dist = Math.sqrt(dx * dx + dy * dy) || 1;
    const force = (dist - linkDist) * k;
    a.vx = (a.vx ?? 0) + (dx / dist) * force;
    a.vy = (a.vy ?? 0) + (dy / dist) * force;
    b.vx = (b.vx ?? 0) - (dx / dist) * force;
    b.vy = (b.vy ?? 0) - (dy / dist) * force;
  }

  for (const n of nodes) {
    n.vx = (n.vx ?? 0) * 0.85;
    n.vy = (n.vy ?? 0) * 0.85;
    n.x = Math.max(20, Math.min(W - 20, (n.x ?? 0) + (n.vx ?? 0)));
    n.y = Math.max(20, Math.min(H - 20, (n.y ?? 0) + (n.vy ?? 0)));
  }
}

export function OntologyGraphPanel() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const nodesRef = useRef<GraphNode[]>(JSON.parse(JSON.stringify(SAMPLE_NODES)));

  useEffect(() => {
    const nodes = nodesRef.current;
    initPositions(nodes);

    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animId: number;

    const draw = () => {
      tick(nodes, SAMPLE_EDGES);

      ctx.clearRect(0, 0, W, H);
      ctx.fillStyle = '#0a0e1a';
      ctx.fillRect(0, 0, W, H);

      const nodeMap = Object.fromEntries(nodes.map((n) => [n.id, n]));

      for (const edge of SAMPLE_EDGES) {
        const a = nodeMap[edge.source];
        const b = nodeMap[edge.target];
        if (!a || !b) continue;
        ctx.beginPath();
        ctx.moveTo(a.x ?? 0, a.y ?? 0);
        ctx.lineTo(b.x ?? 0, b.y ?? 0);
        ctx.strokeStyle = '#1f2937';
        ctx.lineWidth = 1;
        ctx.stroke();

        const mx = ((a.x ?? 0) + (b.x ?? 0)) / 2;
        const my = ((a.y ?? 0) + (b.y ?? 0)) / 2;
        ctx.fillStyle = '#6b7280';
        ctx.font = '8px monospace';
        ctx.textAlign = 'center';
        ctx.fillText(edge.label, mx, my - 2);
      }

      for (const node of nodes) {
        const color = NODE_COLORS[node.type] ?? '#9ca3af';
        ctx.beginPath();
        ctx.arc(node.x ?? 0, node.y ?? 0, 8, 0, Math.PI * 2);
        ctx.fillStyle = color + '33';
        ctx.fill();
        ctx.strokeStyle = color;
        ctx.lineWidth = 1.5;
        ctx.stroke();

        ctx.fillStyle = '#ffffff';
        ctx.font = '9px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(node.label, node.x ?? 0, (node.y ?? 0) + 18);
      }

      animId = requestAnimationFrame(draw);
    };

    animId = requestAnimationFrame(draw);
    return () => cancelAnimationFrame(animId);
  }, []);

  return (
    <div className="p-3">
      <p className="text-xs text-port-muted mb-2">온톨로지 관계 그래프</p>
      <canvas
        ref={canvasRef}
        width={W}
        height={H}
        className="rounded border border-port-border w-full"
        style={{ imageRendering: 'crisp-edges' }}
      />
      <div className="flex flex-wrap gap-2 mt-2">
        {Object.entries(NODE_COLORS).map(([type, color]) => (
          <div key={type} className="flex items-center gap-1 text-xs text-port-muted">
            <div className="w-2 h-2 rounded-full" style={{ backgroundColor: color }} />
            {type === 'vessel' ? '선박' : type === 'berth' ? '부두' : type === 'operator' ? '운영사' : '구역'}
          </div>
        ))}
      </div>
    </div>
  );
}
