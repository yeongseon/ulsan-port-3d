import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

export function SeaPlane() {
  const meshRef = useRef<THREE.Mesh>(null);
  const timeRef = useRef(0);

  useFrame((_, delta) => {
    timeRef.current += delta * 0.3;
    if (meshRef.current) {
      (meshRef.current.material as THREE.MeshStandardMaterial).map?.offset.set(
        Math.sin(timeRef.current * 0.1) * 0.01,
        timeRef.current * 0.005,
      );
    }
  });

  return (
    <mesh ref={meshRef} rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
      <planeGeometry args={[2000, 2000, 64, 64]} />
      <meshStandardMaterial
        color="#4a9ece"
        roughness={0.2}
        metalness={0.3}
        transparent
        opacity={0.85}
      />
    </mesh>
  );
}
