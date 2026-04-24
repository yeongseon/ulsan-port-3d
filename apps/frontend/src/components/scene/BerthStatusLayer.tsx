import { ThreeEvent } from '@react-three/fiber';
import type { Berth } from '@/stores/dataStore';
import { latLonToLocal } from '@/utils/coordinates';
import { useMapStore } from '@/stores/mapStore';
import { PORT_LAYOUT_BY_FACILITY } from './portLayout';

const STATUS_COLORS: Record<Berth['status'], string> = {
  normal: '#22c55e',
  damaged: '#f59e0b',
  unavailable: '#ef4444',
  checking: '#9ca3af',
};

function BerthMarker({ berth }: { berth: Berth }) {
  const selectEntity = useMapStore((s) => s.selectEntity);
  const pos = latLonToLocal(berth.lat, berth.lon, 0);
  const color = STATUS_COLORS[berth.status];
  const layout = PORT_LAYOUT_BY_FACILITY[berth.facility_code];

  const handleClick = (e: ThreeEvent<MouseEvent>) => {
    e.stopPropagation();
    selectEntity('berth', berth.berth_id);
  };

  return (
    <group
      position={[pos.x, 0, pos.z]}
      rotation={[0, layout?.rotation ?? 0, 0]}
    >
      <mesh position={[0, 0.5, 0]} onPointerUp={handleClick}>
        <boxGeometry args={[layout?.length ?? 3, 0.24, layout?.width ?? 0.8]} />
        <meshStandardMaterial
          color={color}
          emissive={color}
          emissiveIntensity={0.45}
          transparent
          opacity={0.85}
        />
      </mesh>
    </group>
  );
}

interface BerthStatusLayerProps {
  berths: Berth[];
}

export function BerthStatusLayer({ berths }: BerthStatusLayerProps) {
  return (
    <group>
      {berths.map((b) => (
        <BerthMarker key={b.berth_id} berth={b} />
      ))}
    </group>
  );
}
