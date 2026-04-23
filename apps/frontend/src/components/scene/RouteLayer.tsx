import { useMemo } from 'react';
import * as THREE from 'three';
import { latLonToLocal } from '@/utils/coordinates';

interface RoutePoint {
  lat: number;
  lon: number;
}

interface Route {
  id: string;
  points: RoutePoint[];
  color: string;
}

const SHIPPING_ROUTES: Route[] = [
  {
    id: 'main-channel',
    color: '#3b82f6',
    points: [
      { lat: 35.48, lon: 129.38 },
      { lat: 35.49, lon: 129.381 },
      { lat: 35.50, lon: 129.383 },
      { lat: 35.51, lon: 129.384 },
      { lat: 35.52, lon: 129.385 },
    ],
  },
  {
    id: 'oil-approach',
    color: '#f59e0b',
    points: [
      { lat: 35.50, lon: 129.40 },
      { lat: 35.50, lon: 129.395 },
      { lat: 35.50, lon: 129.39 },
    ],
  },
  {
    id: 'container-route',
    color: '#22c55e',
    points: [
      { lat: 35.52, lon: 129.36 },
      { lat: 35.515, lon: 129.363 },
      { lat: 35.513, lon: 129.366 },
    ],
  },
];

function RouteLine({ route }: { route: Route }) {
  const lineObj = useMemo(() => {
    const pts = route.points.map((p) => {
      const local = latLonToLocal(p.lat, p.lon, 3);
      return new THREE.Vector3(local.x, local.y, local.z);
    });
    const geometry = new THREE.BufferGeometry().setFromPoints(pts);
    const material = new THREE.LineBasicMaterial({ color: route.color });
    return new THREE.Line(geometry, material);
  }, [route]);

  return <primitive object={lineObj} />;
}

export function RouteLayer() {
  return (
    <group>
      {SHIPPING_ROUTES.map((route) => (
        <RouteLine key={route.id} route={route} />
      ))}
    </group>
  );
}
