import type { Page } from '@playwright/test';
import type { Research, AnalysisIndex, AnalysisProduct, AnalysisId } from '../src/lib/research';
import { ANALYSIS_IDS } from '../src/lib/research';

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
    { id: 'Rm_021', experiment: 3, space_type: 'Bedroom', lighting: 'Day', illuminance_lux: 210, cct_kelvin: 3300, dimensions: { length: 7, width: 6, height: 3 }, independent_attributes: { length: 7, width: 6, height: 3, num_doors: 1, door_area: 2, num_windows: 2, window_area: 4, daylight_factor: 3, illuminance: 210, cct: 3300, walkable_floor_area: 38, day_or_night: 'Day', space_type: 'Bedroom' }, mean_affect: null, n_affect: 0 },
  ],
  trials: [
    { id: 'synthetic-1', experiment: 1, participant_id: 'P01', room_id: 'Rm_001', eeg_valid: false, ecg_valid: false, reasons: ['No usable signal'], eeg: null, ecg: null, eeg_band_power: null, faa: null, heart_rate_bpm: null, rmssd_ms: null, subjective: null, objective: null, fused: null, alpha: null, cohort: 'comfort_only', comfort: 0.1, available_components: [], axis_availability: { valence: false, arousal: false } },
    { id: 'synthetic-2', experiment: 2, participant_id: 'P01', room_id: 'Rm_011', eeg_valid: true, ecg_valid: true, reasons: [], eeg: { sample_rate_hz: 4, unit: 'µV', channel: 'Fp1', window_start_s: 2, raw: [1, 2, 1, 0], cleaned: [0, 1, 0, -1], rejected_segments: [[2.25, 2.5]] }, ecg: { sample_rate_hz: 4, unit: 'mV', channel: 'wrist', window_start_s: 2, raw: [0, 1, 0, -1], cleaned: [0, 0.8, 0, -0.8], rejected_segments: [] }, eeg_band_power: { alpha: 0.4 }, faa: 0.12, heart_rate_bpm: 70, rmssd_ms: 22, subjective: { valence: 0.4, arousal: 0.2 }, objective: { valence: 0, arousal: 0 }, fused: { valence: 0.2, arousal: 0.1 }, alpha: 0.5, cohort: 'complete_fusion', comfort: null, available_components: ['faa', 'beta_alpha', 'heart_rate_bpm', 'rmssd_ms'], axis_availability: { valence: true, arousal: true } },
    { id: 'synthetic-3', experiment: 3, participant_id: 'P02', room_id: 'Rm_021', eeg_valid: true, ecg_valid: false, reasons: ['ECG peaks absent'], eeg: { sample_rate_hz: 4, unit: 'µV', channel: 'Fp1', window_start_s: 0, raw: [0, 1, 0, -1], cleaned: [], rejected_segments: [[0.5, 1]] }, ecg: null, eeg_band_power: null, faa: null, heart_rate_bpm: null, rmssd_ms: null, subjective: null, objective: null, fused: null, alpha: null, cohort: 'objective_only', comfort: null, available_components: ['eeg'], axis_availability: { valence: false, arousal: false } },
  ],
  sensitivity: [
    { experiment: 2, participant_id: null, alpha: 0, n: 1, mean_valence: 0, mean_arousal: 0, interval_valence: null, interval_arousal: null },
    { experiment: 2, participant_id: null, alpha: 0.5, n: 1, mean_valence: 0.2, mean_arousal: 0.1, interval_valence: null, interval_arousal: null },
    { experiment: 2, participant_id: 'P01', alpha: 0.5, n: 1, mean_valence: 0.2, mean_arousal: 0.1, interval_valence: null, interval_arousal: null },
    { experiment: 3, participant_id: null, alpha: 0.5, n: 0, mean_valence: null, mean_arousal: null, interval_valence: null, interval_arousal: null },
  ],
  disagreement: [
    { experiment: 2, participant_id: null, cohort: 'complete_fusion', axis: 'valence', n: 1, mean_objective_minus_subjective: -0.4 },
    { experiment: 2, participant_id: 'P01', cohort: 'complete_fusion', axis: 'valence', n: 1, mean_objective_minus_subjective: -0.4 },
  ],
  people: [
    { id: 'P01', experiments: [1, 2], trials: 2, valid_fused: 1, mean_valence: 0.2, mean_arousal: 0.1, age: 26, gender: 'Female', sleep_hours: null, by_experiment: [
      { experiment: 1, trials: 1, valid_fused: 0, mean_valence: null, mean_arousal: null, sleep_hours: null, sleep_min_hours: null, sleep_max_hours: null, sleep_observations: 0 },
      { experiment: 2, trials: 1, valid_fused: 1, mean_valence: 0.2, mean_arousal: 0.1, sleep_hours: null, sleep_min_hours: null, sleep_max_hours: null, sleep_observations: 0 },
    ] },
    { id: 'P02', experiments: [3], trials: 1, valid_fused: 0, mean_valence: null, mean_arousal: null, age: 29, gender: 'Male', sleep_hours: null, by_experiment: [
      { experiment: 3, trials: 1, valid_fused: 0, mean_valence: null, mean_arousal: null, sleep_hours: 7, sleep_min_hours: 7, sleep_max_hours: 7, sleep_observations: 1 },
    ] },
  ],
  model: { status: 'weak', explanation: 'Synthetic weak-model status for browser testing.', metrics: [{ name: 'Room holdout MAE', value: null, unit: null, interval: null, n: 0, group: 'room-held-out' }], limitations: ['No validated prediction from synthetic records.'], artifact_version: null, summary: { cohort_trials: 1, cohort_participants: 1, cohort_rooms: 1, exclusions: { missing_features: 2 }, selection_status: 'synthetic_only', selected_candidate: { name: 'fixture' }, preprocessing: ['Synthetic test-only step'], provenance: { code_tree_sha256: 'synthetic-test-hash' }, participant_baseline_fallback: 'Synthetic fixture fallback; not a research finding.', evidence_links: { model_card: 'docs/model_card.md' } } },
};

