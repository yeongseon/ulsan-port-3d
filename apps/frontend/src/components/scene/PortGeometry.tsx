import * as THREE from 'three';
import { latLonToLocal } from '@/utils/coordinates';
import { PORT_WHARVES, type PortWharfLayout } from './portLayout';

const ZONE_COLORS: Record<PortWharfLayout['zone'], { deck: string; edge: string }> = {
  general: { deck: '#90a4ae', edge: '#546e7a' },
  container: { deck: '#81c784', edge: '#388e3c' },
  oil: { deck: '#ffb74d', edge: '#e65100' },
  passenger: { deck: '#b39ddb', edge: '#5e35b1' },
  bulk: { deck: '#a1887f', edge: '#4e342e' },
};

const CRANE_POST_GEO = new THREE.BoxGeometry(0.15, 3.0, 0.15);
const CRANE_BEAM_GEO = new THREE.BoxGeometry(0.12, 0.12, 2.5);
const CRANE_HOIST_GEO = new THREE.BoxGeometry(0.06, 0.3, 0.06);
const CRANE_MAT = new THREE.MeshStandardMaterial({ color: '#f57f17', roughness: 0.6, metalness: 0.4 });
const CRANE_HOIST_MAT = new THREE.MeshStandardMaterial({ color: '#424242', roughness: 0.5, metalness: 0.6 });

const OIL_TANK_GEO = new THREE.CylinderGeometry(0.4, 0.4, 0.8, 16);
const OIL_TANK_CAP_GEO = new THREE.CylinderGeometry(0.38, 0.38, 0.04, 16);
const OIL_TANK_MAT = new THREE.MeshStandardMaterial({ color: '#e0e0e0', roughness: 0.3, metalness: 0.6 });
const OIL_TANK_CAP_MAT = new THREE.MeshStandardMaterial({ color: '#bdbdbd', roughness: 0.4, metalness: 0.5 });

const CRANE_COUNTS: Record<PortWharfLayout['zone'], number> = {
  general: 2,
  container: 4,
  bulk: 3,
  oil: 0,
  passenger: 0,
};

function PortCrane({ position }: { position: [number, number, number] }) {
  return (
    <group position={position}>
      <mesh geometry={CRANE_POST_GEO} material={CRANE_MAT} castShadow dispose={null} />
      <mesh position={[0, 1.5, 0]} geometry={CRANE_BEAM_GEO} material={CRANE_MAT} castShadow dispose={null} />
      <mesh position={[0, 1.35, -0.8]} geometry={CRANE_HOIST_GEO} material={CRANE_HOIST_MAT} dispose={null} />
    </group>
  );
}

function OilTank({ position }: { position: [number, number, number] }) {
  return (
    <group position={position}>
      <mesh geometry={OIL_TANK_GEO} material={OIL_TANK_MAT} castShadow dispose={null} />
      <mesh position={[0, 0.42, 0]} geometry={OIL_TANK_CAP_GEO} material={OIL_TANK_CAP_MAT} dispose={null} />
    </group>
  );
}

function WharfStructure({ wharf }: { wharf: PortWharfLayout }) {
  const pos = latLonToLocal(wharf.lat, wharf.lon, 0);
  const colors = ZONE_COLORS[wharf.zone];
  const craneCount = CRANE_COUNTS[wharf.zone];

  const cranes: Array<{ key: string; offset: number }> = [];
  if (craneCount > 0) {
    const spacing = wharf.length / (craneCount + 1);
    for (let i = 0; i < craneCount; i++) {
      cranes.push({ key: `${wharf.facilityCode}-crane-${i}`, offset: -wharf.length / 2 + spacing * (i + 1) });
    }
  }

  return (
    <group position={[pos.x, 0, pos.z]} rotation={[0, wharf.rotation, 0]}>
      <mesh position={[0, 0.2, 0]} castShadow receiveShadow>
        <boxGeometry args={[wharf.length, 0.4, wharf.width]} />
        <meshStandardMaterial color={colors.deck} roughness={0.85} metalness={0.15} />
      </mesh>

      <mesh position={[0, 0.42, -wharf.width / 2 + 0.03]}>
        <boxGeometry args={[wharf.length, 0.08, 0.06]} />
        <meshStandardMaterial color={colors.edge} roughness={0.7} metalness={0.3} />
      </mesh>
      <mesh position={[0, 0.42, wharf.width / 2 - 0.03]}>
        <boxGeometry args={[wharf.length, 0.08, 0.06]} />
        <meshStandardMaterial color={colors.edge} roughness={0.7} metalness={0.3} />
      </mesh>

      {wharf.zone !== 'oil' && wharf.zone !== 'passenger' && (
        <mesh position={[0, 0.55, wharf.width * 0.25]} castShadow>
          <boxGeometry args={[wharf.length * 0.6, 0.3, wharf.width * 0.3]} />
          <meshStandardMaterial color="#eceff1" roughness={0.8} metalness={0.1} />
        </mesh>
      )}

      {wharf.zone === 'passenger' && (
        <mesh position={[0, 0.7, 0]} castShadow>
          <boxGeometry args={[wharf.length * 0.7, 0.8, wharf.width * 0.6]} />
          <meshStandardMaterial color="#e8eaf6" roughness={0.5} metalness={0.2} />
        </mesh>
      )}

      {cranes.map((c) => (
        <PortCrane key={c.key} position={[c.offset, 0.4 + 1.5, -wharf.width / 2 + 0.2]} />
      ))}

      {wharf.zone === 'oil' && (
        <>
          <OilTank position={[-wharf.length * 0.25, 0.8, wharf.width * 0.3]} />
          <OilTank position={[wharf.length * 0.1, 0.8, wharf.width * 0.3]} />
          <OilTank position={[wharf.length * 0.25, 0.8, -wharf.width * 0.2]} />
        </>
      )}

      {wharf.zone === 'container' && (
        <>
          {[-0.3, 0, 0.3].map((xFrac) => (
            <mesh key={`stack-${xFrac}`} position={[wharf.length * xFrac, 0.6, wharf.width * 0.25]} castShadow>
              <boxGeometry args={[wharf.length * 0.15, 0.4, wharf.width * 0.2]} />
              <meshStandardMaterial color="#66bb6a" roughness={0.6} metalness={0.3} />
            </mesh>
          ))}
        </>
      )}
    </group>
  );
}

export function PortGeometry() {
  return (
    <group>
      {PORT_WHARVES.map((w) => (
        <WharfStructure key={w.facilityCode} wharf={w} />
      ))}
    </group>
  );
}
