import { useEffect, useRef, useState } from 'react';
import * as Plot from '@observablehq/plot';
import DensityFigure from './DensityFigure';
import type { AnalysisProduct } from '../lib/research';
import { Value } from '../ui';

type Row = AnalysisProduct['chart']['rows'][number];
const readable = (key: string) => key.replaceAll('_', ' ').replace(/\b\w/g, letter => letter.toUpperCase());
const numeric = (value: Row[string] | undefined): value is number => typeof value === 'number' && Number.isFinite(value);
const encoded = (value: Row[string]) => value == null ? 'Unavailable' : typeof value === 'number' ? <Value value={value} /> : String(value);
const countLabel = (count: number, singular: string, plural: string) => `${count} ${count === 1 ? singular : plural}`;
const axisTick = (value: unknown) => {
  const label = String(value);
  return /^(Rm_|Subj_|P\d)/.test(label) ? label : readable(label);
};
const visualSpread = (key: string) => {
  let hash = 0;
  for (const character of key) hash = (Math.imul(hash, 31) + character.charCodeAt(0)) >>> 0;
  return ((hash % 1001) / 1000 - .5) * .42;
};

function PlotView({ product, rows, facet, seriesInHeading }: { product: AnalysisProduct; rows: Row[]; facet?: string; seriesInHeading?: boolean }) {
  const ref = useRef<HTMLDivElement>(null);
  const [width, setWidth] = useState(640);
  const [contentOverflow, setContentOverflow] = useState(false);
  const [theme, setTheme] = useState(document.documentElement.dataset.theme);
  const chart = product.chart;
  const plottedRows = product.id === 'P3'
    ? rows.filter(row => numeric(row[chart.x]) && numeric(row[chart.y]) && row.error_unit === 'constructed-coordinate units')
    : rows;
  const xCategories = [...new Set(rows.map(row => row[chart.x]).filter((value): value is string => typeof value === 'string'))];
  const yCategories = [...new Set(rows.map(row => row[chart.y]).filter((value): value is string => typeof value === 'string'))];
  const longestX = Math.max(0, ...xCategories.map(value => axisTick(value).length));
  const longestY = Math.max(0, ...yCategories.map(value => axisTick(value).length));
  const marginLeft = Math.max(76, Math.ceil(longestY * 7.2 + 28));
  const marginBottom = xCategories.length > 2 ? Math.min(175, Math.max(74, Math.ceil(longestX * 4.6 + 30))) : 58;
  const marginTop = 38;
  const plotHeight = Math.max(360, marginTop + marginBottom + 260);
  const categoryBand = Math.min(150, Math.max(42, Math.ceil(longestX * 5.5 + 16)));
  const minimumPlotWidth = xCategories.length ? marginLeft + 28 + xCategories.length * categoryBand : 0;
  const plotWidth = Math.max(width, minimumPlotWidth);
  const scrollable = plotWidth > width + 4 || contentOverflow;
  useEffect(() => {
    const element = ref.current;
    if (!element) return;
    const resize = new ResizeObserver(() => setWidth(Math.max(280, Math.floor(element.clientWidth))));
    resize.observe(element);
    const themeObserver = new MutationObserver(() => setTheme(document.documentElement.dataset.theme));
    themeObserver.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
    return () => { resize.disconnect(); themeObserver.disconnect(); };
  }, []);
  useEffect(() => {
    const element = ref.current;
    if (!element || !rows.length || product.chart.type === 'table') return;
    const style = getComputedStyle(document.documentElement);
    const ink = style.getPropertyValue('--ink').trim();
    const sky = style.getPropertyValue('--sky').trim();
    const lamp = style.getPropertyValue('--lamp').trim();
    const functionRatings = product.id === 'R7';
    const categories = functionRatings ? [...new Set(rows.map(row => String(row.space_type)))].sort() : [];
    const colorValues = chart.series && !seriesInHeading ? plottedRows.map(row => row[chart.series!]).filter(value => value != null) : [];
    const numericColor = colorValues.length > 0 && colorValues.every(numeric);
    const correlation = product.id === 'S4' && chart.series === 'spearman_rho';
    const signedColor = numericColor && colorValues.some(value => (value as number) < 0);
    const color = chart.series && !seriesInHeading && !functionRatings ? correlation
      ? { legend: true, scheme: 'RdBu' as const, domain: [-1, 1] }
      : { legend: true, scheme: numericColor ? (signedColor ? 'RdBu' as const : 'Blues' as const) : 'observable10' as const }
      : undefined;
    const common = { x: chart.x, y: chart.y };
    let marks: Plot.Markish[];
    if (functionRatings) {
      const observed = rows.filter(row => row.kind === 'observed_trial').map((row, index) => ({ ...row, display_x: categories.indexOf(String(row.space_type)) + visualSpread(`${row.participant_id}:${row.room_id}:${row.axis}:${index}`) }));
      const means = rows.filter(row => row.kind === 'function_mean').map(row => ({ ...row, display_x: categories.indexOf(String(row.space_type)) }));
      marks = [
        Plot.dot(observed, { x: 'display_x', y: chart.y, fill: sky, fillOpacity: .48, stroke: sky, r: 3.5, className: 'r7-observations', title: row => `${row.participant_id} · ${row.room_id}: ${row.axis} rating ${row.mean_rating}` }),
        Plot.dot(means, { x: 'display_x', y: chart.y, symbol: 'diamond', fill: lamp, stroke: ink, strokeWidth: 1.5, r: 8, className: 'r7-means', title: row => `${row.space_type} function mean: ${row.mean_rating}; ${row.trials} trials, ${row.participants} people, ${row.rooms} rooms` }),
      ];
    }
    else if (chart.type === 'line') marks = [Plot.line(plottedRows, { ...common, stroke: chart.series || sky, tip: true }), Plot.dot(plottedRows, { ...common, stroke: chart.series || sky, tip: true })];
    else if (chart.type === 'bar') {
      marks = [product.id === 'P2'
        ? Plot.rectY(rows, { x1: 'bin_left', x2: 'bin_right', y1: 0, y2: 'draw_count', fill: sky, tip: true })
        : Plot.barY(rows, { ...common, fill: seriesInHeading ? sky : chart.series || sky, tip: true })];
      const observed = product.id === 'P2' ? rows.find(row => numeric(row.observed))?.observed : null;
      if (numeric(observed)) {
        const top = Math.max(0, ...rows.map(row => numeric(row[chart.y]) ? row[chart.y] as number : 0));
        marks.push(Plot.ruleX([observed], { stroke: lamp, strokeWidth: 2, title: `Observed ${observed}` }));
        marks.push(Plot.text([{ observed, top }], { x: 'observed', y: 'top', text: () => 'Observed', dy: -8, fill: lamp, fontWeight: 700 }));
      }
    }
    else if (chart.type === 'heatmap') marks = [Plot.cell(chart.series ? rows.filter(row => row[chart.series!] != null) : rows, { ...common, fill: chart.series || chart.y, tip: true })];
    else marks = [Plot.dot(rows, { ...common, fill: chart.series || sky, stroke: ink, tip: true, r: 4 })];
    const xValues = plottedRows.map(row => row[chart.x]).filter(numeric);
    const yValues = plottedRows.map(row => row[chart.y]).filter(numeric);
    const signedX = xValues.length > 0 && Math.min(...xValues) >= -1 && Math.max(...xValues) <= 1 && /valence|arousal/i.test(chart.x);
    const signedY = yValues.length > 0 && Math.min(...yValues) >= -1 && Math.max(...yValues) <= 1 && /valence|arousal|rating|comfort|rho/i.test(chart.y);
    const plot = Plot.plot({
      width: plotWidth, height: plotHeight, marginLeft, marginBottom, marginRight: 28, marginTop,
      style: { background: 'transparent', color: ink, fontFamily: 'Public Sans, sans-serif', fontSize: '12px' },
      x: functionRatings
        ? { label: null, domain: [-.5, categories.length - .5], ticks: categories.map((_, index) => index), tickFormat: (value: number) => categories[value] || '', tickRotate: -45 }
        : { label: null, grid: true, domain: signedX ? [-1, 1] : undefined, ticks: signedX ? [-1, 0, 1] : undefined, tickFormat: xCategories.length ? axisTick : undefined, tickRotate: xCategories.length > 3 ? -45 : undefined },
      y: { label: null, grid: true, domain: signedY ? [-1, 1] : undefined, ticks: signedY ? [-1, 0, 1] : undefined, tickFormat: yCategories.length ? axisTick : undefined },
      color: color && product.id === 'P3' ? { ...color, domain: [...new Set(colorValues.map(String))] } : color,
      marks, caption: facet ? `${product.id}: ${facet}` : product.id,
    });
    plot.setAttribute('aria-label', `${product.question}${facet ? ` — ${facet}` : ''}. A complete data table follows.`);
    const plotSvgs = plot instanceof SVGSVGElement ? [plot] : [...plot.querySelectorAll('svg')];
    // Every exported mark has a complete table alternative below the figure.
    // Observable Plot labels its internal mark groups, which are not valid
    // accessible names for those SVG groups; keep the drawings decorative.
    plotSvgs.forEach(item => { item.setAttribute('aria-hidden', 'true'); item.setAttribute('focusable', 'false'); });
    const svg = plotSvgs.find(item => Number(item.getAttribute('width')) === plotWidth && Number(item.getAttribute('height')) === plotHeight);
    svg?.setAttribute('data-main-plot', 'true');
    element.append(plot);
    setContentOverflow(element.scrollWidth > element.clientWidth + 4);
    return () => plot.remove();
  }, [product, rows, facet, seriesInHeading, width, theme, plotWidth, plotHeight, marginLeft, marginBottom, marginTop]);
  return <div className="plot-view"><div className="plot-axis-descriptors"><span><strong>Y</strong> {product.id === 'P3' ? 'Mean absolute error (constructed fused-coordinate units)' : `${chart.y_label}${chart.y_unit ? ` (${chart.y_unit})` : ''}`}</span><span><strong>X</strong> {chart.x_label}{chart.x_unit ? ` (${chart.x_unit})` : ''}</span></div>{scrollable && <p className="plot-scroll-hint">Scroll the chart horizontally to read every category.</p>}<div className="research-plot" ref={ref} role={scrollable ? 'region' : undefined} aria-label={scrollable ? `${product.id}${facet ? ` ${facet}` : ''} scrollable chart` : undefined} tabIndex={scrollable ? 0 : undefined} /></div>;
}

