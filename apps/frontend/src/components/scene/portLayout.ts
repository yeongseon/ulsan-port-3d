export interface PortWharfLayout {
  facilityCode: string;
  length: number;
  width: number;
  rotation: number;
  zone: 'general' | 'container' | 'oil' | 'passenger' | 'bulk';
  lat: number;
  lon: number;
}

export const PORT_WHARVES: PortWharfLayout[] = [
  { facilityCode: 'ULS-B01', lat: 35.511, lon: 129.370, length: 3.0, width: 1.2, rotation: 0.1, zone: 'general' },
  { facilityCode: 'ULS-B02', lat: 35.509, lon: 129.374, length: 2.8, width: 1.1, rotation: 0.15, zone: 'general' },
  { facilityCode: 'ULS-B03', lat: 35.507, lon: 129.378, length: 3.2, width: 1.0, rotation: 0.2, zone: 'general' },
  { facilityCode: 'ULS-B04', lat: 35.505, lon: 129.382, length: 3.5, width: 1.3, rotation: 0.25, zone: 'general' },
  { facilityCode: 'ULS-B05', lat: 35.503, lon: 129.386, length: 3.0, width: 1.0, rotation: 0.3, zone: 'general' },
  { facilityCode: 'ULS-S01', lat: 35.495, lon: 129.376, length: 4.0, width: 1.5, rotation: -0.2, zone: 'bulk' },
  { facilityCode: 'ULS-S02', lat: 35.493, lon: 129.381, length: 3.8, width: 1.4, rotation: -0.15, zone: 'bulk' },
  { facilityCode: 'ULS-OA1', lat: 35.500, lon: 129.393, length: 5.0, width: 2.0, rotation: 0.4, zone: 'oil' },
  { facilityCode: 'ULS-OB1', lat: 35.498, lon: 129.397, length: 5.0, width: 2.0, rotation: 0.45, zone: 'oil' },
  { facilityCode: 'ULS-KT1', lat: 35.514, lon: 129.362, length: 6.0, width: 2.5, rotation: -0.1, zone: 'container' },
  { facilityCode: 'ULS-KT2', lat: 35.512, lon: 129.366, length: 6.0, width: 2.5, rotation: -0.05, zone: 'container' },
  { facilityCode: 'ULS-P01', lat: 35.507, lon: 129.360, length: 4.5, width: 1.8, rotation: -0.3, zone: 'passenger' },
];

export const PORT_LAYOUT_BY_FACILITY: Record<string, PortWharfLayout> = Object.fromEntries(
  PORT_WHARVES.map((w) => [w.facilityCode, w]),
);
