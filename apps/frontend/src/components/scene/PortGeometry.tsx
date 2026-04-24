import { latLonToLocal } from '@/utils/coordinates';

interface BerthDef {
  name: string;
  lat: number;
  lon: number;
  width: number;
  depth: number;
}

const BERTH_DEFINITIONS: BerthDef[] = [
  { name: '1부두', lat: 35.511, lon: 129.370, width: 30, depth: 20 },
  { name: '2부두', lat: 35.509, lon: 129.374, width: 28, depth: 22 },
  { name: '3부두', lat: 35.507, lon: 129.378, width: 32, depth: 18 },
  { name: '4부두', lat: 35.505, lon: 129.382, width: 35, depth: 25 },
  { name: '5부두', lat: 35.503, lon: 129.386, width: 30, depth: 20 },
  { name: '남항 1', lat: 35.495, lon: 129.376, width: 40, depth: 28 },
  { name: '남항 2', lat: 35.493, lon: 129.381, width: 38, depth: 26 },
  { name: '오일터미널 A', lat: 35.500, lon: 129.393, width: 50, depth: 35 },
  { name: '오일터미널 B', lat: 35.498, lon: 129.397, width: 50, depth: 35 },
  { name: '컨테이너 1', lat: 35.514, lon: 129.362, width: 60, depth: 40 },
  { name: '컨테이너 2', lat: 35.512, lon: 129.366, width: 60, depth: 40 },
  { name: '여객터미널', lat: 35.507, lon: 129.360, width: 45, depth: 30 },
];

const CRANE_POSITIONS = [0, 1, 2, 3, 4, 5, 6, 7].map((i) => ({
  key: `crane-${i}`,
  angle: (i / 8) * Math.PI * 2,
}));

const UNIT_SCALE = 1 / 100;

export function PortGeometry() {
  return (
    <group>
      <mesh position={[0, 0.5, 0]} rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
        <planeGeometry args={[120, 80]} />
        <meshStandardMaterial color="#b0bec5" roughness={0.9} metalness={0.1} />
      </mesh>

      {BERTH_DEFINITIONS.map((berth) => {
        const pos = latLonToLocal(berth.lat, berth.lon, 2);
        const w = berth.width * UNIT_SCALE;
        const d = berth.depth * UNIT_SCALE;
        return (
          <group key={berth.name} position={[pos.x, pos.y, pos.z]}>
            <mesh castShadow receiveShadow>
              <boxGeometry args={[w, 0.4, d]} />
              <meshStandardMaterial color="#78909c" roughness={0.8} metalness={0.2} />
            </mesh>
            <mesh>
              <boxGeometry args={[w + 0.05, 0.45, d + 0.05]} />
              <meshStandardMaterial color="#2563eb" wireframe />
            </mesh>
          </group>
        );
      })}

      {CRANE_POSITIONS.map(({ key, angle }) => {
        const r = 15;
        return (
          <mesh key={key} position={[Math.cos(angle) * r, 3, Math.sin(angle) * r]} castShadow>
            <cylinderGeometry args={[0.3, 0.3, 6, 8]} />
            <meshStandardMaterial color="#546e7a" roughness={0.7} metalness={0.5} />
          </mesh>
        );
      })}
    </group>
  );
}
