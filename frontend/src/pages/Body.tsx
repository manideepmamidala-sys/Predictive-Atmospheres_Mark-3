import { Link, useSearchParams } from 'react-router-dom';
import { useResearch } from '../lib/research';
import Catalogue from './Catalogue';
import Circumplex, { type AffectPoint } from '../figures/Circumplex';
import { Notice, PageHeading } from '../ui';

type Component = 'objective' | 'subjective' | 'fused';
const components: { id: Component; label: string; note: string }[] = [
  { id: 'objective', label: 'Physiology-derived', note: 'Candidate coordinates constructed from eligible EEG/ECG features.' },
  { id: 'subjective', label: 'Self-reported', note: 'Coordinates supplied by participants in the rated experiments.' },
  { id: 'fused', label: 'Fused', note: 'A weighted coordinate from eligible physiology and report components.' },
];

export default function Body() {
  const state = useResearch();
  const data = state.status === 'ready' ? state.data : null;
  const [params, setParams] = useSearchParams();
  const candidate = params.get('component');
  const component: Component = candidate === 'subjective' || candidate === 'fused' ? candidate : 'objective';
  const experiment = params.get('experiment') || 'all';
  const trials = data?.trials.filter(trial => experiment === 'all' || String(trial.experiment) === experiment) || [];
  const points: AffectPoint[] = trials.flatMap(trial => trial[component] ? [{ id: trial.id, label: `${trial.participant_id}, ${trial.room_id}`, position: trial[component]!, kind: component, cohort: trial.cohort }] : []);
  const update = (key: string, value: string) => setParams(previous => { const next = new URLSearchParams(previous); if (value === 'all') next.delete(key); else next.set(key, value); return next; });
  return <><PageHeading eyebrow="03 / Human metrics" title="Body & Experience" intro="How do quality-checked EEG and ECG features relate to what participants reported? Physiology leads this investigation; self-report and fused positions remain visible for comparison and disagreement." />
    <section className="body-intro"><div><p className="eyebrow">Three descriptions of experience</p><h2>Related, but not interchangeable</h2><p>Forehead signals and wrist ECG are processed into candidate features, then mapped into the valence–arousal plane under stated assumptions. Reports use participants' ratings. Fusion combines eligible positions with a documented weight. A shared display axis does not prove that the three descriptions measure the same construct.</p><Link to="/methods">Read the method and eligibility rules ↗</Link></div><div className="component-key">{components.map(item => <div key={item.id}><span className={`component-symbol ${item.id}`} aria-hidden="true" /><div><strong>{item.label}</strong><p>{item.note}</p></div></div>)}</div></section>
    <section className="body-plane"><div className="section-heading"><div><p className="eyebrow">Exported trial positions</p><h2>Valence × arousal</h2></div><Link to="/explore?view=trials">Inspect trial records ↗</Link></div><div className="toolbar"><label>Component<select value={component} onChange={event => update('component', event.target.value)}>{components.map(item => <option key={item.id} value={item.id}>{item.label}</option>)}</select></label><label>Experiment<select value={experiment} onChange={event => update('experiment', event.target.value)}><option value="all">All experiments</option><option value="1">Form · comfort only</option><option value="2">Lighting</option><option value="3">Function</option></select></label></div>{data ? <Circumplex points={points} caption={`${components.find(item => item.id === component)!.label} positions from the selected exported trials. Experiment 1 comfort remains separate and has no invented valence coordinate.`} /> : <Notice title="Positions unavailable" warning><p>{state.status === 'error' ? state.message : 'Loading the validated trial export.'}</p></Notice>}</section>
    <Catalogue ids={['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8']} title="Signal quality, components and agreement" />
  </>;
}