export async function useSyntheticResearch(page: Page, data: Research = SYNTHETIC_RESEARCH) {
  await page.route('**/research/bundle.json', route => route.fulfill({ json: { ...data, trials: data.trials.map(trial => ({ ...trial, eeg: null, ecg: null })) } }));
  await page.route('**/research/signals.json', route => route.fulfill({ json: { schema_version: data.schema_version, provenance: data.provenance, trials: data.trials } }));
}

const SPEC_HASH = 'a'.repeat(64);
const SOURCE_HASH = 'b'.repeat(64);
export const SYNTHETIC_ANALYSIS_INDEX: AnalysisIndex = {
  schema_version: '1.0.0', method_version: '1.2.0', approved_spec_sha256: SPEC_HASH,
  products: ANALYSIS_IDS.map(id => ({ id, route: id === 'Methods' ? '/methods' : id === 'S4' || id.startsWith('R') ? '/rooms' : id.startsWith('S') ? '/study' : id.startsWith('B') ? '/body' : '/prediction', status: 'available' as const, path: `/research/analysis/${id}.json` })),
};
export function syntheticProduct(id: AnalysisId): AnalysisProduct {
  const entry = SYNTHETIC_ANALYSIS_INDEX.products.find(product => product.id === id)!;
  return {
    schema_version: '1.0.0', id, route: entry.route, status: 'available', question: `Synthetic ${id} question`, takeaway: 'Synthetic chart fixture; not a research result.', method: 'Browser interaction fixture', caveats: ['Synthetic values are never published.'],
    counts: { trials: 2, participants: 1, rooms: 2 }, units: { x_value: 'unit', y_value: 'unit' },
    provenance: { method_version: '1.2.0', approved_spec_sha256: SPEC_HASH, source_manifest_sha256: SOURCE_HASH, generated_at_utc: '2026-10-10T00:00:00Z' },
    availability_reason: null,
    chart: { type: 'scatter', rows: [{ x_value: -1, y_value: -1, group: 'A' }, { x_value: 1, y_value: 1, group: 'B' }], x: 'x_value', y: 'y_value', x_label: 'Synthetic x', y_label: 'Synthetic y', x_unit: 'unit', y_unit: 'unit' },
  };
}
export async function useSyntheticAnalysis(page: Page) {
  await page.route('**/research/analysis/*.json', route => {
    const id = route.request().url().split('/').pop()?.replace('.json', '') as AnalysisId;
    return route.fulfill({ json: syntheticProduct(id) });
  });
  await page.route('**/research/analysis/index.json', route => route.fulfill({ json: SYNTHETIC_ANALYSIS_INDEX }));
}
