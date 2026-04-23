import { Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Environment, Stars } from '@react-three/drei';
import { SeaPlane } from './SeaPlane';
import { PortGeometry } from './PortGeometry';
import { VesselLayer } from './VesselLayer';
import { BerthStatusLayer } from './BerthStatusLayer';
import { RouteLayer } from './RouteLayer';
import { useDataStore } from '@/stores/dataStore';
import { useMapStore } from '@/stores/mapStore';

function SceneContent() {
  const vessels = useDataStore((s) => s.vessels);
  const berths = useDataStore((s) => s.berths);
  const activeLayerIds = useMapStore((s) => s.activeLayerIds);
  const cameraPosition = useMapStore((s) => s.cameraPosition);

  return (
    <>
      <color attach="background" args={['#060b18']} />
      <fog attach="fog" args={['#060b18', 200, 1500]} />

      <ambientLight intensity={0.15} />
      <directionalLight
        position={[100, 200, 100]}
        intensity={1.2}
        castShadow
        shadow-mapSize={[2048, 2048]}
      />
      <pointLight position={[0, 80, 0]} intensity={0.4} color="#4a90d9" />

      <Stars radius={800} depth={100} count={5000} factor={4} saturation={0} fade />

      <Environment preset="night" />

      <SeaPlane />
      <PortGeometry />

      {activeLayerIds.includes('berths') && <BerthStatusLayer berths={berths} />}
      {activeLayerIds.includes('vessels') && <VesselLayer vessels={vessels} />}
      {activeLayerIds.includes('routes') && <RouteLayer />}

      <OrbitControls
        enablePan
        enableZoom
        enableRotate
        minDistance={20}
        maxDistance={1200}
        maxPolarAngle={Math.PI / 2.1}
        target={[0, 0, 0]}
      />

      <gridHelper
        args={[2000, 100, '#1a2744', '#0d1529']}
        position={[0, 0.1, 0]}
      />

      <axesHelper args={[50]} />

      <perspectiveCamera
        position={cameraPosition}
        fov={55}
        near={0.5}
        far={3000}
      />
    </>
  );
}

export function PortScene() {
  return (
    <Canvas
      shadows
      gl={{ antialias: true, alpha: false, powerPreference: 'high-performance' }}
      className="w-full h-full"
      style={{ background: '#060b18' }}
    >
      <Suspense fallback={null}>
        <SceneContent />
      </Suspense>
    </Canvas>
  );
}
