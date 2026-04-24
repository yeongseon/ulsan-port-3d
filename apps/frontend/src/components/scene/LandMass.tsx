import * as THREE from 'three';
import { useMemo } from 'react';
import { latLonToLocal } from '@/utils/coordinates';

/**
 * Realistic Ulsan Port land mass, coastline, breakwaters, and river.
 *
 * Real geography reference (satellite imagery):
 *  - Ulsan Bay (울산만) opens to the southeast
 *  - Main port (본항) on the west shore of the bay
 *  - Container terminal (신항) to the northwest
 *  - Oil terminals on the east side near bay entrance
 *  - Jangsaengpo (장생포) peninsula on the south side
 *  - Taehwa River (태화강) enters from the west into the north part of the bay
 *  - Two breakwaters narrow the bay entrance from north and south
 *
 * All coordinates are real WGS84 lat/lon, converted via latLonToLocal().
 */

// ─── Utility ────────────────────────────────────────────────────────────────

function coordsToShape(coords: [number, number][]): THREE.Shape {
  const pts = coords.map(([lat, lon]) => {
    const p = latLonToLocal(lat, lon, 0);
    return new THREE.Vector2(p.x, p.z);
  });
  const shape = new THREE.Shape();
  shape.moveTo(pts[0].x, pts[0].y);
  for (let i = 1; i < pts.length; i++) {
    shape.lineTo(pts[i].x, pts[i].y);
  }
  shape.closePath();
  return shape;
}

// ─── Coastline Polygons (WGS84: [lat, lon]) ────────────────────────────────

/**
 * Western mainland: the main city land mass behind all port wharves.
 * Traces the coastline from northwest (above container terminal) down to
 * southwest (below bulk terminals), then extends inland.
 *
 * Coastline follows the real curved shoreline of Ulsan Bay's western shore.
 */
const WESTERN_MAINLAND: [number, number][] = [
  // NW inland (off-screen)
  [35.525, 129.340],
  [35.525, 129.358],
  // North coast approaching container terminal
  [35.520, 129.358],
  [35.518, 129.359],
  [35.516, 129.360],   // behind ULS-KT1 (35.514, 129.362)
  [35.515, 129.361],
  [35.514, 129.362],
  // Coast runs SE along the bay — smooth curve behind main berths
  // Wharves extend EAST from this coastline into the water
  [35.513, 129.364],   // behind ULS-KT2 (35.512, 129.366)
  [35.512, 129.366],
  [35.511, 129.368],   // behind ULS-B01 (35.511, 129.370)
  [35.510, 129.370],
  [35.509, 129.372],   // behind ULS-B02 (35.509, 129.374)
  [35.508, 129.374],
  [35.507, 129.376],   // behind ULS-B03 (35.507, 129.378)
  [35.506, 129.378],
  [35.505, 129.380],   // behind ULS-B04 (35.505, 129.382)
  [35.504, 129.382],
  [35.503, 129.384],   // behind ULS-B05 (35.503, 129.386)
  // Coast curves west toward bulk terminals
  [35.501, 129.382],
  [35.499, 129.379],
  [35.497, 129.376],
  [35.496, 129.374],   // behind ULS-S01 (35.495, 129.376)
  [35.494, 129.376],
  [35.493, 129.379],   // behind ULS-S02 (35.493, 129.381)
  [35.492, 129.380],
  // SW coast recedes inland
  [35.490, 129.378],
  [35.488, 129.374],
  [35.486, 129.368],
  [35.485, 129.360],
  // SW inland (off-screen)
  [35.485, 129.340],
];

/**
 * Northern headland / peninsula north of the bay.
 * Extends from the northeast coast, creating the north side of the bay entrance.
 */
const NORTHERN_HEADLAND: [number, number][] = [
  // Start from north inland
  [35.525, 129.390],
  [35.525, 129.410],
  // ── NE coast
  [35.520, 129.410],
  [35.518, 129.405],
  [35.516, 129.400],
  // ── Headland tip (north side of bay entrance)
  [35.514, 129.396],
  [35.513, 129.394],
  [35.512, 129.392],
  // ── Inner bay coast heading west toward river mouth
  [35.513, 129.388],
  [35.514, 129.385],
  [35.516, 129.382],
  [35.518, 129.378],
  [35.520, 129.376],
  [35.522, 129.374],
  [35.524, 129.372],
  [35.525, 129.372],
];

/**
 * Southern peninsula (장생포 Jangsaengpo area).
 * Creates the south side of the bay entrance.
 */
