import { useMemo } from 'react';
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

interface ShipConfig {
  length: number;
  beam: number;
  hullHeight: number;
  bowTaper: number;
  bridgePos: number;
  bridgeW: number;
  bridgeD: number;
  bridgeH: number;
  deckDetails: 'containers' | 'tanks' | 'none';
}

const SHIP_CONFIGS: Record<string, ShipConfig> = {
  container: {
    length: 3.5, beam: 0.6, hullHeight: 0.25, bowTaper: 0.7,
    bridgePos: 0.88, bridgeW: 0.35, bridgeD: 0.3, bridgeH: 0.4,
    deckDetails: 'containers',
  },
  tanker: {
    length: 3.2, beam: 0.55, hullHeight: 0.2, bowTaper: 0.6,
    bridgePos: 0.85, bridgeW: 0.3, bridgeD: 0.28, bridgeH: 0.35,
    deckDetails: 'tanks',
  },
  cargo: {
    length: 2.8, beam: 0.5, hullHeight: 0.22, bowTaper: 0.65,
    bridgePos: 0.5, bridgeW: 0.28, bridgeD: 0.25, bridgeH: 0.35,
    deckDetails: 'none',
  },
  passenger: {
    length: 3.0, beam: 0.5, hullHeight: 0.2, bowTaper: 0.75,
    bridgePos: 0.3, bridgeW: 0.4, bridgeD: 0.55, bridgeH: 0.5,
    deckDetails: 'none',
  },
  tug: {
    length: 1.0, beam: 0.3, hullHeight: 0.15, bowTaper: 0.5,
    bridgePos: 0.45, bridgeW: 0.2, bridgeD: 0.18, bridgeH: 0.25,
    deckDetails: 'none',
  },
};

const DEFAULT_CONFIG: ShipConfig = {
  length: 2.0, beam: 0.4, hullHeight: 0.18, bowTaper: 0.6,
  bridgePos: 0.7, bridgeW: 0.22, bridgeD: 0.2, bridgeH: 0.3,
  deckDetails: 'none',
};

/** Hull outline: pointed bow, wide mid-section, squared stern — extruded upward for 3D volume. */
function createHullShape(length: number, beam: number, bowTaper: number): THREE.Shape {
  const halfL = length / 2;
  const halfB = beam / 2;
  const bowX = halfL;
  const sternX = -halfL;
  // taper: 0 = full width bow, 1 = needle-sharp bow
  const bowHalfB = halfB * (1 - bowTaper);

  const shape = new THREE.Shape();
  shape.moveTo(sternX, -halfB);
  shape.lineTo(sternX, halfB);
  shape.quadraticCurveTo(halfL * 0.3, halfB * 1.05, bowX, bowHalfB);
  shape.lineTo(bowX, -bowHalfB);
  shape.quadraticCurveTo(halfL * 0.3, -halfB * 1.05, sternX, -halfB);

  return shape;
}

function useShipGeometries(cfg: ShipConfig) {
  return useMemo(() => {
    const hullShape = createHullShape(cfg.length, cfg.beam, cfg.bowTaper);
    const hullGeo = new THREE.ExtrudeGeometry(hullShape, {
      depth: cfg.hullHeight,
      bevelEnabled: false,
    });
    // Extrude along Y axis
    hullGeo.rotateX(-Math.PI / 2);

    return { hullGeo };
  }, [cfg.length, cfg.beam, cfg.bowTaper, cfg.hullHeight]);
}

function ContainerStacks({ cfg, color }: { cfg: ShipConfig; color: string }) {
  const halfL = cfg.length / 2;
  const rows = 4;
  const startX = -halfL * 0.4;
  const endX = halfL * 0.6;
  const step = (endX - startX) / rows;
  const containerH = 0.08;

  const blocks: Array<{ x: number; y: number; even: boolean }> = [];
  for (let row = 0; row < rows; row++) {
    const x = startX + step * row + step * 0.5;
    const layers = row % 2 === 0 ? 3 : 2;
    for (let layer = 0; layer < layers; layer++) {
      blocks.push({ x, y: cfg.hullHeight + containerH * 0.5 + containerH * layer, even: layer % 2 === 0 });
    }
  }

  return (
    <>
      {blocks.map((b) => (
        <mesh key={`${b.x.toFixed(3)}-${b.y.toFixed(3)}`} position={[b.x, b.y, 0]} castShadow>
          <boxGeometry args={[step * 0.85, containerH, cfg.beam * 0.7]} />
          <meshStandardMaterial
            color={b.even ? color : '#e2e8f0'}
            roughness={0.6}
            metalness={0.3}
          />
        </mesh>
      ))}
    </>
  );
}

