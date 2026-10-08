import type { Position } from '../lib/research';
import { Figure, Value } from '../ui';

export type AffectPoint = { id: string; label: string; position: Position; kind?: 'subjective' | 'objective' | 'fused'; cohort?: string | null; cct?: number | null };
const clamp = (value: number) => Math.max(-1, Math.min(1, value));
function color(cct: number | null | undefined) {
  if (cct == null) return 'var(--muted)';
  const warmShare = Math.round((1 - Math.max(0, Math.min(1, (cct - 2700) / (6500 - 2700)))) * 100);
  return `color-mix(in oklch, var(--lamp) ${warmShare}%, var(--sky))`;
}
export default function Circumplex({ points, caption = 'Valence–arousal coordinates. Position encodes the axes; warm and cool points indicate documented lighting temperature when available.' }: { points: AffectPoint[]; caption?: string }) {
  return <Figure title="Atmosphere plane" caption={`${caption} n = ${points.length} plotted positions. Source: generated affect export.`}>
    <svg viewBox="0 0 420 420" role="img" aria-label={`Valence arousal plot with ${points.length} positions. A data table follows.`}>
      <rect x="45" y="25" width="340" height="340" fill="var(--plot)" stroke="var(--rule)" />
      <line className="gridline" x1="215" y1="25" x2="215" y2="365" /><line className="gridline" x1="45" y1="195" x2="385" y2="195" />
      <text className="plot-label" x="180" y="405">Valence →</text><text className="plot-label" x="6" y="18">Arousal ↑</text>
      {points.map((point, index) => <circle key={`${point.id}-${point.kind}-${index}`} className="point" tabIndex={0} role="img" aria-label={`${point.label}, ${point.cohort || 'cohort unavailable'}: valence ${point.position.valence.toFixed(2)}, arousal ${point.position.arousal.toFixed(2)}`} cx={215 + clamp(point.position.valence) * 170} cy={195 - clamp(point.position.arousal) * 170} r="5" fill={point.cohort === 'partial_modality_fusion' ? 'var(--plot)' : color(point.cct)} stroke={point.cohort === 'partial_modality_fusion' ? color(point.cct) : 'var(--plot)'} strokeWidth={point.cohort === 'partial_modality_fusion' ? '2.5' : '1.5'}><title>{point.label}: valence {point.position.valence.toFixed(2)}, arousal {point.position.arousal.toFixed(2)}, {point.cohort || 'cohort unavailable'}</title></circle>)}
    </svg>
    <div className="legend"><span className="warm">Lower reported CCT</span><span>Higher reported CCT</span> · Display scale: 2700–6500 K · Grey: CCT unavailable · Open circle: partial-modality fusion</div>
    {points.length ? <div className="table-wrap"><table className="data-table"><caption className="small-text">Accessible plotted values</caption><thead><tr><th scope="col">Record</th><th scope="col">Component</th><th scope="col">Cohort</th><th scope="col">Valence</th><th scope="col">Arousal</th><th scope="col">CCT</th></tr></thead><tbody>{points.slice(0, 100).map((point, i) => <tr key={`${point.id}-${point.kind}-${i}`}><th scope="row">{point.label}</th><td>{point.kind || 'position'}</td><td>{point.cohort || 'Unavailable'}</td><td><Value value={point.position.valence} /></td><td><Value value={point.position.arousal} /></td><td><Value value={point.cct} unit="K" /></td></tr>)}</tbody></table>{points.length > 100 && <p className="figure-note">Table shows the first 100 records. Filter to narrow the view.</p>}</div> : <p className="small-text">No eligible position is available for this selection.</p>}
  </Figure>;
}
