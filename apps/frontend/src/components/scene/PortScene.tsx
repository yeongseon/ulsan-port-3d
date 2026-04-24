import { Suspense, memo } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Environment, PerspectiveCamera } from '@react-three/drei';
import { SeaPlane } from './SeaPlane';
import { LandMass } from './LandMass';
import { PortGeometry } from './PortGeometry';
import { VesselLayer } from './VesselLayer';
import { BerthStatusLayer } from './BerthStatusLayer';
import { RouteLayer } from './RouteLayer';
import { useDataStore } from '@/stores/dataStore';
import { useMapStore } from '@/stores/mapStore';

const StaticScene = memo(function StaticScene() {
  return (
    <>
      <color attach="background" args={['#e8f4f8']} />
      <fog attach="fog" args={['#e8f4f8', 400, 2000]} />

      <ambientLight intensity={0.7} />
      <directionalLight
        position={[100, 200, 100]}
        intensity={1.5}
        castShadow
        shadow-mapSize={[2048, 2048]}
        shadow-camera-left={-80}
        shadow-camera-right={80}
        shadow-camera-top={80}
        shadow-camera-bottom={-80}
        shadow-camera-near={1}
        shadow-camera-far={400}
      />
      <pointLight position={[0, 80, 0]} intensity={0.3} color="#87ceeb" />

      <Environment preset="city" />

      <SeaPlane />
      <LandMass />
      <PortGeometry />
    </>
  );
});

function DynamicLayers() {
  const vessels = useDataStore((s) => s.vessels);
  const berths = useDataStore((s) => s.berths);
  const activeLayerIds = useMapStore((s) => s.activeLayerIds);

  return (
    <>
      {activeLayerIds.includes('berths') && <BerthStatusLayer berths={berths} />}
      {activeLayerIds.includes('vessels') && <VesselLayer vessels={vessels} />}
      {activeLayerIds.includes('routes') && <RouteLayer />}
    </>
  );
}

function SceneContent() {
  return (
    <>
      <StaticScene />
      <DynamicLayers />

      <OrbitControls
        enablePan
        enableZoom
        enableRotate
        minDistance={20}
        maxDistance={1200}
        maxPolarAngle={Math.PI / 2.1}
        target={[0, 0, 0]}
      />

      <PerspectiveCamera
        makeDefault
        position={[0, 40, 60]}
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
      style={{ background: '#e8f4f8' }}
    >
      <Suspense fallback={null}>
        <SceneContent />
      </Suspense>
    </Canvas>
  );
}
