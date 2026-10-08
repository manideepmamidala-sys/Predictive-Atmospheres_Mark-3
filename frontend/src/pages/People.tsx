import { useState } from 'react';
import { useResearch, type Research } from '../lib/research';
import Circumplex from '../figures/Circumplex';
import { Notice, PageHeading, Section, Value } from '../ui';

type Person = Research['people'][number];
type ExperimentSummary = Person['by_experiment'][number];
type VisiblePerson = { person: Person; summary: Pick<Person, 'trials' | 'valid_fused' | 'mean_valence' | 'mean_arousal'>; sleep: ExperimentSummary | undefined };

export default function People() {
  const state = useResearch();
  const data = state.status === 'ready' ? state.data : null;
  const [experiment, setExperiment] = useState('all');
  const [personId, setPersonId] = useState('all');

  const visible: VisiblePerson[] = data?.people.flatMap(person => {
    if (personId !== 'all' && person.id !== personId) return [];
    const summary = experiment === 'all' ? person : person.by_experiment.find(row => String(row.experiment) === experiment);
    if (!summary) return [];
    const sleep = experiment === 'all'
      ? person.by_experiment.find(row => row.experiment === 3)
      : person.by_experiment.find(row => String(row.experiment) === experiment);
    return [{ person, summary, sleep }];
  }) || [];
  const points = visible.flatMap(({ person, summary }) => summary.mean_valence == null || summary.mean_arousal == null
    ? []
    : [{ id: person.id, label: person.id, position: { valence: summary.mean_valence, arousal: summary.mean_arousal } }]);

  return <><PageHeading eyebrow="Repeated experiences" title="People" intro="Inspect participant summaries within the selected experiment. Source IDs can recur across experiments; each row states the records behind its mean." />
    {!data ? <Notice title="Participant export unavailable" warning><p>{state.status === 'error' ? state.message : 'Loading participant summaries.'}</p></Notice> : <>
      <div className="toolbar">
        <label>Experiment<select value={experiment} onChange={event => setExperiment(event.target.value)}><option value="all">All experiments</option>{data.study.experiments.map(item => <option key={item.id} value={item.id}>Experiment {item.id}</option>)}</select></label>
        <label>Participant<select value={personId} onChange={event => setPersonId(event.target.value)}><option value="all">All participant IDs</option>{data.people.map(person => <option key={person.id}>{person.id}</option>)}</select></label>
        <span className="status">{visible.length} participant {visible.length === 1 ? 'summary' : 'summaries'}</span>
      </div>
      <div className="page-grid"><div className="reading">
        <Section title="Participant summaries">
          <p>Trials and complete-fusion means follow the selected experiment. Experiment 1 comfort is a separate construct, so its fused means remain unavailable. Age and reported gender come from the source ID mapping. Sleep was recorded only in Experiment 3; its range and count describe available trial observations, not a stable personal trait.</p>
          <div className="table-wrap"><table className="data-table"><thead><tr><th scope="col">ID</th><th scope="col">Trials</th><th scope="col">Complete fusion n</th><th scope="col">Valence</th><th scope="col">Arousal</th><th scope="col">Age</th><th scope="col">Reported gender</th><th scope="col">Sleep (E3 observations)</th></tr></thead><tbody>
            {visible.map(({ person, summary, sleep }) => <tr key={person.id}><th scope="row">{person.id}</th><td>{summary.trials}</td><td>{summary.valid_fused}</td><td><Value value={summary.mean_valence} /></td><td><Value value={summary.mean_arousal} /></td><td><Value value={person.age} unit="years" /></td><td>{person.gender || 'Unavailable'}</td><td>{sleep?.sleep_observations ? <><Value value={sleep.sleep_hours} unit="h mean" />; <Value value={sleep.sleep_min_hours} />–<Value value={sleep.sleep_max_hours} unit="h range" />; n={sleep.sleep_observations}</> : experiment === '3' ? 'No recorded sleep' : 'Structurally unavailable'}</td></tr>)}
          </tbody></table></div>
          {!visible.length && <p>No participant matches this experiment and ID.</p>}
        </Section>
        <Section title="Interpreting cohort differences"><p>Repeated trials from one person are not independent participants. Demographic fields are descriptive source metadata, and sparse complete-fusion records do not establish a demographic effect. An unavailable mean is not zero.</p></Section>
      </div><div className="figure-column"><Circumplex points={points} caption="Per-participant complete-fusion mean for the selected experiment scope. Table counts give contributing trials; point placement has no inferred uncertainty interval." /></div></div>
    </>}
  </>;
}
