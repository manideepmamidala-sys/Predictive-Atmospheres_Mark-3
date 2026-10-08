import type { Page } from '@playwright/test';
import type { Research } from '../src/lib/research';

/** Synthetic records for browser behavior tests only. Never copied into public/research. */
export const SYNTHETIC_RESEARCH: Research = {
  schema_version: '1.0.0',
  provenance: { source: 'SYNTHETIC TEST FIXTURE', method: 'Hand-authored browser interaction cases', generated_at: null, limitations: ['Not a research result'] },
  study: {
    title: 'Synthetic test study', abstract: 'Only used by Playwright tests.',
    experiments: [
      { id: 1, trials: 1, participants: 1, rooms: 1, measured: ['comfort'] },
      { id: 2, trials: 1, participants: 1, rooms: 1, measured: ['EEG', 'ECG', 'self-report'] },
      { id: 3, trials: 1, participants: 1, rooms: 1, measured: ['EEG', 'ECG', 'self-report', 'sleep'] },
    ],
    protocol: ['Viewed a room render', 'Provided a rating where collected'],
    limitations: ['Synthetic browser cases do not represent participants.'],
  },
  rooms: [
    { id: 'Rm_001', experiment: 1, space_type: null, lighting: null, illuminance_lux: null, cct_kelvin: null, dimensions: { length: 5, width: 4, height: 3 }, mean_affect: null, n_affect: null },
    { id: 'Rm_011', experiment: 2, space_type: null, lighting: 'Day', illuminance_lux: 200, cct_kelvin: 3000, dimensions: { length: 6, width: 5, height: 3 }, mean_affect: { valence: 0.2, arousal: 0.1 }, n_affect: 1 },
    { id: 'Rm_021', experiment: 3, space_type: 'Bedroom', lighting: 'Day', illuminance_lux: null, cct_kelvin: null, dimensions: { length: 7, width: 6, height: 3 }, mean_affect: null, n_affect: 0 },
  ],
  trials: [
    { id: 'synthetic-1', experiment: 1, participant_id: 'P01', room_id: 'Rm_001', eeg_valid: false, ecg_valid: false, reasons: ['No usable signal'], eeg: null, ecg: null, eeg_band_power: null, faa: null, heart_rate_bpm: null, rmssd_ms: null, subjective: null, objective: null, fused: null, alpha: null, cohort: 'comfort_only', comfort: 0.1, available_components: [], axis_availability: { valence: false, arousal: false } },
    { id: 'synthetic-2', experiment: 2, participant_id: 'P01', room_id: 'Rm_011', eeg_valid: true, ecg_valid: true, reasons: [], eeg: { sample_rate_hz: 4, unit: 'µV', channel: 'Fp1', window_start_s: 2, raw: [1, 2, 1, 0], cleaned: [0, 1, 0, -1], rejected_segments: [[2.25, 2.5]] }, ecg: { sample_rate_hz: 4, unit: 'mV', channel: 'wrist', window_start_s: 2, raw: [0, 1, 0, -1], cleaned: [0, 0.8, 0, -0.8], rejected_segments: [] }, eeg_band_power: { alpha: 0.4 }, faa: 0.12, heart_rate_bpm: 70, rmssd_ms: 22, subjective: { valence: 0.4, arousal: 0.2 }, objective: { valence: 0, arousal: 0 }, fused: { valence: 0.2, arousal: 0.1 }, alpha: 0.5, cohort: 'complete_fusion', comfort: null, available_components: ['faa', 'beta_alpha', 'heart_rate_bpm', 'rmssd_ms'], axis_availability: { valence: true, arousal: true } },
    { id: 'synthetic-3', experiment: 3, participant_id: 'P02', room_id: 'Rm_021', eeg_valid: true, ecg_valid: false, reasons: ['ECG peaks absent'], eeg: { sample_rate_hz: 4, unit: 'µV', channel: 'Fp1', window_start_s: 0, raw: [0, 1, 0, -1], cleaned: [], rejected_segments: [[0.5, 1]] }, ecg: null, eeg_band_power: null, faa: null, heart_rate_bpm: null, rmssd_ms: null, subjective: null, objective: null, fused: null, alpha: null, cohort: 'objective_only', comfort: null, available_components: ['eeg'], axis_availability: { valence: false, arousal: false } },
  ],
  sensitivity: [
    { experiment: 2, alpha: 0, n: 1, mean_valence: 0, mean_arousal: 0, interval_valence: null, interval_arousal: null },
    { experiment: 2, alpha: 0.5, n: 1, mean_valence: 0.2, mean_arousal: 0.1, interval_valence: null, interval_arousal: null },
    { experiment: 3, alpha: 0.5, n: 0, mean_valence: null, mean_arousal: null, interval_valence: null, interval_arousal: null },
  ],
  people: [
    { id: 'P01', experiments: [1, 2], trials: 2, valid_fused: 1, mean_valence: 0.2, mean_arousal: 0.1, age: null, gender: null, sleep_hours: null },
    { id: 'P02', experiments: [3], trials: 1, valid_fused: 0, mean_valence: null, mean_arousal: null, age: null, gender: null, sleep_hours: 7 },
  ],
  model: { status: 'weak', explanation: 'Synthetic weak-model status for browser testing.', metrics: [{ name: 'Room holdout MAE', value: null, unit: null, interval: null, n: 0, group: 'room-held-out' }], limitations: ['No validated prediction from synthetic records.'], artifact_version: null },
};

export async function useSyntheticResearch(page: Page, data: Research = SYNTHETIC_RESEARCH) {
  await page.route('**/research/bundle.json', route => route.fulfill({ json: { ...data, trials: data.trials.map(trial => ({ ...trial, eeg: null, ecg: null })) } }));
  await page.route('**/research/signals.json', route => route.fulfill({ json: { schema_version: data.schema_version, provenance: data.provenance, trials: data.trials } }));
}
