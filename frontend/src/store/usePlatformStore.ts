import { create } from 'zustand';

interface SpatialState {
  // Inputs
  length_m: number;
  width_m: number;
  height_m: number;
  num_doors: number;
  door_area_m2: number;
  num_windows: number;
  window_area_m2: number;
  daylight_factor_pct: number;
  illuminance_lux: number;
  cct_k: number;
  walkable_floor_area_m2: number;
  room_volume_m3: number;
  space_use_type: string;
  
  // Outputs
  predicted_neuro_score: number | null;
  predicted_valence: number | null;
  predicted_arousal: number | null;
  confidence_pct: number | null;
  atmospheric_label: string | null;
  
  // Status
  isPredicting: boolean;
  error500: string | null;
  error422: string | null;
  
  // Actions
  setField: (field: keyof SpatialState, value: any) => void;
  fetchPrediction: () => Promise<void>;
  fetchInverseOptimization: (targetNeuroScore: number) => Promise<void>;
}

// Keep track of timeout for debounce
let debounceTimer: ReturnType<typeof setTimeout> | null = null;

export const usePlatformStore = create<SpatialState>((set, get) => ({
  length_m: 10.0,
  width_m: 8.0,
  height_m: 3.5,
  num_doors: 1,
  door_area_m2: 2.1,
  num_windows: 2,
  window_area_m2: 4.0,
  daylight_factor_pct: 2.0,
  illuminance_lux: 300,
  cct_k: 4000,
  walkable_floor_area_m2: 60.0,
  room_volume_m3: 280.0,
  space_use_type: 'Workplace',
  
  predicted_neuro_score: null,
  predicted_valence: null,
  predicted_arousal: null,
  confidence_pct: null,
  atmospheric_label: null,
  
  isPredicting: false,
  error500: null,
  error422: null,
  
  setField: (field, value) => {
    set({ [field]: value });
    
    // Auto-trigger prediction on input change, with debounce
    if (debounceTimer) clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
      get().fetchPrediction();
    }, 150);
  },
  
  fetchPrediction: async () => {
    const state = get();
    set({ isPredicting: true, error500: null, error422: null });
    
    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          length_m: state.length_m,
          width_m: state.width_m,
          height_m: state.height_m,
          num_doors: state.num_doors,
          door_area_m2: state.door_area_m2,
          num_windows: state.num_windows,
          window_area_m2: state.window_area_m2,
          daylight_factor_pct: state.daylight_factor_pct,
          illuminance_lux: state.illuminance_lux,
          cct_k: state.cct_k,
          walkable_floor_area_m2: state.walkable_floor_area_m2,
          room_volume_m3: state.room_volume_m3,
          space_use_type: state.space_use_type
        })
      });
      
      if (response.status === 422) {
        set({ error422: 'Validation error: Please ensure all inputs are valid numbers.' });
        return;
      }
      
      if (!response.ok) {
        throw new Error(`Server returned ${response.status}`);
      }
      
      const data = await response.json();
      set({
        predicted_neuro_score: data.neuro_score,
        predicted_valence: data.valence,
        predicted_arousal: data.arousal,
        confidence_pct: data.confidence_pct,
        atmospheric_label: data.atmospheric_label
      });
      
    } catch (err: any) {
      set({ error500: err.message || 'An unknown error occurred during prediction.' });
    } finally {
      set({ isPredicting: false });
    }
  },
  
  fetchInverseOptimization: async (targetNeuroScore: number) => {
    set({ isPredicting: true, error500: null, error422: null });
    
    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/inverse-optimize`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ target_neuro_score: targetNeuroScore })
      });
      
      if (!response.ok) {
        throw new Error(`Server returned ${response.status}`);
      }
      
      const data = await response.json();
      set({
        length_m: data.length,
        width_m: data.width,
        height_m: data.height,
        predicted_neuro_score: data.neuro_score,
        predicted_valence: data.predicted_valence,
        predicted_arousal: data.predicted_arousal
      });
      
    } catch (err: any) {
      set({ error500: err.message || 'Optimization failed.' });
    } finally {
      set({ isPredicting: false });
    }
  }
}));
