import type { KeyboardEvent, MouseEvent } from 'react';
import type { AffectTarget } from '../api/client';

const clamp = (value: number) => Math.max(-1, Math.min(1, Math.round(value * 100) / 100));
const projectX = (value: number) => 38 + (value + 1) * 120;
const projectY = (value: number) => 278 - (value + 1) * 120;

export default function TargetPlane({ target, onChange, predicted }: { target: AffectTarget; onChange: (target: AffectTarget) => void; predicted?: AffectTarget | null }) {
  function point(event: MouseEvent<SVGSVGElement>) {
    const rect = event.currentTarget.getBoundingClientRect();
    const x = (event.clientX - rect.left) * 320 / rect.width;
    const y = (event.clientY - rect.top) * 320 / rect.height;
    onChange({ valence: clamp((x - 38) / 120 - 1), arousal: clamp((278 - y) / 120 - 1) });
  }
  function key(event: KeyboardEvent<SVGCircleElement>) {
    const step = event.shiftKey ? .01 : .05;
    const next = { ...target };
    if (event.key === 'ArrowRight') next.valence = clamp(next.valence + step);
    else if (event.key === 'ArrowLeft') next.valence = clamp(next.valence - step);
    else if (event.key === 'ArrowUp') next.arousal = clamp(next.arousal + step);
    else if (event.key === 'ArrowDown') next.arousal = clamp(next.arousal - step);
    else if (event.key === 'Home') { next.valence = 0; next.arousal = 0; }
    else return;
    event.preventDefault(); onChange(next);
  }
  return <div className="target-plane"><svg viewBox="0 0 320 320" onClick={point} role="group" aria-label="Select an emotional target on a signed valence and arousal plane">
    <rect x="38" y="38" width="240" height="240" fill="var(--plot)" stroke="var(--rule)" />
    <line x1="158" y1="38" x2="158" y2="278" className="gridline" /><line x1="38" y1="158" x2="278" y2="158" className="gridline" />
    <text className="plot-label" x="45" y="55">activated · unpleasant</text><text className="plot-label" x="185" y="55">activated · pleasant</text><text className="plot-label" x="45" y="269">calm · unpleasant</text><text className="plot-label" x="204" y="269">calm · pleasant</text>
    {[-1,0,1].map(n => <g key={`x${n}`}><text x={projectX(n)} y="296" className="plot-label" textAnchor="middle">{n === -1 ? '−1' : n === 1 ? '+1' : '0'}</text><text x="26" y={projectY(n)+4} className="plot-label" textAnchor="end">{n === -1 ? '−1' : n === 1 ? '+1' : '0'}</text></g>)}
    <text x="158" y="314" className="plot-label" textAnchor="middle">Valence →</text><text transform="translate(11 158) rotate(-90)" className="plot-label" textAnchor="middle">Arousal →</text>
    {predicted && <><line x1={projectX(target.valence)} y1={projectY(target.arousal)} x2={projectX(predicted.valence)} y2={projectY(predicted.arousal)} stroke="var(--lamp)" strokeWidth="2" strokeDasharray="5 3" /><circle cx={projectX(predicted.valence)} cy={projectY(predicted.arousal)} r="7" fill="var(--lamp)" stroke="var(--plot)" strokeWidth="2"><title>Predicted fused position: valence {predicted.valence.toFixed(2)}, arousal {predicted.arousal.toFixed(2)}</title></circle></>}
    <circle cx={projectX(target.valence)} cy={projectY(target.arousal)} r="9" fill="var(--sky)" stroke="var(--plot)" strokeWidth="3" tabIndex={0} role="button" aria-label={`Emotional target on valence and arousal plane: valence ${target.valence.toFixed(2)}, arousal ${target.arousal.toFixed(2)}`} onKeyDown={key}><title>Target: valence {target.valence.toFixed(2)}, arousal {target.arousal.toFixed(2)}</title></circle>
  </svg><p className="figure-note">Select a point, or focus the blue marker and use arrow keys (Shift for 0.01 steps; Home centres it). Blue = your target{predicted ? '; amber = predicted fused point; dashed line = distance scored' : ''}. Numeric fields below set the same coordinates.</p></div>;
}
