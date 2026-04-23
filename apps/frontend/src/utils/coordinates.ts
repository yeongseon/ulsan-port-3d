/**
 * Coordinate utilities for converting WGS84 lat/lon to local 3D coordinates
 * centered on Ulsan Port (lat: 35.5, lon: 129.38).
 *
 * Convention:
 *   X axis → East
 *   Z axis → South (THREE.js right-handed, Y-up)
 *   Y axis → altitude (meters)
 *
 * Scale: 1 THREE.js unit = 100 meters
 */

export const PORT_CENTER_LAT = 35.5;
export const PORT_CENTER_LON = 129.38;

// Approximate meters per degree at Ulsan latitude
const METERS_PER_DEG_LAT = 111_000;
const METERS_PER_DEG_LON = 111_000 * Math.cos((PORT_CENTER_LAT * Math.PI) / 180); // ≈ 90_900

const SCALE = 1 / 100; // 1 unit = 100 m

export interface LocalCoord {
  x: number; // east offset (units)
  y: number; // altitude (units)
  z: number; // south offset (units, negative = north)
}

/** Convert WGS84 lat/lon/alt_m to local 3D coordinates */
export function latLonToLocal(lat: number, lon: number, altMeters = 0): LocalCoord {
  const dx = (lon - PORT_CENTER_LON) * METERS_PER_DEG_LON * SCALE;
  const dz = -(lat - PORT_CENTER_LAT) * METERS_PER_DEG_LAT * SCALE; // negate so north = -Z
  const dy = altMeters * SCALE;
  return { x: dx, y: dy, z: dz };
}

/** Convert local 3D coordinates back to WGS84 */
export function localToLatLon(x: number, z: number): { lat: number; lon: number } {
  const lon = PORT_CENTER_LON + x / (METERS_PER_DEG_LON * SCALE);
  const lat = PORT_CENTER_LAT + -z / (METERS_PER_DEG_LAT * SCALE);
  return { lat, lon };
}

/** Return distance in meters between two WGS84 points (Haversine) */
export function haversineMeters(
  lat1: number,
  lon1: number,
  lat2: number,
  lon2: number,
): number {
  const R = 6_371_000;
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLon = ((lon2 - lon1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLon / 2) ** 2;
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}
