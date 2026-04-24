export function SeaPlane() {
  return (
    <mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
      <planeGeometry args={[2000, 2000, 1, 1]} />
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
