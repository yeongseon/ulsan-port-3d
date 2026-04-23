import { useRef } from 'react';
import { ThreeEvent } from '@react-three/fiber';
import * as THREE from 'three';
import type { Vessel } from '@/stores/dataStore';
import { latLonToLocal } from '@/utils/coordinates';
import { useMapStore } from '@/stores/mapStore';

const TYPE_COLORS: Record<string, string> = {
  cargo: '#3b82f6',
  tanker: '#f59e0b',
  container: '#22c55e',
  passenger: '#a78bfa',
  tug: '#f97316',
  default: '#9ca3af',
};

function VesselMarker({ vessel }: { vessel: Vessel }) {
  const meshRef = useRef<THREE.Mesh>(null);
  const selectEntity = useMapStore((s) => s.selectEntity);

  const pos = latLonToLocal(vessel.lat, vessel.lon, 5);
  const color = TYPE_COLORS[vessel.ship_type] ?? TYPE_COLORS.default;
  const headingRad = ((vessel.heading ?? 0) * Math.PI) / 180;

  const handleClick = (e: ThreeEvent<MouseEvent>) => {
    e.stopPropagation();
    selectEntity('vessel', vessel.vessel_id);
  };

  return (
    <group position={[pos.x, pos.y, pos.z]} rotation={[0, -headingRad, 0]}>
      <mesh ref={meshRef} onPointerUp={handleClick} castShadow>
        <coneGeometry args={[1.2, 3.5, 6]} />
        <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.4} />
      </mesh>
      <pointLight color={color} intensity={0.5} distance={20} />
    </group>
  );
}

interface VesselLayerProps {
  vessels: Vessel[];
}

export function VesselLayer({ vessels }: VesselLayerProps) {
  return (
    <group>
      {vessels.map((v) => (
        <VesselMarker key={v.vessel_id} vessel={v} />
      ))}
    </group>
  );
}
