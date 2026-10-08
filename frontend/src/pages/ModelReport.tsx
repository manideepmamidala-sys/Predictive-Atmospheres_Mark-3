import { Link } from 'react-router-dom';
import { useResearch } from '../lib/research';
import { repositoryFileUrl } from '../lib/repository';
import { Notice, PageHeading, Section, Value, modelStatusLabel } from '../ui';

const label = (key: string) => key.replaceAll('_', ' ');

export default function ModelReport() {
  const state = useResearch();
  const data = state.status === 'ready' ? state.data : null;
  const summary = data?.model.summary;
  return <><PageHeading eyebrow="Experimental modeling" title="Model report" intro="Read the eligible cohort, fitted preparation and held-out comparisons behind this pilot predictor. It is not a validated design tool." />
    {!data ? <Notice title="Model report unavailable" warning><p>{state.status === 'error' ? state.message : 'Loading model evaluation.'}</p></Notice> : <div className="page-grid"><div className="reading">
      <Notice title={`Model status: ${modelStatusLabel(data.model.status)}`} warning={data.model.status !== 'ready'}><p>{data.model.explanation}</p>{data.model.status === 'not_better_than_baseline' && <p>This experimental predictor did not improve on the reported baseline under held-out evaluation.</p>}</Notice>
      {summary ? <>
        <Section title="Eligible modeling cohort"><div className="metric-row"><div className="metric-card"><span className="value">{summary.cohort_trials}</span><span className="label">Eligible trials</span></div><div className="metric-card"><span className="value">{summary.cohort_participants}</span><span className="label">Participants</span></div><div className="metric-card"><span className="value">{summary.cohort_rooms}</span><span className="label">Rooms</span></div></div><p>These are the records eligible for the population-constructed target, not the separate within-person descriptive fusion cohort.</p>
          {Object.keys(summary.exclusions).length ? <div className="table-wrap"><table className="data-table"><caption className="small-text">Generated eligibility and exclusion counts</caption><thead><tr><th scope="col">Reason or stage</th><th scope="col">Count</th></tr></thead><tbody>{Object.entries(summary.exclusions).map(([name, count]) => <tr key={name}><th scope="row">{label(name)}</th><td>{count}</td></tr>)}</tbody></table></div> : <p>No generated exclusion breakdown is available.</p>}
        </Section>
        <Section title="Fitted preparation and selection"><p>Model selection status: {summary.selection_status || 'Unavailable'}.</p>{summary.preprocessing.length ? <ul>{summary.preprocessing.map((step, index) => <li key={index}>{step}</li>)}</ul> : <p>Preprocessing detail unavailable.</p>}
          {summary.selected_candidate ? <div className="table-wrap"><table className="data-table"><caption className="small-text">Selected candidate configuration</caption><tbody>{Object.entries(summary.selected_candidate).map(([name, value]) => <tr key={name}><th scope="row">{label(name)}</th><td>{String(value)}</td></tr>)}</tbody></table></div> : <p>Selected candidate unavailable.</p>}
          <p>{summary.participant_baseline_fallback}</p>
        </Section>
      </> : <Notice title="Detailed model evidence unavailable"><p>The export does not include a generated cohort or preparation summary.</p></Notice>}
      <Section title="Held-out evaluation"><p>Room and participant holdouts ask different generalization questions. Target transforms and preprocessing are fitted inside training partitions; metrics with no eligible fold or defensible interval remain unavailable. The participant-fold fallback is described above when exported.</p>{data.model.metrics.length ? <div className="table-wrap"><table className="data-table"><thead><tr><th scope="col">Measure</th><th scope="col">Value</th><th scope="col">Interval</th><th scope="col">n</th><th scope="col">Group</th></tr></thead><tbody>{data.model.metrics.map((metric, index) => <tr key={`${metric.name}-${index}`}><th scope="row">{label(metric.name)}</th><td><Value value={metric.value} unit={metric.unit || undefined} /></td><td>{metric.interval ? `${metric.interval[0].toFixed(2)}–${metric.interval[1].toFixed(2)}` : 'Unavailable'}</td><td><Value value={metric.n} /></td><td>{metric.group ? label(metric.group) : '—'}</td></tr>)}</tbody></table></div> : <p>No eligible model metric is available.</p>}</Section>
      <Section title="Known limits">{data.model.limitations.length ? <ul>{data.model.limitations.map((item, index) => <li key={index}>{item}</li>)}</ul> : <p>See the versioned model card for data and method limits.</p>}<p>The <Link to="/simulator">room simulator</Link> keeps weak-model and support status visible; it does not invent calibrated intervals.</p></Section>
    </div><div className="figure-column"><div className="card"><h3>Artifact and evidence</h3><p className="small-text">Artifact version: {data.model.artifact_version || 'Unavailable'}</p><p className="small-text">Schema version: {data.schema_version}</p><p className="small-text">Source: {data.provenance.source}</p><p className="small-text">Method: {data.provenance.method}</p>
      {summary && <><h3>Provenance hashes</h3><div className="table-wrap"><table className="data-table"><tbody>{Object.entries(summary.provenance).map(([name, hash]) => <tr key={name}><th scope="row">{label(name)}</th><td style={{ overflowWrap: 'anywhere' }}><code>{hash}</code></td></tr>)}</tbody></table></div><h3>Detailed records</h3><ul>{Object.entries(summary.evidence_links).map(([name, path]) => { const url = repositoryFileUrl(path); return <li key={name}>{url ? <a href={url} target="_blank" rel="noreferrer">{label(name)}</a> : label(name)}</li>; })}</ul></>}
    </div></div></div>}
  </>;
}
