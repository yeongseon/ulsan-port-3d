import type { Vessel } from '@/stores/dataStore';
import { mockVessels } from '@/mock/data';

function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value));
}

function randomDelta(magnitude: number): number {
  return (Math.random() * 2 - 1) * magnitude;
}

function cloneVessel(vessel: Vessel): Vessel {
  return { ...vessel };
}

function nextVesselState(vessel: Vessel): Vessel {
  return {
    ...vessel,
    lat: clamp(vessel.lat + randomDelta(0.001), 35.49, 35.52),
    lon: clamp(vessel.lon + randomDelta(0.001), 129.36, 129.4),
    speed: Math.max(0, Number((vessel.speed + randomDelta(1)).toFixed(1))),
    course: (vessel.course + randomDelta(6) + 360) % 360,
    heading: (vessel.heading + randomDelta(6) + 360) % 360,
    updated_at: new Date().toISOString(),
  };
}

export function startMockWebSocket(onMessage: (data: unknown) => void): () => void {
  let currentVessels = mockVessels.map(cloneVessel);

  const intervalId = window.setInterval(() => {
    currentVessels = currentVessels.map(nextVesselState);
    onMessage({
      event: 'vessel_update',
      payload: currentVessels.map(cloneVessel),
    });
  }, 5_000);

  return () => {
    window.clearInterval(intervalId);
  };
}
