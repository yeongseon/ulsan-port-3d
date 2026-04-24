import { apiClient } from '@/api/client';
import { mockApiClient } from '@/mock/mockClient';

export { startMockWebSocket } from '@/mock/mockWebSocket';
export { mockApiClient } from '@/mock/mockClient';
export * from '@/mock/data';

export function isMockMode(): boolean {
  return import.meta.env.VITE_USE_MOCK === 'true';
}

export function enableMocks(): typeof apiClient {
  Object.assign(apiClient, mockApiClient);
  return apiClient;
}