const SOUTHERN_PENINSULA: [number, number][] = [
  // ── West side, connecting to mainland coast
  [35.492, 129.384],
  [35.491, 129.388],
  [35.490, 129.392],
  // ── South coast
  [35.489, 129.396],
  [35.488, 129.400],
  // ── Peninsula tip (south side of bay entrance)
  [35.489, 129.404],
  [35.490, 129.406],
  [35.492, 129.408],
  // ── East coast heading north
  [35.494, 129.406],
  [35.496, 129.404],
  [35.498, 129.402],
  // ── Inner bay coast
  [35.499, 129.400],
  [35.500, 129.398],
  [35.500, 129.396],
  [35.499, 129.394],
  [35.498, 129.392],
  [35.496, 129.390],
  [35.494, 129.388],
  [35.493, 129.386],
  // Far south inland
  [35.485, 129.410],
  [35.485, 129.384],
];

/**
 * North breakwater (북방파제): long narrow structure extending from the
 * north headland southeastward into the bay entrance.
 */
const NORTH_BREAKWATER: [number, number][] = [
  [35.512, 129.392],
  [35.510, 129.396],
  [35.508, 129.400],
  [35.507, 129.402],  // tip
  [35.507, 129.403],
  [35.508, 129.401],
  [35.510, 129.397],
  [35.512, 129.393],
];

/**
 * South breakwater (남방파제): extends from the south peninsula
 * northwestward toward the bay entrance.
 */
const SOUTH_BREAKWATER: [number, number][] = [
  [35.498, 129.402],
  [35.500, 129.404],
  [35.502, 129.406],
  [35.503, 129.407],  // tip
  [35.504, 129.407],
  [35.503, 129.406],
  [35.501, 129.404],
  [35.499, 129.402],
];

/**
 * Taehwa River channel: a water channel cutting into the western mainland
 * from the east. Rendered as a separate blue shape above the land.
 */
const TAEHWA_RIVER: [number, number][] = [
  // ── River mouth (east, opening to bay)
  [35.514, 129.378],
  [35.515, 129.376],
  [35.516, 129.372],
  [35.517, 129.368],
  [35.518, 129.364],
  [35.519, 129.358],
  [35.520, 129.352],
  [35.521, 129.348],
  // ── North bank going west (wider inland)
  [35.522, 129.348],
  [35.521, 129.352],
  [35.520, 129.358],
  [35.519, 129.363],
  [35.518, 129.368],
  [35.517, 129.373],
  [35.516, 129.376],
  [35.515, 129.379],
];

// ─── Materials (shared at module scope) ──────────────────────────────────────

const LAND_MATERIAL = new THREE.MeshStandardMaterial({
  color: '#8fbc8f',   // dark sea green - natural land
  roughness: 0.95,
  metalness: 0.0,
  side: THREE.DoubleSide,
});

const URBAN_MATERIAL = new THREE.MeshStandardMaterial({
  color: '#b0bec5',   // blue-grey for built-up port areas
  roughness: 0.85,
  metalness: 0.1,
  side: THREE.DoubleSide,
});

const BREAKWATER_MATERIAL = new THREE.MeshStandardMaterial({
  color: '#78909c',   // concrete grey
  roughness: 0.8,
  metalness: 0.15,
  side: THREE.DoubleSide,
});

const RIVER_MATERIAL = new THREE.MeshStandardMaterial({
  color: '#5c99b5',   // slightly different blue from sea
  roughness: 0.3,
  metalness: 0.2,
  transparent: true,
  opacity: 0.9,
  side: THREE.DoubleSide,
});

const SAND_MATERIAL = new THREE.MeshStandardMaterial({
  color: '#d4c5a9',   // sandy beach color
  roughness: 0.95,
  metalness: 0.0,
  side: THREE.DoubleSide,
});

// ─── Extrude settings ───────────────────────────────────────────────────────

const LAND_EXTRUDE: THREE.ExtrudeGeometryOptions = {
  depth: 0.6,     // land height above sea level
  bevelEnabled: false,
};

const BREAKWATER_EXTRUDE: THREE.ExtrudeGeometryOptions = {
  depth: 0.8,     // breakwater slightly higher than land
  bevelEnabled: false,
};

const RIVER_EXTRUDE: THREE.ExtrudeGeometryOptions = {
  depth: 0.02,    // paper-thin, just above sea level
  bevelEnabled: false,
};

// ─── Geometry builders (module scope, computed once) ─────────────────────────

function buildExtrudedGeo(
  coords: [number, number][],
  opts: THREE.ExtrudeGeometryOptions,
): THREE.ExtrudeGeometry {
  const shape = coordsToShape(coords);
  return new THREE.ExtrudeGeometry(shape, opts);
}

// ─── Port area overlay: flat colored zones behind wharves ────────────────────

/**
 * Industrial/urban zone behind the main port wharves.
 * Sits slightly above the land to show the port facility footprint.
 */
