import { useState } from 'react';
import { useResearch } from '../lib/research';
import Circumplex, { type AffectPoint } from '../figures/Circumplex';
import Sensitivity from '../figures/Sensitivity';
import { Notice, PageHeading, Section, Value } from '../ui';

export default function Affect() {
  const state = useResearch();
  const data = state.status === 'ready' ? state.data : null;
  const [experiment, setExperiment] = useState('all');
  const [person, setPerson] = useState('all');
  const [component, setComponent] = useState<'subjective' | 'objective' | 'fused'>('fused');
  const [alpha, setAlpha] = useState('all');

  const inExperiment = (value: number) => experiment === 'all' || String(value) === experiment;
  const inPerson = (value: string | null | undefined) => person === 'all' ? value == null : value === person;
  const trials = data?.trials.filter(row => inExperiment(row.experiment) && (person === 'all' || row.participant_id === person)) || [];
  const complete = trials.filter(trial => trial.cohort === 'complete_fusion' && trial.fused);
  const partial = trials.filter(trial => trial.cohort === 'partial_modality_fusion' && trial.fused);
  const comfort = trials.filter(trial => trial.experiment === 1 && trial.comfort != null);
  const points: AffectPoint[] = trials.flatMap(trial => {
    const position = trial[component];
    return position ? [{ id: trial.id, label: `${trial.participant_id}, ${trial.room_id}`, position, kind: component, cohort: trial.cohort, cct: data?.rooms.find(room => room.id === trial.room_id)?.cct_kelvin }] : [];
  });
  const people = [...new Set(data?.trials.map(trial => trial.participant_id) || [])].sort();
  const alphaValues = [...new Set(data?.sensitivity.map(row => row.alpha) || [])].sort((a, b) => a - b);
  const sensitivity = data?.sensitivity.filter(row => inExperiment(row.experiment ?? -1) && inPerson(row.participant_id) && (alpha === 'all' || String(row.alpha) === alpha)) || [];
  const disagreement = data?.disagreement.filter(row => inExperiment(row.experiment) && inPerson(row.participant_id)) || [];

  return <><PageHeading eyebrow="Descriptive synthesis" title="Affect" intro="Compare reported, physiology-mapped and fused positions without treating their shared axes as proof that they measure the same construct. Experiment 1 comfort remains separate." />
    {!data ? <Notice title="Affect export unavailable" warning><p>{state.status === 'error' ? state.message : 'Loading validated positions.'}</p></Notice> : <>
      <div className="toolbar">
        <label>Experiment<select value={experiment} onChange={event => setExperiment(event.target.value)}><option value="all">All experiments</option>{data.study.experiments.map(item => <option key={item.id} value={item.id}>Experiment {item.id}</option>)}</select></label>
        <label>Participant<select value={person} onChange={event => setPerson(event.target.value)}><option value="all">All participant IDs</option>{people.map(item => <option key={item}>{item}</option>)}</select></label>
        <label>Component<select value={component} onChange={event => setComponent(event.target.value as typeof component)}><option value="fused">Fused</option><option value="subjective">Self-report</option><option value="objective">Physiology mapped</option></select></label>
        <label>Sensitivity α<select value={alpha} onChange={event => setAlpha(event.target.value)}><option value="all">All exported weights</option>{alphaValues.map(value => <option key={value} value={value}>{value}</option>)}</select></label>
        <span className="status">{component === 'fused' ? `${complete.length} complete + ${partial.length} partial-modality fused positions` : `${points.length} ${component} positions`} from {trials.length} {trials.length === 1 ? 'trial' : 'trials'}</span>
      </div>
      <div className="page-grid"><div className="reading">
        <Section title="What is combined"><p>The subjective component uses eligible self-report. The objective component maps eligible physiology to proposed coordinates. Fused positions combine available terms using the documented weight α; a missing term is never silently promoted to complete fusion. The chart changes component without placing unavailable trials at an invented origin.</p></Section>
        <Section title="Component availability"><div className="metric-row">{(['subjective', 'objective'] as const).map(key => <div className="metric-card" key={key}><span className="value">{trials.filter(trial => trial[key]).length}</span><span className="label">{key} positions</span></div>)}<div className="metric-card"><span className="value">{complete.length}</span><span className="label">Complete fusion</span></div><div className="metric-card"><span className="value">{partial.length}</span><span className="label">Partial-modality fusion</span></div></div></Section>
        <Section title="Independent people behind positions"><p>{new Set(complete.map(trial => trial.participant_id)).size} participant IDs contribute complete-fusion positions; {new Set(partial.map(trial => trial.participant_id)).size} contribute partial-modality positions in this filter. Trial counts are not independent people.</p></Section>
        {(experiment === 'all' || experiment === '1') && <Section title="Experiment 1 comfort"><p>Comfort is a separately reported construct. These supplied values are not valence, arousal or fused positions, and they are never plotted on the affect plane.</p><div className="table-wrap"><table className="data-table"><thead><tr><th scope="col">Trial</th><th scope="col">Person</th><th scope="col">Room</th><th scope="col">Supplied comfort</th></tr></thead><tbody>{comfort.map(trial => <tr key={trial.id}><th scope="row">{trial.id}</th><td>{trial.participant_id}</td><td>{trial.room_id}</td><td><Value value={trial.comfort} /></td></tr>)}</tbody></table></div>{!comfort.length && <p>No Experiment 1 comfort observation matches this filter.</p>}</Section>}
        <Section title="Objective minus self-report"><p>Generated paired-axis disagreement is shown by experiment and cohort. The available-pair denominator n counts trials with both components for that axis; it is not a participant count. Rows follow the selected participant and experiment. Missing pairs have no substituted difference.</p>{disagreement.length ? <div className="table-wrap"><table className="data-table"><thead><tr><th scope="col">Experiment</th><th scope="col">Participant scope</th><th scope="col">Cohort</th><th scope="col">Axis</th><th scope="col">Paired n</th><th scope="col">Mean objective − self-report</th></tr></thead><tbody>{disagreement.map((row, index) => <tr key={`${row.experiment}-${row.participant_id}-${row.cohort}-${row.axis}-${index}`}><td>{row.experiment}</td><td>{row.participant_id || 'All eligible IDs'}</td><td>{row.cohort}</td><td>{row.axis}</td><td>{row.n}</td><td><Value value={row.mean_objective_minus_subjective} /></td></tr>)}</tbody></table></div> : <p>No paired disagreement result is available for this filter.</p>}</Section>
        <Section title="Trial records"><div className="table-wrap"><table className="data-table"><thead><tr><th scope="col">Trial</th><th scope="col">Person</th><th scope="col">Room</th><th scope="col">Cohort</th><th scope="col">Components</th><th scope="col">Valence</th><th scope="col">Arousal</th><th scope="col">Default α</th></tr></thead><tbody>{trials.map(trial => <tr key={trial.id}><th scope="row">{trial.id}</th><td>{trial.participant_id}</td><td>{trial.room_id}</td><td>{trial.cohort || 'Unclassified'}</td><td>{trial.available_components?.join(', ') || 'Unavailable'}</td><td><Value value={trial[component]?.valence} /></td><td><Value value={trial[component]?.arousal} /></td><td><Value value={trial.alpha} /></td></tr>)}</tbody></table></div></Section>
      </div><div className="figure-column"><Circumplex points={points} caption={`${component} positions from eligible records at exported default settings.${component === 'fused' ? ` ${complete.length} complete and ${partial.length} partial-modality positions in this filter.` : ''} The α control selects generated sensitivity rows; it does not recompute trial positions.`} /><Sensitivity rows={sensitivity} /></div></div>
    </>}
  </>;
}
