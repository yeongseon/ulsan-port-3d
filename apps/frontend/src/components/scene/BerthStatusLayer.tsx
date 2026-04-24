import { ThreeEvent } from '@react-three/fiber';
import type { Berth } from '@/stores/dataStore';
import { latLonToLocal } from '@/utils/coordinates';
import { useMapStore } from '@/stores/mapStore';

const STATUS_COLORS: Record<Berth['status'], string> = {
  normal: '#22c55e',
  damaged: '#f59e0b',
  unavailable: '#ef4444',
  checking: '#9ca3af',
};

function BerthMarker({ berth }: { berth: Berth }) {
  const selectEntity = useMapStore((s) => s.selectEntity);
  const pos = latLonToLocal(berth.lat, berth.lon, 1);
  const color = STATUS_COLORS[berth.status];

  const handleClick = (e: ThreeEvent<MouseEvent>) => {
    e.stopPropagation();
    selectEntity('berth', berth.berth_id);
  };

  return (
    <group position={[pos.x, pos.y, pos.z]}>
      <mesh onPointerUp={handleClick}>
        <boxGeometry args={[3, 0.5, 2]} />
        <meshStandardMaterial
          color={color}
          emissive={color}
          emissiveIntensity={0.3}
          transparent
          opacity={0.85}
        />
      </mesh>
      <pointLight color={color} intensity={0.8} distance={15} decay={2} />
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
