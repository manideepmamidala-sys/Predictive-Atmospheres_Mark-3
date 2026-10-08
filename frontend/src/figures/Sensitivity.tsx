import type { Research } from '../lib/research';
import { Figure, Value } from '../ui';

export default function Sensitivity({ rows }: { rows: Research['sensitivity'] }) {
  return <Figure title="Fusion weight sensitivity" caption="Descriptive mean positions at prespecified fusion weights. Intervals appear only when the export supplies them. n varies with eligible components; source: generated affect export.">
    {rows.length ? <div className="table-wrap"><table className="data-table"><thead><tr><th scope="col">Experiment</th><th scope="col">α</th><th scope="col">Eligible n</th><th scope="col">Valence</th><th scope="col">Arousal</th><th scope="col">Valence interval</th></tr></thead><tbody>{rows.map((row, index) => <tr key={`${row.experiment}-${row.alpha}-${index}`}><td>{row.experiment ?? 'Pooled'}</td><th scope="row"><Value value={row.alpha} /></th><td>{row.n}</td><td><Value value={row.mean_valence} /></td><td><Value value={row.mean_arousal} /></td><td>{row.interval_valence ? `${row.interval_valence[0].toFixed(2)}–${row.interval_valence[1].toFixed(2)}` : 'Unavailable'}</td></tr>)}</tbody></table></div> : <p>No valid sensitivity result is available.</p>}
  </Figure>;
}
