import { Link } from 'react-router-dom';
import { useResearch } from '../lib/research';
import Catalogue from './Catalogue';
import { Notice, PageHeading, Value, modelStatusLabel } from '../ui';

export default function Prediction() {
  const state = useResearch();
  const model = state.status === 'ready' ? state.data.model : null;
  return <><PageHeading eyebrow="04 / Model evaluation" title="Prediction & Findings" intro="Do spatial attributes predict a held-out experience, and how does an experimental model compare with simple baselines? The answer depends on the target, eligible cohort and holdout design." />
    <section className="prediction-lead"><div><p className="eyebrow">The generalization question</p><h2>A studied room is not an unseen room.</h2><p>Participant holdouts test transfer to another person who may have viewed a known room. Room holdouts test transfer to unseen room attributes. Both analyses must fit preprocessing and target construction within training folds. Performance belongs beside its baseline and missingness, including an explicit unavailable result.</p><Link to="/methods">Review the analysis method ↗</Link></div><div className="model-status-panel"><p className="eyebrow">Current exported model status</p>{model ? <><strong>{modelStatusLabel(model.status)}</strong><p>{model.explanation}</p>{model.summary && <dl><div><dt>Eligible trials</dt><dd><Value value={model.summary.cohort_trials} /></dd></div><div><dt>People</dt><dd><Value value={model.summary.cohort_participants} /></dd></div><div><dt>Rooms</dt><dd><Value value={model.summary.cohort_rooms} /></dd></div></dl>}</> : <p>{state.status === 'error' ? state.message : 'Loading the validated model report.'}</p>}</div></section>
    <div className="prediction-flow" aria-label="Model evaluation sequence"><span>Eligible room–response pairs</span><span aria-hidden="true">→</span><span>Train within folds</span><span aria-hidden="true">→</span><span>Held-out comparison</span><span aria-hidden="true">→</span><span>Baseline and limits</span></div>
    {model?.status === 'baseline_only' && <Notice title="Baseline-only result" warning><p>The selected model is a baseline and currently gives the same fused position for different room geometry. The atlas does not claim a learned spatial gain or reliable individual prediction; see the held-out errors and null comparisons below.</p></Notice>}
    {model?.status === 'not_better_than_baseline' && <Notice title="Experimental model limit" warning><p>The exported model did not outperform its reported baseline under the held-out evaluation. The Design Studio may still expose the model as a research demonstration, with this limit in view.</p></Notice>}
    <Catalogue ids={['P1', 'P2', 'P3', 'P4', 'P5']} title="Prediction questions and evidence" />
    <div className="next-route"><span>Continue the investigation</span><Link to="/studio">Test the experimental Design Studio ↗</Link></div>
  </>;
}
