import { useEffect, useMemo, useRef, useState } from 'react';
import { apiClient } from '@/api/client';
import { useDataStore } from '@/stores/dataStore';
import { useMapStore } from '@/stores/mapStore';

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

type GraphPayload = {
  nodes: GraphNode[];
  edges: GraphEdge[];
};

type GraphNodeType = GraphNode['type'];

const NODE_COLORS: Record<GraphNodeType, string> = {
  vessel: '#3b82f6',
  berth: '#22c55e',
  operator: '#f59e0b',
  zone: '#a78bfa',
};

const W = 360;
const H = 280;

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null;
}

function getString(value: unknown, fallback = ''): string {
  return typeof value === 'string' ? value : fallback;
}

function getNodesContainer(value: unknown): unknown[] {
  if (Array.isArray(value)) return value;
  if (!isRecord(value)) return [];

  const nested = value.nodes ?? value.vertices ?? value.entities ?? value.items ?? value.data;
  return Array.isArray(nested) ? nested : [];
}

function getEdgesContainer(value: unknown): unknown[] {
  if (Array.isArray(value)) return value;
  if (!isRecord(value)) return [];

  const nested = value.edges ?? value.links ?? value.relations ?? value.relationships;
  return Array.isArray(nested) ? nested : [];
}

function toGraphNodeType(value: unknown): GraphNodeType {
  const v = typeof value === 'string' ? value.toLowerCase() : '';
  if (v === 'berth') return 'berth';
  if (v === 'operator') return 'operator';
  if (v === 'zone' || v === 'portzone') return 'zone';
  return 'vessel';
}

function normalizeGraphNode(entry: unknown): GraphNode | null {
  if (!isRecord(entry)) return null;

  const id = getString(entry.id ?? entry.node_id ?? entry.entity_id ?? entry.uid);
  if (!id) return null;

  return {
    id,
    label: getString(entry.label ?? entry.name ?? entry.title, id),
    type: toGraphNodeType(entry.type ?? entry.node_type ?? entry.kind),
  };
}

function normalizeGraphEdge(entry: unknown): GraphEdge | null {
  if (!isRecord(entry)) return null;

  const source = getString(entry.source ?? entry.from ?? entry.source_id ?? entry.subject);
  const target = getString(entry.target ?? entry.to ?? entry.target_id ?? entry.object);
  if (!source || !target) return null;

  return {
    source,
    target,
    label: getString(entry.label ?? entry.predicate ?? entry.relationship, ''),
  };
}

function normalizeEntityGraphResponse(payload: Record<string, unknown>): GraphPayload {
  const center = normalizeGraphNode(payload.center);
  if (!center) return { nodes: [], edges: [] };

  const relations = Array.isArray(payload.relations) ? payload.relations : [];
  const nodes: GraphNode[] = [center];
  const edges: GraphEdge[] = [];

  for (const rel of relations) {
    if (!isRecord(rel)) continue;
    const relNode = normalizeGraphNode(rel.node);
    if (!relNode) continue;
    nodes.push(relNode);
    edges.push({
      source: center.id,
      target: relNode.id,
      label: getString(rel.predicate, ''),
    });
  }

  return { nodes, edges };
}

function normalizeGraphPayload(payload: unknown): GraphPayload {
  const source = isRecord(payload) && isRecord(payload.data) ? payload.data : payload;

  // Handle EntityGraphResponse shape (center + relations)
  if (isRecord(source) && 'center' in source && 'relations' in source) {
    return normalizeEntityGraphResponse(source);
  }

  return {
    nodes: getNodesContainer(source).map(normalizeGraphNode).filter((node): node is GraphNode => node !== null),
    edges: getEdgesContainer(source).map(normalizeGraphEdge).filter((edge): edge is GraphEdge => edge !== null),
  };
}

function initPositions(nodes: GraphNode[]) {
  nodes.forEach((n, i) => {
    const angle = (i / Math.max(nodes.length, 1)) * Math.PI * 2;
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

  for (let i = 0; i < nodes.length; i += 1) {
    for (let j = i + 1; j < nodes.length; j += 1) {
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
  const nodesRef = useRef<GraphNode[]>([]);
  const [edges, setEdges] = useState<GraphEdge[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const selectedEntityId = useMapStore((s) => s.selectedEntityId);
  const selectedEntityType = useMapStore((s) => s.selectedEntityType);
  const vessels = useDataStore((s) => s.vessels);
  const berths = useDataStore((s) => s.berths);

  const graphTarget = useMemo(() => {
    if (selectedEntityType && selectedEntityId) {
      return { type: selectedEntityType, id: selectedEntityId };
    }

    if (vessels[0]) {
      return { type: 'vessel', id: vessels[0].vessel_id };
    }

    if (berths[0]) {
      return { type: 'berth', id: berths[0].berth_id };
    }

    return null;
  }, [berths, selectedEntityId, selectedEntityType, vessels]);

  useEffect(() => {
    if (!graphTarget) {
      nodesRef.current = [];
      setEdges([]);
      return;
    }

    let isMounted = true;
    setIsLoading(true);

    const TYPE_MAP: Record<string, string> = { vessel: 'Vessel', berth: 'Berth', operator: 'Operator', zone: 'Zone' };
    const backendType = TYPE_MAP[graphTarget.type] ?? graphTarget.type;
    apiClient.getGraph(backendType, graphTarget.id)
      .then((payload) => {
        if (!isMounted) return;

        const graph = normalizeGraphPayload(payload);
        initPositions(graph.nodes);
        nodesRef.current = graph.nodes;
        setEdges(graph.edges);
      })
      .catch((err) => {
        if (!isMounted) return;
        nodesRef.current = [];
        setEdges([]);
        console.error('Failed to load ontology graph:', err);
      })
      .finally(() => {
        if (isMounted) {
          setIsLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [graphTarget]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return undefined;

    const ctx = canvas.getContext('2d');
    if (!ctx) return undefined;

    let animId = 0;

    const draw = () => {
      const nodes = nodesRef.current;
      tick(nodes, edges);

      ctx.clearRect(0, 0, W, H);
      ctx.fillStyle = '#0a0e1a';
      ctx.fillRect(0, 0, W, H);

      if (nodes.length === 0) {
        ctx.fillStyle = '#6b7280';
        ctx.font = '11px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(isLoading ? '관계 그래프 불러오는 중...' : '선택된 엔티티 그래프가 없습니다', W / 2, H / 2);
        animId = requestAnimationFrame(draw);
        return;
      }

      const nodeMap = Object.fromEntries(nodes.map((n) => [n.id, n]));

      for (const edge of edges) {
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
        ctx.fillStyle = `${color}33`;
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
  }, [edges, isLoading]);

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
      <div className="mt-2 flex items-center justify-between gap-2 text-[11px] text-port-muted">
        <span>
          {graphTarget ? `${graphTarget.type}:${graphTarget.id}` : '엔티티 선택 대기 중'}
        </span>
        <span>{nodesRef.current.length} nodes</span>
      </div>
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
