import { Figure } from '../ui';
import type { Trial } from '../lib/research';

type Trace = NonNullable<Trial['eeg']>;
function line(samples: number[], height: number) {
  if (samples.length < 2) return '';
  const finite = samples.filter(Number.isFinite);
  if (!finite.length) return '';
  const min = Math.min(...finite), max = Math.max(...finite), span = max - min || 1;
  return samples.map((value, index) => `${index ? 'L' : 'M'}${(index / (samples.length - 1) * 600).toFixed(1)},${(height - (value - min) / span * (height - 20) - 10).toFixed(1)}`).join(' ');
}
export default function SignalTrace({ title, trace, mode }: { title: string; trace: Trace | null | undefined; mode: 'raw' | 'cleaned' }) {
  const values = trace?.[mode] || [];
  const duration = trace?.sample_rate_hz && values.length ? values.length / trace.sample_rate_hz : null;
  const windowStart = trace?.window_start_s || 0;
  return <Figure title={title} caption={`${mode === 'raw' ? 'Raw' : 'Cleaned'} bounded trace export${trace?.channel ? ` (${trace.channel})` : ''}. n = ${values.length} displayed samples; unit: ${trace?.unit || 'unavailable'}; display rate: ${trace?.sample_rate_hz ?? 'unconfirmed'} Hz; source analytical scenario: ${trace?.source_sample_rate_hz ?? 'unconfirmed'} Hz; window: ${duration == null ? 'unavailable' : `${windowStart.toFixed(1)}–${(windowStart + duration).toFixed(1)} s`}. Browser traces are anti-aliased display derivatives; physiological features were calculated from the full-rate source. Shaded segments are rejected by QC. The source acquisition rate remains unverified. Source: generated signals export.`}>
    {values.length > 1 ? <svg viewBox="0 0 600 170" role="img" aria-label={`${title} ${mode} trace with ${values.length} displayed samples`}><rect x="0" y="0" width="600" height="170" fill="var(--plot)" />{trace?.rejected_segments.map(([start, end], i) => duration ? <rect key={i} x={Math.max(0, (start - windowStart) / duration * 600)} width={Math.max(0, (Math.min(end, windowStart + duration) - Math.max(start, windowStart)) / duration * 600)} y="0" height="170" fill="var(--alert)" opacity=".15" /> : null)}<path d={line(values, 170)} fill="none" stroke="var(--sky)" strokeWidth="1.5" vectorEffect="non-scaling-stroke" /></svg> : <p className="small-text">No {mode} trace was exported for this trial.</p>}
    <p className="figure-note">The chart preserves export sample order and does not calculate physiological features in the browser.</p>
  </Figure>;
}