const PORT_INDUSTRIAL_ZONE: [number, number][] = [
  // Narrow strip between coastline and wharf edges (landward side of wharves)
  [35.516, 129.360],
  [35.514, 129.362],
  [35.512, 129.366],
  [35.511, 129.368],
  [35.509, 129.372],
  [35.507, 129.376],
  [35.505, 129.380],
  [35.503, 129.384],
  [35.501, 129.382],
  [35.498, 129.378],
  [35.496, 129.374],
  [35.494, 129.376],
  [35.493, 129.379],
  // Return inland (slightly west of the above)
  [35.494, 129.375],
  [35.497, 129.373],
  [35.500, 129.377],
  [35.502, 129.381],
  [35.504, 129.381],
  [35.506, 129.377],
  [35.508, 129.373],
  [35.510, 129.369],
  [35.512, 129.365],
  [35.514, 129.361],
  [35.516, 129.359],
];

// ─── Shoreline detail: sandy strips along the coast ─────────────────────────

const BEACH_STRIPS: [number, number][][] = [
  // Small beach north of main port
  [
    [35.514, 129.380],
    [35.513, 129.384],
    [35.512, 129.386],
    [35.512, 129.387],
    [35.513, 129.385],
    [35.514, 129.381],
  ],
];

// ─── Component ──────────────────────────────────────────────────────────────

export function LandMass() {
  const geometries = useMemo(() => {
    const westernGeo = buildExtrudedGeo(WESTERN_MAINLAND, LAND_EXTRUDE);
    const northernGeo = buildExtrudedGeo(NORTHERN_HEADLAND, LAND_EXTRUDE);
    const southernGeo = buildExtrudedGeo(SOUTHERN_PENINSULA, LAND_EXTRUDE);
    const northBWGeo = buildExtrudedGeo(NORTH_BREAKWATER, BREAKWATER_EXTRUDE);
    const southBWGeo = buildExtrudedGeo(SOUTH_BREAKWATER, BREAKWATER_EXTRUDE);
    const riverGeo = buildExtrudedGeo(TAEHWA_RIVER, RIVER_EXTRUDE);
    const industrialGeo = buildExtrudedGeo(PORT_INDUSTRIAL_ZONE, {
      depth: 0.05,
      bevelEnabled: false,
    });
    const beachGeos = BEACH_STRIPS.map((strip) =>
      buildExtrudedGeo(strip, { depth: 0.03, bevelEnabled: false }),
    );

    return {
      westernGeo,
      northernGeo,
      southernGeo,
      northBWGeo,
      southBWGeo,
      riverGeo,
      industrialGeo,
      beachGeos,
    };
  }, []);

  // ExtrudeGeometry extrudes along Z in shape-local space.
  // We rotate -PI/2 around X so it extrudes upward (Y+).
  return (
    <group>
      {/* Western mainland */}
      <mesh
        geometry={geometries.westernGeo}
        material={LAND_MATERIAL}
        rotation={[-Math.PI / 2, 0, 0]}
        position={[0, 0, 0]}
        receiveShadow
      />

      {/* Northern headland */}
      <mesh
        geometry={geometries.northernGeo}
        material={LAND_MATERIAL}
        rotation={[-Math.PI / 2, 0, 0]}
        position={[0, 0, 0]}
        receiveShadow
      />

      {/* Southern peninsula (장생포) */}
      <mesh
        geometry={geometries.southernGeo}
        material={LAND_MATERIAL}
        rotation={[-Math.PI / 2, 0, 0]}
        position={[0, 0, 0]}
        receiveShadow
      />

      {/* Port industrial zone overlay */}
      <mesh
        geometry={geometries.industrialGeo}
        material={URBAN_MATERIAL}
        rotation={[-Math.PI / 2, 0, 0]}
        position={[0, 0.6, 0]}
        receiveShadow
      />

      {/* North breakwater */}
      <mesh
        geometry={geometries.northBWGeo}
        material={BREAKWATER_MATERIAL}
        rotation={[-Math.PI / 2, 0, 0]}
        position={[0, 0, 0]}
        castShadow
        receiveShadow
      />

      {/* South breakwater */}
      <mesh
        geometry={geometries.southBWGeo}
        material={BREAKWATER_MATERIAL}
        rotation={[-Math.PI / 2, 0, 0]}
        position={[0, 0, 0]}
        castShadow
        receiveShadow
      />

      {/* Taehwa River */}
      <mesh
        geometry={geometries.riverGeo}
        material={RIVER_MATERIAL}
        rotation={[-Math.PI / 2, 0, 0]}
        position={[0, 0.62, 0]}
      />

      {/* Beach strips */}
      {geometries.beachGeos.map((geo, idx) => {
        const beachKeys = ['north-main-port'];
        return (
          <mesh
            key={beachKeys[idx] ?? `beach-extra-${idx}`}
            geometry={geo}
            material={SAND_MATERIAL}
            rotation={[-Math.PI / 2, 0, 0]}
            position={[0, 0.58, 0]}
            receiveShadow
          />
        );
      })}
    </group>
  );
}
