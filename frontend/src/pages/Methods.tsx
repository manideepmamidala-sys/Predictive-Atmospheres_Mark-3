import { Link } from 'react-router-dom';
import Catalogue from './Catalogue';
import { PageHeading } from '../ui';

const glossary = [
  ['Valence', 'A signed axis from unpleasant (−1) to pleasant (+1) in the constructed affect plane.'],
  ['Arousal', 'A signed axis from calm (−1) to activated (+1) in the constructed affect plane.'],
  ['Physiology-derived', 'A candidate valence–arousal position constructed from eligible forehead EEG and wrist ECG features under documented assumptions.'],
  ['Self-reported', 'A participant response; Experiment 1 comfort is separate from later valence–arousal ratings.'],
  ['Fused', 'A documented weighted combination of eligible physiology-derived and self-reported coordinates. Missing components remain explicit.'],
  ['Neuro-Score', 'Proximity of a model-predicted fused coordinate to a selected emotional target, displayed from 0 to 100. It is not a health, certainty or design-quality score.'],
  ['Held-out room', 'A room excluded from model fitting when testing transfer to unseen room attributes.'],
];

export default function Methods() {
  return <><PageHeading eyebrow="07 / Method and context" title="Methods & Research Context" intro="The atlas carries an evolving analysis of an earlier architectural thesis. This page distinguishes the source experiments, current reproducible methods and historical design demonstrations." />
    <section className="methods-columns"><div><p className="eyebrow">Source study</p><h2>What was recorded</h2><p>Thirty rendered rooms, repeated participant exposures, approximate bilateral forehead EEG, wrist ECG and available ratings form the source record. Source protocol and metadata define what can be linked; they do not establish a measured neutral baseline, calibrated headset illuminance or verified hardware sample rate.</p><p>Experiment 1 supplied comfort. Experiments 2 and 3 supplied valence–arousal ratings under different elicitation procedures. Their observations are separated before any combined view.</p></div><div><p className="eyebrow">Current analysis</p><h2>What is constructed</h2><p>Quality checks determine which signal features can be used. Documented mappings propose physiology-derived coordinates; reports remain their own component. Fusion is a descriptive hypothesis, compared with both parts. Predictions are evaluated on held-out people and rooms against simple baselines.</p><p>The public research charts are generated from versioned exports. An unavailable value carries its reason, and trial counts are distinguished from independent participants and rooms.</p></div></section>
    <section className="prototype-story"><div><p className="eyebrow">Thesis demonstrations · historical context</p><h2>From evidence to a designer's canvas</h2><p>The thesis demonstrated a Grasshopper connection that sent Rhino room attributes to a backend and displayed predicted coordinates and a score in the canvas. A separate AI rendering demonstration used a Rhino camera and an attribute/prediction prompt. These are documented proof-of-concept workflows from the thesis, rather than live features of this atlas.</p><p>The current <Link to="/studio">Design Studio</Link> uses a schematic room volume, a fitted experimental model when available and clearly labeled renders of studied rooms for comparison.</p></div><div className="method-diagram" role="img" aria-label="Room attributes flow through a model to a predicted fused position and user-target Neuro-Score; studied room imagery remains reference material"><span>ROOM ATTRIBUTES</span><i aria-hidden="true">↓</i><span>EXPERIMENTAL MODEL</span><i aria-hidden="true">↓</i><span>FUSED POSITION</span><i aria-hidden="true">↓</i><span>TARGET PROXIMITY</span></div></section>
    <section className="glossary"><div className="section-heading"><div><p className="eyebrow">Reading guide</p><h2>Terms used across the atlas</h2></div><Link to="/explore">Inspect records ↗</Link></div><dl>{glossary.map(([term, meaning]) => <div key={term}><dt>{term}</dt><dd>{meaning}</dd></div>)}</dl></section>
    <Catalogue ids={['Methods']} title="Versioned method record" />
  </>;
}