function TankDomes({ cfg, color }: { cfg: ShipConfig; color: string }) {
  const halfL = cfg.length / 2;
  const tanks = 3;
  const startX = -halfL * 0.3;
  const endX = halfL * 0.5;
  const step = (endX - startX) / tanks;
  const domeR = cfg.beam * 0.28;

  return (
    <>
      {Array.from({ length: tanks }, (_, i) => {
        const posX = startX + step * i + step * 0.5;
        return (
          <mesh
            key={`tank-${posX.toFixed(2)}`}
            position={[posX, cfg.hullHeight + domeR * 0.5, 0]}
            castShadow
          >
            <sphereGeometry args={[domeR, 12, 8, 0, Math.PI * 2, 0, Math.PI / 2]} />
            <meshStandardMaterial color={color} roughness={0.4} metalness={0.5} />
          </mesh>
        );
      })}
    </>
  );
}

function VesselMarker({ vessel }: { vessel: Vessel }) {
  const selectEntity = useMapStore((s) => s.selectEntity);

  const pos = latLonToLocal(vessel.lat, vessel.lon, 5);
  const color = TYPE_COLORS[vessel.ship_type] ?? TYPE_COLORS.default;
  const headingRad = ((vessel.heading ?? 0) * Math.PI) / 180;
  const cfg = SHIP_CONFIGS[vessel.ship_type] ?? DEFAULT_CONFIG;
  const { hullGeo } = useShipGeometries(cfg);

  const handleClick = (e: ThreeEvent<MouseEvent>) => {
    e.stopPropagation();
    selectEntity('vessel', vessel.vessel_id);
  };

  const halfL = cfg.length / 2;
  const bridgeX = -halfL + cfg.length * cfg.bridgePos;

  return (
    <group position={[pos.x, pos.y, pos.z]} rotation={[0, -headingRad, 0]}>
      <mesh geometry={hullGeo} onPointerUp={handleClick} castShadow receiveShadow>
        <meshStandardMaterial color={color} roughness={0.5} metalness={0.3} />
      </mesh>

      <mesh position={[0, cfg.hullHeight * 0.15, 0]} onPointerUp={handleClick}>
        <boxGeometry args={[cfg.length * 0.92, cfg.hullHeight * 0.3, cfg.beam * 0.98]} />
        <meshStandardMaterial color="#991b1b" roughness={0.7} metalness={0.2} />
      </mesh>

      <mesh position={[0, cfg.hullHeight, 0]} receiveShadow>
        <boxGeometry args={[cfg.length * 0.9, 0.02, cfg.beam * 0.85]} />
        <meshStandardMaterial color="#94a3b8" roughness={0.8} metalness={0.1} />
      </mesh>

      <mesh position={[bridgeX, cfg.hullHeight + cfg.bridgeH * 0.5, 0]} castShadow>
        <boxGeometry args={[cfg.bridgeD, cfg.bridgeH, cfg.bridgeW]} />
        <meshStandardMaterial color="#f1f5f9" roughness={0.4} metalness={0.2} />
      </mesh>

      <mesh position={[bridgeX + cfg.bridgeD * 0.51, cfg.hullHeight + cfg.bridgeH * 0.65, 0]}>
        <boxGeometry args={[0.01, cfg.bridgeH * 0.25, cfg.bridgeW * 0.8]} />
        <meshStandardMaterial color="#1e3a5f" roughness={0.2} metalness={0.8} />
      </mesh>

      <mesh position={[bridgeX, cfg.hullHeight + cfg.bridgeH + 0.08, 0]}>
        <cylinderGeometry args={[0.01, 0.01, 0.16, 4]} />
        <meshStandardMaterial color="#475569" roughness={0.6} metalness={0.5} />
      </mesh>

      {cfg.deckDetails === 'containers' && <ContainerStacks cfg={cfg} color={color} />}
      {cfg.deckDetails === 'tanks' && <TankDomes cfg={cfg} color={color} />}

      <pointLight color={color} intensity={0.3} distance={15} />
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
