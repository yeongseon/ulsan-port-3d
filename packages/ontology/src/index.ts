export const ONTOLOGY_CLASSES = {
  spatial: ['Port', 'Zone', 'Berth', 'Buoy', 'RouteSegment', 'Terminal', 'TankTerminal', 'Operator'],
  operational: ['Vessel', 'VoyageCall', 'VesselPosition', 'VesselEvent', 'BerthStatus', 'CongestionStat'],
  cargo: ['CargoType', 'LiquidCargoStat', 'ArrivalStat'],
  environmental: ['WeatherObservation', 'WeatherForecast', 'TideObservation', 'HazardDoc', 'MsdsDoc', 'SafetyManual'],
  ui: ['Alert', 'Insight', 'ScenarioFrame'],
} as const;

export type OntologyClass = (typeof ONTOLOGY_CLASSES)[keyof typeof ONTOLOGY_CLASSES][number];

export interface OntologyRelation {
  subject: string;
  predicate: string;
  object: string;
}

export const ONTOLOGY_RELATIONS: OntologyRelation[] = [
  { subject: 'Port', predicate: 'hasZone', object: 'Zone' },
  { subject: 'Zone', predicate: 'hasBerth', object: 'Berth' },
  { subject: 'Zone', predicate: 'hasBuoy', object: 'Buoy' },
  { subject: 'Zone', predicate: 'hasRouteSegment', object: 'RouteSegment' },
  { subject: 'Operator', predicate: 'operates', object: 'Berth' },
  { subject: 'Operator', predicate: 'operates', object: 'TankTerminal' },
  { subject: 'TankTerminal', predicate: 'locatedIn', object: 'Zone' },
  { subject: 'TankTerminal', predicate: 'stores', object: 'CargoType' },
  { subject: 'Vessel', predicate: 'hasVoyageCall', object: 'VoyageCall' },
  { subject: 'VoyageCall', predicate: 'usesFacility', object: 'Berth' },
  { subject: 'VoyageCall', predicate: 'hasEvent', object: 'VesselEvent' },
  { subject: 'Vessel', predicate: 'hasPosition', object: 'VesselPosition' },
  { subject: 'Berth', predicate: 'hasStatus', object: 'BerthStatus' },
  { subject: 'Berth', predicate: 'handlesCargo', object: 'CargoType' },
  { subject: 'Zone', predicate: 'hasWeather', object: 'WeatherObservation' },
  { subject: 'Zone', predicate: 'hasForecast', object: 'WeatherForecast' },
  { subject: 'Zone', predicate: 'hasTide', object: 'TideObservation' },
  { subject: 'Operator', predicate: 'hasHazardDoc', object: 'HazardDoc' },
  { subject: 'CargoType', predicate: 'hasMsds', object: 'MsdsDoc' },
];

export function getRelationsFor(entityType: string): OntologyRelation[] {
  return ONTOLOGY_RELATIONS.filter(
    (r) => r.subject === entityType || r.object === entityType,
  );
}

export function getRelatedTypes(entityType: string): string[] {
  const related = new Set<string>();
  for (const r of ONTOLOGY_RELATIONS) {
    if (r.subject === entityType) related.add(r.object);
    if (r.object === entityType) related.add(r.subject);
  }
  return [...related];
}
