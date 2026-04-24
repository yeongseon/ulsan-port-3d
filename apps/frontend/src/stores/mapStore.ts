import { create } from 'zustand';

interface MapState {
  cameraPosition: [number, number, number];
  activeLayerIds: string[];
  selectedEntityId: string | null;
  selectedEntityType: string | null;
  zoomLevel: number;
  setCameraPosition: (pos: [number, number, number]) => void;
  toggleLayer: (layerId: string) => void;
  selectEntity: (type: string | null, id: string | null) => void;
  setZoomLevel: (level: number) => void;
}

export const useMapStore = create<MapState>((set) => ({
  cameraPosition: [0, 40, 60],
  activeLayerIds: ['vessels', 'berths', 'weather'],
  selectedEntityId: null,
  selectedEntityType: null,
  zoomLevel: 1,
  setCameraPosition: (pos) => set({ cameraPosition: pos }),
  toggleLayer: (layerId) =>
    set((state) => ({
      activeLayerIds: state.activeLayerIds.includes(layerId)
        ? state.activeLayerIds.filter((id) => id !== layerId)
        : [...state.activeLayerIds, layerId],
    })),
  selectEntity: (type, id) =>
    set({ selectedEntityType: type, selectedEntityId: id }),
  setZoomLevel: (level) => set({ zoomLevel: level }),
}));
