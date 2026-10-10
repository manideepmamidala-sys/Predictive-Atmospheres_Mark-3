import { useRef, useState, type KeyboardEvent } from 'react';
import type { Position } from '../lib/research';
import { Figure, Value } from '../ui';

export type AffectPoint = { id: string; label: string; position: Position; kind?: 'subjective' | 'objective' | 'fused'; cohort?: string | null; cct?: number | null };
const clamp = (value: number) => Math.max(-1, Math.min(1, value));
const pointColor = (point: AffectPoint) => point.kind === 'subjective' ? 'var(--lamp)' : point.kind === 'objective' ? 'var(--sky)' : 'var(--ink)';
const kindLabel = (kind?: AffectPoint['kind']) => kind === 'objective' ? 'Physiology-derived' : kind === 'subjective' ? 'Self-reported' : kind === 'fused' ? 'Fused' : 'Position';

export default function Circumplex({ points, caption = 'Valence–arousal coordinates from the exported research record.' }: { points: AffectPoint[]; caption?: string }) {
  const [active, setActive] = useState(0);
  const refs = useRef<(SVGCircleElement | null)[]>([]);
  function move(event: KeyboardEvent<SVGCircleElement>, index: number) {
    const next = event.key === 'ArrowRight' || event.key === 'ArrowDown' ? Math.min(points.length - 1, index + 1) : event.key === 'ArrowLeft' || event.key === 'ArrowUp' ? Math.max(0, index - 1) : event.key === 'Home' ? 0 : event.key === 'End' ? points.length - 1 : null;
    if (next != null) { event.preventDefault(); setActive(next); refs.current[next]?.focus(); }
  }
  return <Figure title="Valence–arousal plane" caption={`${caption} n = ${points.length} plotted positions. Source: generated affect export.`}>
    <svg viewBox="0 0 460 440" role="group" aria-label={`Signed valence arousal plot with ${points.length} positions, axes from minus one to plus one. A complete data table follows.`}>
      <rect x="55" y="35" width="340" height="340" fill="var(--plot)" stroke="var(--rule)" />
      <line className="gridline" x1="225" y1="35" x2="225" y2="375" /><line className="gridline" x1="55" y1="205" x2="395" y2="205" />
      <text className="plot-label" x="61" y="55">activated · unpleasant</text><text className="plot-label" x="264" y="55">activated · pleasant</text>
      <text className="plot-label" x="61" y="365">calm · unpleasant</text><text className="plot-label" x="289" y="365">calm · pleasant</text>
      {[-1, 0, 1].map(value => <g key={`x-${value}`}><line className="axis" x1={225 + value * 170} x2={225 + value * 170} y1="375" y2="381" /><text className="plot-label" x={225 + value * 170} y="398" textAnchor="middle">{value === 1 ? '+1' : value === -1 ? '−1' : '0'}</text></g>)}
      {[-1, 0, 1].map(value => <g key={`y-${value}`}><line className="axis" x1="49" x2="55" y1={205 - value * 170} y2={205 - value * 170} /><text className="plot-label" x="44" y={209 - value * 170} textAnchor="end">{value === 1 ? '+1' : value === -1 ? '−1' : '0'}</text></g>)}
      <text className="plot-label" x="225" y="424" textAnchor="middle">Valence · unpleasant → pleasant</text><text className="plot-label" transform="translate(13 205) rotate(-90)" textAnchor="middle">Arousal · calm → activated</text>
      {points.map((point, index) => <circle key={`${point.id}-${point.kind}-${index}`} ref={element => { refs.current[index] = element; }} className="point" tabIndex={index === active ? 0 : -1} role="img" aria-label={`${point.label}, ${kindLabel(point.kind)}: valence ${point.position.valence.toFixed(2)}, arousal ${point.position.arousal.toFixed(2)}`} onFocus={() => setActive(index)} onKeyDown={event => move(event, index)} cx={225 + clamp(point.position.valence) * 170} cy={205 - clamp(point.position.arousal) * 170} r="5" fill={point.cohort === 'partial_modality_fusion' ? 'var(--plot)' : pointColor(point)} stroke={pointColor(point)} strokeWidth="2"><title>{point.label}: valence {point.position.valence.toFixed(2)}, arousal {point.position.arousal.toFixed(2)}</title></circle>)}
    </svg>
    <p className="figure-note">Each axis runs from −1 to +1. Tab into the plot, then use arrow keys, Home or End to inspect positions. Open circles denote partial-modality fusion. The table below provides every plotted value.</p>
    {points.length > 0 && <p className="status" aria-live="polite">Selected: {points[Math.min(active, points.length - 1)].label}; valence <Value value={points[Math.min(active, points.length - 1)].position.valence} />; arousal <Value value={points[Math.min(active, points.length - 1)].position.arousal} />.</p>}
    {points.length ? <div className="table-wrap"><table className="data-table"><caption>Accessible plotted valence and arousal values, all {points.length} positions</caption><thead><tr><th scope="col">Record</th><th scope="col">Component</th><th scope="col">Cohort</th><th scope="col">Valence (−1 to +1)</th><th scope="col">Arousal (−1 to +1)</th></tr></thead><tbody>{points.map((point, index) => <tr key={`${point.id}-${point.kind}-${index}`}><th scope="row">{point.label}</th><td>{kindLabel(point.kind)}</td><td>{point.cohort || 'Unavailable'}</td><td><Value value={point.position.valence} /></td><td><Value value={point.position.arousal} /></td></tr>)}</tbody></table></div> : <p className="small-text">No eligible position is available for this selection.</p>}
  </Figure>;
}
