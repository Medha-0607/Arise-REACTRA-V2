import { create } from 'zustand';
import { HealthResponse } from '../types/api';
import { apiClient } from '../services/apiClient';

interface AppState {
  health: HealthResponse | null;
  isLoading: boolean;
  error: string | null;
  fetchHealth: () => Promise<void>;
}

export const useAppStore = create<AppState>((set) => ({
  health: null,
  isLoading: false,
  error: null,
  fetchHealth: async () => {
    set({ isLoading: true, error: null });
    try {
      const health = await apiClient.getHealth();
      set({ health, isLoading: false });
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to reach API';
      set({ error: message, isLoading: false });
    }
  },
}));
