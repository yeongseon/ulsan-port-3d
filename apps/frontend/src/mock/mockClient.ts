import { apiClient } from '@/api/client';
import type { Berth, Vessel, WeatherData } from '@/stores/dataStore';
import {
  mockAlerts,
  mockArrivalStats,
  mockBerths,
  mockCongestionStats,
  mockGraph,
  mockInsights,
  mockScenarioFrames,
  mockScenarios,
  mockVessels,
  mockWeather,
} from '@/mock/data';

function cloneVessel(vessel: Vessel): Vessel {
  return { ...vessel };
}

function cloneBerth(berth: Berth): Berth {
  return { ...berth };
}

function cloneWeather(weather: WeatherData): WeatherData {
  return { ...weather };
}

function randomDelay(): number {
  return Math.floor(Math.random() * 151) + 50;
}

function withDelay<T>(factory: () => T): Promise<T> {
  return new Promise((resolve, reject) => {
    window.setTimeout(() => {
      try {
        resolve(factory());
      } catch (error) {
        reject(error);
      }
    }, randomDelay());
  });
}

function requireVessel(id: string): Vessel {
  const vessel = mockVessels.find((entry) => entry.vessel_id === id);
  if (!vessel) {
    throw new Error(`Mock vessel not found: ${id}`);
  }

  return cloneVessel(vessel);
}

function requireBerth(id: string): Berth {
  const berth = mockBerths.find((entry) => entry.berth_id === id);
  if (!berth) {
    throw new Error(`Mock berth not found: ${id}`);
  }

  return cloneBerth(berth);
}

export const mockApiClient: typeof apiClient = {
  getVessels: () => withDelay(() => mockVessels.map(cloneVessel)),
  getBerths: () => withDelay(() => mockBerths.map(cloneBerth)),
  getWeather: () => withDelay(() => cloneWeather(mockWeather)),
  getVesselById: (id: string) => withDelay(() => requireVessel(id)),
  getBerthById: (id: string) => withDelay(() => requireBerth(id)),
  getInsights: () => withDelay(() => mockInsights.map((entry) => ({ ...entry }))),
  getAlerts: () => withDelay(() => mockAlerts.map((entry) => ({ ...entry }))),
  getScenarios: () => withDelay(() => mockScenarios.map((entry) => ({ ...entry }))),
  getScenarioFrames: (id: string) => withDelay(() => (mockScenarioFrames[id] ?? []).map((entry) => ({ ...entry }))),
  getGraph: (_type: string, _id: string) => withDelay(() => ({
    center: { ...mockGraph.center },
    relations: mockGraph.relations.map((entry) => ({
      ...entry,
      node: { ...entry.node },
    })),
  })),
  getStats: () => withDelay(() => mockArrivalStats.map((entry) => ({ ...entry }))),
  getCongestion: () => withDelay(() => mockCongestionStats.map((entry) => ({ ...entry }))),
};
