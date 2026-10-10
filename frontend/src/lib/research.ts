import { useEffect, useState } from 'react';
import { z } from 'zod';

const finite = z.number().finite();
const position = z.object({ valence: finite, arousal: finite });
const provenance = z.object({ source: z.string(), method: z.string(), generated_at: z.string().nullable().optional(), limitations: z.array(z.string()).default([]) });
const experiment = z.object({ id: z.number().int(), trials: z.number().int().nonnegative(), participants: z.number().int().nonnegative(), rooms: z.number().int().nonnegative(), measured: z.array(z.string()).default([]) });
const room = z.object({ id: z.string(), experiment: z.number().int(), space_type: z.string().nullable().optional(), lighting: z.string().nullable().optional(), illuminance_lux: finite.nullable().optional(), cct_kelvin: finite.nullable().optional(), dimensions: z.record(finite.nullable()).default({}), independent_attributes: z.record(z.union([finite, z.string(), z.null()])).optional(), mean_affect: position.nullable().optional(), n_affect: z.number().int().nonnegative().nullable().optional() });
const trace = z.object({ sample_rate_hz: finite.nullable(), source_sample_rate_hz: finite.nullable().optional(), unit: z.string(), channel: z.string().nullable().optional(), window_start_s: finite.nonnegative().optional(), raw: z.array(finite).default([]), cleaned: z.array(finite).default([]), rejected_segments: z.array(z.tuple([finite, finite])).default([]) });
const qcDecision = z.object({ signal: z.string(), status: z.enum(['accept', 'reject', 'uncertain']), reason: z.string(), reviewer: z.string(), entry_id: z.string() });
const qcComponent = z.object({ automated_eligible: z.boolean(), automated_reasons: z.array(z.string()), reviewed_eligible: z.boolean(), review_decisions: z.array(qcDecision) });
const qcComponents = z.object({ timebase: qcComponent, eeg_right: qcComponent, eeg_left: qcComponent, eeg_bilateral: qcComponent, ecg_hr: qcComponent, ecg_rmssd: qcComponent });
const reviewedEligibility = z.object({ timebase: z.boolean(), eeg_right: z.boolean(), eeg_left: z.boolean(), eeg_bilateral: z.boolean(), ecg_hr: z.boolean(), ecg_rmssd: z.boolean() });
const trial = z.object({ id: z.string(), experiment: z.number().int(), participant_id: z.string(), room_id: z.string(), eeg_valid: z.boolean(), ecg_valid: z.boolean(), ecg_hr_valid: z.boolean(), ecg_rmssd_valid: z.boolean(), reviewed_eligibility: reviewedEligibility, qc_components: qcComponents, reasons: z.array(z.string()).default([]), eeg: trace.nullable().optional(), ecg: trace.nullable().optional(), eeg_band_power: z.record(finite.nullable()).nullable().optional(), faa: finite.nullable().optional(), heart_rate_bpm: finite.nullable().optional(), rmssd_ms: finite.nullable().optional(), subjective: position.nullable().optional(), objective: position.nullable().optional(), fused: position.nullable().optional(), alpha: finite.nullable().optional(), cohort: z.string().nullable().optional(), comfort: finite.nullable().optional(), eeg_reasons: z.array(z.string()).optional(), ecg_reasons: z.array(z.string()).optional(), rate_status: z.string().nullable().optional(), components: z.record(finite.nullable()).optional(), available_components: z.array(z.string()).optional(), axis_availability: z.record(z.boolean()).optional() }).superRefine((record, context) => {
  for (const key of reviewedEligibility.keyof().options) {
    if (record.reviewed_eligibility[key] !== record.qc_components[key].reviewed_eligible) context.addIssue({ code: z.ZodIssueCode.custom, message: `Reviewed ${key} status disagrees with QC provenance.` });
  }
  if (record.eeg_valid !== record.qc_components.eeg_bilateral.reviewed_eligible || record.ecg_hr_valid !== record.qc_components.ecg_hr.reviewed_eligible || record.ecg_rmssd_valid !== record.qc_components.ecg_rmssd.reviewed_eligible) context.addIssue({ code: z.ZodIssueCode.custom, message: 'Published component eligibility disagrees with QC provenance.' });
});
const sensitivity = z.object({ experiment: z.number().int().nullable().optional(), participant_id: z.string().nullable().optional(), alpha: finite, n: z.number().int().nonnegative(), mean_valence: finite.nullable(), mean_arousal: finite.nullable(), interval_valence: z.tuple([finite, finite]).nullable().optional(), interval_arousal: z.tuple([finite, finite]).nullable().optional() });
const disagreement = z.object({ experiment: z.number().int(), participant_id: z.string().nullable(), cohort: z.string(), axis: z.string(), n: z.number().int().nonnegative(), mean_objective_minus_subjective: finite.nullable() });
const personExperiment = z.object({ experiment: z.number().int(), trials: z.number().int().nonnegative(), valid_fused: z.number().int().nonnegative(), mean_valence: finite.nullable(), mean_arousal: finite.nullable(), sleep_hours: finite.nullable(), sleep_min_hours: finite.nullable(), sleep_max_hours: finite.nullable(), sleep_observations: z.number().int().nonnegative() });
const person = z.object({ id: z.string(), experiments: z.array(z.number().int()).default([]), trials: z.number().int().nonnegative(), valid_fused: z.number().int().nonnegative(), mean_valence: finite.nullable(), mean_arousal: finite.nullable(), age: finite.nullable().optional(), gender: z.string().nullable().optional(), sleep_hours: finite.nullable().optional(), by_experiment: z.array(personExperiment).default([]) });
const metric = z.object({ name: z.string(), value: finite.nullable(), unit: z.string().nullable().optional(), interval: z.tuple([finite, finite]).nullable().optional(), n: z.number().int().nonnegative().nullable().optional(), group: z.string().nullable().optional() });
const modelSummary = z.object({ cohort_trials: z.number().int().nonnegative(), cohort_participants: z.number().int().nonnegative(), cohort_rooms: z.number().int().nonnegative(), exclusions: z.record(z.number().int().nonnegative()), selection_status: z.string().nullable(), selected_candidate: z.record(z.union([z.string(), finite])).nullable(), preprocessing: z.array(z.string()), provenance: z.record(z.string()), participant_baseline_fallback: z.string(), evidence_links: z.record(z.string()) });
export const ResearchSchema = z.object({
  schema_version: z.literal('1.0.0'), provenance,
  study: z.object({ title: z.string(), abstract: z.string(), experiments: z.array(experiment), protocol: z.array(z.string()).default([]), limitations: z.array(z.string()).default([]) }),
  rooms: z.array(room), trials: z.array(trial), sensitivity: z.array(sensitivity), disagreement: z.array(disagreement).default([]), people: z.array(person),
  model: z.object({ status: z.string(), explanation: z.string(), metrics: z.array(metric), limitations: z.array(z.string()).default([]), artifact_version: z.string().nullable().optional(), summary: modelSummary.nullable().optional() }),
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

export const ANALYSIS_IDS = ['S1', 'S2', 'S3', 'S4', 'S5', 'R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8', 'R9', 'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'P1', 'P2', 'P3', 'P4', 'P5', 'Methods'] as const;
export type AnalysisId = typeof ANALYSIS_IDS[number];
const analysisId = z.enum(ANALYSIS_IDS);
const analysisStatus = z.enum(['available', 'unavailable']);
const chartValue = z.union([z.string(), finite, z.boolean(), z.null()]);
const methodsEvidence = z.object({
  settings: z.array(z.object({ category: z.string().min(1), label: z.string().min(1), value: z.union([z.string(), finite, z.boolean()]), unit: z.string().nullable(), source: z.string().min(1) })).min(1),
  review: z.object({ verdict: z.string().min(1), reviewed_at_utc: z.string().min(1), reviewers: z.array(z.string()), decision_counts: z.record(z.number().int().nonnegative()), reviewed_eligibility_counts: z.record(z.number().int().nonnegative()), ledger_path: z.string().min(1) }),
  sensitivity: z.array(z.object({ experiment: z.number().int(), alpha: finite, n: z.number().int().nonnegative(), mean_valence: finite.nullable(), mean_arousal: finite.nullable() })).min(1),
  references: z.array(z.object({ label: z.string().min(1), path: z.string().min(1) })).min(1),
});
export const AnalysisProductSchema = z.object({
  schema_version: z.literal('1.0.0'), id: analysisId, route: z.string().startsWith('/'), status: analysisStatus,
  question: z.string().min(1), takeaway: z.string().min(1), method: z.string().min(1), caveats: z.array(z.string()),
  counts: z.object({ trials: z.number().int().nonnegative(), participants: z.number().int().nonnegative(), rooms: z.number().int().nonnegative() }),
  units: z.record(z.string()),
  provenance: z.object({ method_version: z.literal('1.2.0'), approved_spec_sha256: z.string().regex(/^[0-9a-f]{64}$/), source_manifest_sha256: z.string().regex(/^[0-9a-f]{64}$/), generated_at_utc: z.string().min(1) }),
  availability_reason: z.string().nullable(),
  methods_evidence: methodsEvidence.optional(),
  chart: z.object({ type: z.enum(['line', 'bar', 'scatter', 'heatmap', 'table']), rows: z.array(z.record(chartValue)), x: z.string(), y: z.string(), series: z.string().nullish(), facet: z.string().nullish(), x_label: z.string(), y_label: z.string(), x_unit: z.string().nullish(), y_unit: z.string().nullish() }),
}).superRefine((product, context) => {
  if (product.id === 'Methods' && product.status === 'available' && !product.methods_evidence) context.addIssue({ code: z.ZodIssueCode.custom, message: 'Available Methods product needs approved method evidence.' });
  if (product.status === 'unavailable' && !product.availability_reason) context.addIssue({ code: z.ZodIssueCode.custom, message: 'Unavailable product needs a reason.' });
  if (product.status === 'available' && product.chart.rows.some(row => !(product.chart.x in row) || !(product.chart.y in row))) context.addIssue({ code: z.ZodIssueCode.custom, message: 'Chart rows must contain the declared encodings.' });
});
export const AnalysisIndexSchema = z.object({
  schema_version: z.literal('1.0.0'), method_version: z.literal('1.2.0'), approved_spec_sha256: z.string().regex(/^[0-9a-f]{64}$/),
  products: z.array(z.object({ id: analysisId, route: z.string().startsWith('/'), status: analysisStatus, path: z.string().regex(/^\/research\/analysis\/(?:S[1-5]|R[1-9]|B[1-8]|P[1-5]|Methods)\.json$/) })),
}).superRefine((index, context) => {
  const ids = index.products.map(product => product.id);
  if (ids.length !== ANALYSIS_IDS.length || new Set(ids).size !== ANALYSIS_IDS.length || ANALYSIS_IDS.some(id => !ids.includes(id))) context.addIssue({ code: z.ZodIssueCode.custom, message: 'Analysis index must enumerate every catalogue ID exactly once.' });
  if (index.products.some(product => product.path !== `/research/analysis/${product.id}.json`)) context.addIssue({ code: z.ZodIssueCode.custom, message: 'Analysis paths must match catalogue IDs.' });
});
export type AnalysisProduct = z.infer<typeof AnalysisProductSchema>;
export type AnalysisIndex = z.infer<typeof AnalysisIndexSchema>;
const analysisProducts = new Map<AnalysisId, AnalysisProduct>();
let analysisIndex: AnalysisIndex | null = null;
let indexPending: Promise<AnalysisIndex> | null = null;
async function fetchJson(path: string): Promise<unknown> {
  const response = await fetch(path, { cache: 'no-cache' });
  if (!response.ok) throw new Error(`Analysis export unavailable (HTTP ${response.status}).`);
  if (!response.headers.get('content-type')?.includes('application/json')) throw new Error('Analysis export is not published as JSON.');
  return response.json();
}
export async function loadAnalysisIndex(): Promise<AnalysisIndex> {
  if (analysisIndex) return analysisIndex;
  indexPending ??= fetchJson('/research/analysis/index.json').then(value => {
    const parsed = AnalysisIndexSchema.safeParse(value);
    if (!parsed.success) throw new Error('Analysis catalogue index failed validation.');
    analysisIndex = parsed.data;
    return parsed.data;
  }).finally(() => { indexPending = null; });
  return indexPending;
}
export async function loadAnalysisProduct(id: AnalysisId): Promise<AnalysisProduct> {
  const cached = analysisProducts.get(id);
  if (cached) return cached;
  const index = await loadAnalysisIndex();
  const entry = index.products.find(product => product.id === id);
  if (!entry) throw new Error(`Catalogue product ${id} is missing from the index.`);
  const parsed = AnalysisProductSchema.safeParse(await fetchJson(entry.path));
  if (!parsed.success) throw new Error(`Catalogue product ${id} failed validation.`);
  const product = parsed.data;
  if (product.id !== id || product.route !== entry.route || product.status !== entry.status || product.provenance.approved_spec_sha256 !== index.approved_spec_sha256) throw new Error(`Catalogue product ${id} disagrees with its index.`);
  analysisProducts.set(id, product);
  return product;
}
type AnalysisState = { status: 'loading'; products: AnalysisProduct[]; completed: number; total: number } | { status: 'ready'; products: AnalysisProduct[]; completed: number; total: number } | { status: 'error'; message: string; products: AnalysisProduct[]; completed: number; total: number };
export function useAnalysisProducts(ids: readonly AnalysisId[]): AnalysisState {
  const key = ids.join(',');
  const [state, setState] = useState<AnalysisState>({ status: 'loading', products: [], completed: 0, total: ids.length });
  useEffect(() => {
    let alive = true;
    const selected = key.split(',').filter(Boolean) as AnalysisId[];
    const products: AnalysisProduct[] = [];
    let completed = 0;
    setState({ status: 'loading', products: [], completed: 0, total: selected.length });
    const errors: string[] = [];
    Promise.allSettled(selected.map(async id => {
      try { products.push(await loadAnalysisProduct(id)); }
      catch (error) { errors.push(`${id}: ${String(error instanceof Error ? error.message : error)}`); }
      completed += 1;
      if (alive) setState({ status: 'loading', products: [...products].sort((a, b) => selected.indexOf(a.id) - selected.indexOf(b.id)), completed, total: selected.length });
    })).then(() => {
      if (!alive) return;
      const ordered = selected.flatMap(id => products.filter(product => product.id === id));
      setState(errors.length ? { status: 'error', message: errors.join(' '), products: ordered, completed, total: selected.length } : { status: 'ready', products: ordered, completed, total: selected.length });
    });
    return () => { alive = false; };
  }, [key]);
  return state;
}