function ResearchStages({ rows }: { rows: Row[] }) {
  const stages = [...rows].sort((a, b) => Number(a.order) - Number(b.order));
  return <ol className="research-stages" aria-label="Research training stages">
    {stages.map(row => <li key={String(row.stage)}><span className="research-stage-name">{readable(String(row.stage))}</span><strong>{encoded(row.count)} <small>{String(row.unit)}</small></strong><span className="research-stage-scope">{readable(String(row.scope))}</span></li>)}
  </ol>;
}

export default function ResearchChart({ product }: { product: AnalysisProduct }) {
  const { chart } = product;
  const [tableOpen, setTableOpen] = useState(chart.type === 'table');
  const density = (product.id === 'R3' || product.id === 'B8') && chart.rows.some(row => row.kind === 'density_grid');
  const columns = tableOpen ? [...new Set(chart.rows.flatMap(row => Object.keys(row)))] : [];
  const separateSeries = chart.type === 'bar' && Boolean(chart.series);
  const dimensions = [chart.facet, separateSeries ? chart.series : null].filter((value): value is string => Boolean(value));
  const groups = dimensions.length ? [...new Set(chart.rows.map(row => dimensions.map(key => String(row[key] ?? 'Unavailable')).join('\u001f')))].map(key => {
    const values = key.split('\u001f');
    return { key, label: dimensions.map((dimension, index) => `${readable(dimension)} ${values[index]}`).join(' · '), rows: chart.rows.filter(row => dimensions.every((dimension, index) => String(row[dimension] ?? 'Unavailable') === values[index])) };
  }) : [{ key: '', label: '', rows: chart.rows }];
  return <figure className="research-figure" id={`analysis-${product.id}`} aria-labelledby={`analysis-title-${product.id}`}>
    <div className="research-figure-head"><span className="eyebrow">{product.id} · {product.status === 'available' ? 'Current analysis' : 'Unavailable analysis'}</span><h3 id={`analysis-title-${product.id}`}>{product.question}</h3><p>{product.takeaway}</p></div>
    {product.status === 'available' && chart.rows.length ? <>
      {density ? <DensityFigure product={product} /> : product.id === 'P5' ? <ResearchStages rows={chart.rows} /> : chart.type === 'table' ? null : groups.map(group => <div key={group.key}>{group.label && <h4>{group.label}</h4>}<PlotView product={product} rows={group.rows} facet={group.label || undefined} seriesInHeading={separateSeries} /></div>)}
      {product.id === 'S3' && <p className="figure-note">Each line follows one studied room across spatial attributes. The exported display scale runs from 0 to 1 within each experiment and attribute; 0.5 marks a constant attribute. Original values and units follow in the table.</p>}
      {product.id === 'R6' && <p className="figure-note">Points show observed ratings with recorded illuminance. Within-person E2 Day minus Night summaries have no illuminance coordinate and are available in the table.</p>}
      {product.id === 'R7' && <p className="figure-note">Blue dots show {chart.rows.filter(row => row.kind === 'observed_trial').length} individual ratings; larger amber diamonds show {chart.rows.filter(row => row.kind === 'function_mean').length} exported function means. Dots are spread horizontally only to reveal repeated observations; space types are categories, not a numeric axis. Mean-row trial, person and room counts remain in the table.</p>}
      {product.id === 'P2' && <p className="figure-note">Each panel shows its own prespecified null-control draws. The amber rule marks the exported observed metric for that control; its interval and draw count are in the table.</p>}
      {product.id === 'P3' && <p className="figure-note">Lines show only rows with a training-room count. Held-out room folds and self-report-only comparators remain in the table because they have no training-room position; self-report errors use the source rating scale and must not be joined to the fused curve.</p>}
      {product.id === 'P5' && <p className="figure-note">Ordered stages retain their exported counts and units. Trial and room counts describe different stages and are not additive.</p>}
      {chart.series && !density && product.id !== 'R7' && <p className="figure-note">{separateSeries ? `Separate panels show ${readable(chart.series).toLowerCase()}; bars are not stacked or pooled.` : `Colour encodes ${readable(chart.series).toLowerCase()}; position carries the plotted values.`}</p>}
      <details className="chart-data" open={tableOpen} onToggle={event => setTableOpen(event.currentTarget.open)}><summary>Read the plotted data ({chart.rows.length} rows)</summary>{tableOpen && <div className="table-wrap"><table className="data-table"><caption>{product.question} · exported chart rows</caption><thead><tr>{columns.map(key => <th scope="col" key={key}>{readable(key)}{product.units[key] ? ` (${product.units[key]})` : ''}</th>)}</tr></thead><tbody>{chart.rows.map((row, index) => <tr key={index}>{columns.map(key => <td key={key}>{product.id === 'R7' && key === 'kind' ? row[key] === 'observed_trial' ? 'Individual rating (observed_trial)' : row[key] === 'function_mean' ? 'Function mean (function_mean)' : encoded(row[key]) : encoded(row[key])}</td>)}</tr>)}</tbody></table></div>}</details>
    </> : <p className="figure-empty">{product.availability_reason || 'No eligible chart rows were exported for this question.'}</p>}
    <figcaption><span>Method: {product.method}</span><span>Contributing records: {countLabel(product.counts.trials, 'trial', 'trials')} · {countLabel(product.counts.participants, 'person', 'people')} · {countLabel(product.counts.rooms, 'room', 'rooms')}.</span>{product.caveats.length > 0 && <span>Limit: {product.caveats.join(' ')}</span>}<span>Method {product.provenance.method_version} · generated {product.provenance.generated_at_utc}.</span></figcaption>
  </figure>;
}
