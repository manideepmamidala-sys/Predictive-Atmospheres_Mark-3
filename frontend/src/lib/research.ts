import { useEffect, useState } from 'react';
import { z } from 'zod';

const finite = z.number().finite();
const position = z.object({ valence: finite, arousal: finite });
const provenance = z.object({ source: z.string(), method: z.string(), generated_at: z.string().nullable().optional(), limitations: z.array(z.string()).default([]) });
const experiment = z.object({ id: z.number().int(), trials: z.number().int().nonnegative(), participants: z.number().int().nonnegative(), rooms: z.number().int().nonnegative(), measured: z.array(z.string()).default([]) });
const room = z.object({ id: z.string(), experiment: z.number().int(), space_type: z.string().nullable().optional(), lighting: z.string().nullable().optional(), illuminance_lux: finite.nullable().optional(), cct_kelvin: finite.nullable().optional(), dimensions: z.record(finite.nullable()).default({}), mean_affect: position.nullable().optional(), n_affect: z.number().int().nonnegative().nullable().optional() });
const trace = z.object({ sample_rate_hz: finite.nullable(), source_sample_rate_hz: finite.nullable().optional(), unit: z.string(), channel: z.string().nullable().optional(), window_start_s: finite.nonnegative().optional(), raw: z.array(finite).default([]), cleaned: z.array(finite).default([]), rejected_segments: z.array(z.tuple([finite, finite])).default([]) });
const trial = z.object({ id: z.string(), experiment: z.number().int(), participant_id: z.string(), room_id: z.string(), eeg_valid: z.boolean(), ecg_valid: z.boolean(), reasons: z.array(z.string()).default([]), eeg: trace.nullable().optional(), ecg: trace.nullable().optional(), eeg_band_power: z.record(finite.nullable()).nullable().optional(), faa: finite.nullable().optional(), heart_rate_bpm: finite.nullable().optional(), rmssd_ms: finite.nullable().optional(), subjective: position.nullable().optional(), objective: position.nullable().optional(), fused: position.nullable().optional(), alpha: finite.nullable().optional(), cohort: z.string().nullable().optional(), comfort: finite.nullable().optional(), eeg_reasons: z.array(z.string()).optional(), ecg_reasons: z.array(z.string()).optional(), rate_status: z.string().nullable().optional(), components: z.record(finite.nullable()).optional(), available_components: z.array(z.string()).optional(), axis_availability: z.record(z.boolean()).optional() });
const sensitivity = z.object({ experiment: z.number().int().nullable().optional(), alpha: finite, n: z.number().int().nonnegative(), mean_valence: finite.nullable(), mean_arousal: finite.nullable(), interval_valence: z.tuple([finite, finite]).nullable().optional(), interval_arousal: z.tuple([finite, finite]).nullable().optional() });
const person = z.object({ id: z.string(), experiments: z.array(z.number().int()).default([]), trials: z.number().int().nonnegative(), valid_fused: z.number().int().nonnegative(), mean_valence: finite.nullable(), mean_arousal: finite.nullable(), age: finite.nullable().optional(), gender: z.string().nullable().optional(), sleep_hours: finite.nullable().optional() });
const metric = z.object({ name: z.string(), value: finite.nullable(), unit: z.string().nullable().optional(), interval: z.tuple([finite, finite]).nullable().optional(), n: z.number().int().nonnegative().nullable().optional(), group: z.string().nullable().optional() });
export const ResearchSchema = z.object({
  schema_version: z.literal('1.0.0'), provenance,
  study: z.object({ title: z.string(), abstract: z.string(), experiments: z.array(experiment), protocol: z.array(z.string()).default([]), limitations: z.array(z.string()).default([]) }),
  rooms: z.array(room), trials: z.array(trial), sensitivity: z.array(sensitivity), people: z.array(person),
  model: z.object({ status: z.string(), explanation: z.string(), metrics: z.array(metric), limitations: z.array(z.string()).default([]), artifact_version: z.string().nullable().optional() }),
});
const SignalsSchema = z.object({ schema_version: z.literal('1.0.0'), provenance, trials: z.array(trial) });
export type Research = z.infer<typeof ResearchSchema>;
export type Room = Research['rooms'][number];
export type Trial = Research['trials'][number];
export type Position = z.infer<typeof position>;
type State = { status: 'loading' } | { status: 'error'; message: string } | { status: 'ready'; data: Research };
let cache: Research | null = null;
let pending: Promise<Research> | null = null;
let signalCache: z.infer<typeof SignalsSchema> | null = null;
let signalPending: Promise<z.infer<typeof SignalsSchema>> | null = null;
export async function loadResearch(): Promise<Research> {
  if (cache) return cache;
  pending ??= fetch('/research/bundle.json', { cache: 'no-cache' }).then(async response => {
    if (!response.ok) throw new Error(`Research export is not available yet (HTTP ${response.status}).`);
    if (!response.headers.get('content-type')?.includes('application/json')) throw new Error('Validated research results are not published yet.');
    const parsed = ResearchSchema.safeParse(await response.json());
    if (!parsed.success) {
      console.error('Research export schema validation failed', parsed.error.issues);
      throw new Error('The research export could not be validated. Please check the published results.');
    }
    cache = parsed.data; return cache;
  }).finally(() => { pending = null; });
  return pending;
}
export function useResearch(): State {
  const [state, setState] = useState<State>(cache ? { status: 'ready', data: cache } : { status: 'loading' });
  useEffect(() => { let alive = true; loadResearch().then(data => { if (alive) setState({ status: 'ready', data }); }).catch(error => { if (alive) setState({ status: 'error', message: String(error.message || error) }); }); return () => { alive = false; }; }, []);
  return state;
}
async function loadSignalProduct(): Promise<z.infer<typeof SignalsSchema>> {
  if (signalCache) return signalCache;
  signalPending ??= fetch('/research/signals.json', { cache: 'no-cache' }).then(async response => {
    if (!response.ok) throw new Error(`Signal traces are unavailable (HTTP ${response.status}).`);
    if (!response.headers.get('content-type')?.includes('application/json')) throw new Error('Signal traces are not published yet.');
    const parsed = SignalsSchema.safeParse(await response.json());
    if (!parsed.success) {
      console.error('Signal export schema validation failed', parsed.error.issues);
      throw new Error('The signal export could not be validated.');
    }
    signalCache = parsed.data;
    return signalCache;
  }).finally(() => { signalPending = null; });
  return signalPending;
}
type SignalState = { status: 'loading' } | { status: 'error'; message: string } | { status: 'ready'; trials: Trial[] };
export function useSignalTrials(base: Research | null): SignalState {
  const [state, setState] = useState<SignalState>({ status: 'loading' });
  useEffect(() => {
    if (!base) return;
    let alive = true;
    loadSignalProduct().then(product => {
      const byId = new Map(product.trials.map(record => [record.id, record]));
      if (byId.size !== base.trials.length || product.trials.length !== base.trials.length || base.trials.some(record => !byId.has(record.id))) {
        throw new Error('Signal trials do not match the published research bundle.');
      }
      const trials = base.trials.map(record => ({ ...record, eeg: byId.get(record.id)!.eeg, ecg: byId.get(record.id)!.ecg }));
      if (alive) setState({ status: 'ready', trials });
    }).catch(error => { if (alive) setState({ status: 'error', message: String(error.message || error) }); });
    return () => { alive = false; };
  }, [base]);
  return state;
}
export const researchSource = (data: Research) => `Source: ${data.provenance.source}. Method: ${data.provenance.method}.`;
