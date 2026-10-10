import { contours } from 'd3-contour';
import type { AnalysisProduct } from '../lib/research';

type Row = AnalysisProduct['chart']['rows'][number];
const number = (value: Row[string]): value is number => typeof value === 'number' && Number.isFinite(value);
const xPosition = (value: number) => 54 + (value + 1) * 130;
const yPosition = (value: number) => 314 - (value + 1) * 130;
const label = (row: Row) => [row.experiment == null ? null : `Experiment ${row.experiment}`, row.component].filter(Boolean).join(' · ');

function contourPath(coordinates: number[][][][], width: number, height: number) {
  return coordinates.map(polygon => polygon.map(ring => ring.map(([x, y], index) => `${index ? 'L' : 'M'}${(54 + x / width * 260).toFixed(1)},${(314 - y / height * 260).toFixed(1)}`).join(' ') + ' Z').join(' ')).join(' ');
}

function DensityPanel({ rows, id }: { rows: Row[]; id: string }) {
  const grid = rows.filter(row => row.kind === 'density_grid' && number(row.valence) && number(row.arousal) && number(row.density));
  const positions = rows.filter(row => row.kind === 'source_position' && number(row.valence) && number(row.arousal));
  const vectors = rows.filter(row => row.kind === 'target_vector' && number(row.source_valence) && number(row.source_arousal) && number(row.target_valence) && number(row.target_arousal));
  const x = [...new Set(grid.map(row => row.valence as number))].sort((a, b) => a - b);
  const y = [...new Set(grid.map(row => row.arousal as number))].sort((a, b) => a - b);
  const values = new Map(grid.map(row => [`${row.valence},${row.arousal}`, row.density as number]));
  const max = Math.max(0, ...grid.map(row => row.density as number));
  const contourValues = y.flatMap(yValue => x.map(xValue => values.get(`${xValue},${yValue}`) || 0));
  const lines = x.length > 1 && y.length > 1 && max > 0 ? contours().size([x.length, y.length]).thresholds(5)(contourValues) : [];
  const marker = `arrow-${id.replace(/[^a-z0-9]/gi, '-')}`;
  return <div className="density-panel"><h4>{label(rows[0]) || 'Comparable cohort'}</h4><svg viewBox="0 0 350 355" role="img" aria-label={`Backend-computed affect density for ${label(rows[0]) || 'the selected cohort'}, ${positions.length} source positions and ${vectors.length} target vectors. Data table follows.`}>
    <defs><marker id={marker} markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8 Z" fill="var(--lamp)" /></marker></defs>
    <rect x="54" y="54" width="260" height="260" fill="var(--plot)" stroke="var(--rule)" />
    {grid.map((row, index) => <rect key={index} x={xPosition(row.valence as number) - 260 / Math.max(1,x.length) / 2} y={yPosition(row.arousal as number) - 260 / Math.max(1,y.length) / 2} width={260 / Math.max(1,x.length) + .5} height={260 / Math.max(1,y.length) + .5} fill="var(--sky)" opacity={max ? .08 + (row.density as number) / max * .62 : .08} />)}
    {lines.map((line, index) => <path key={index} d={contourPath(line.coordinates, x.length, y.length)} fill="none" stroke="var(--ink)" strokeOpacity={.18 + index / Math.max(1,lines.length) * .35} strokeWidth=".8" />)}
    <line x1="184" y1="54" x2="184" y2="314" className="gridline" /><line x1="54" y1="184" x2="314" y2="184" className="gridline" />
    {positions.map((row, index) => <circle key={index} cx={xPosition(row.valence as number)} cy={yPosition(row.arousal as number)} r="3" fill="var(--ink)" opacity=".6"><title>{String(row.participant_id || 'Trial')} · {String(row.room_id || 'room unavailable')}: valence {row.valence}, arousal {row.arousal}</title></circle>)}
    {vectors.map((row, index) => <line key={index} x1={xPosition(row.source_valence as number)} y1={yPosition(row.source_arousal as number)} x2={xPosition(row.target_valence as number)} y2={yPosition(row.target_arousal as number)} stroke="var(--lamp)" strokeWidth="2.5" markerEnd={`url(#${marker})`}><title>Target vector to valence {row.target_valence}, arousal {row.target_arousal}</title></line>)}
    {[-1,0,1].map(value => <g key={value}><text x={xPosition(value)} y="332" className="plot-label" textAnchor="middle">{value === -1 ? '−1' : value === 1 ? '+1' : '0'}</text><text x="44" y={yPosition(value)+4} className="plot-label" textAnchor="end">{value === -1 ? '−1' : value === 1 ? '+1' : '0'}</text></g>)}
    <text x="184" y="350" textAnchor="middle" className="plot-label">Valence · signed coordinate</text><text transform="translate(12 184) rotate(-90)" textAnchor="middle" className="plot-label">Arousal · signed coordinate</text>
  </svg><p className="figure-note">Darker blue = greater exported density within this panel; contour lines show its shape. Dots = contributing positions; amber arrow = exported target vector. All panels use the same signed axes. Density is descriptive, not a probability of individual emotion.</p></div>;
}

export default function DensityFigure({ product }: { product: AnalysisProduct }) {
  const rows = product.chart.rows;
  const grouped = new Map<string, Row[]>();
  for (const row of rows) {
    const key = `${row.experiment ?? 'all'}|${row.component ?? 'all'}`;
    grouped.set(key, [...(grouped.get(key) || []), row]);
  }
  return <div className="density-grid">{[...grouped].map(([key, group]) => <DensityPanel key={key} id={`${product.id}-${key}`} rows={group} />)}</div>;
}
