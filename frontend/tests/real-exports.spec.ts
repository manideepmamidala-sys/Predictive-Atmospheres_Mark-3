import { existsSync, readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { expect, test } from '@playwright/test';
import { ANALYSIS_IDS } from '../src/lib/research';

const source = resolve(import.meta.dirname, '../../artifacts/results/analysis');
const published = resolve(import.meta.dirname, '../public/research/analysis');
const available = existsSync(resolve(source, 'index.json'));
test.skip(!available, 'Complete current analysis catalogue is generated after the scientific gate.');

test('all 28 generated products retain complete IDs, provenance, route and valid chart encodings', () => {
  const index = JSON.parse(readFileSync(resolve(source, 'index.json'), 'utf8'));
  expect(index.schema_version).toBe('1.0.0');
  expect(index.method_version).toBe('1.2.0');
  expect(index.products.map((item: { id: string }) => item.id).sort()).toEqual([...ANALYSIS_IDS].sort());
  expect(readFileSync(resolve(published, 'index.json'), 'utf8')).toBe(JSON.stringify(index));
  for (const entry of index.products) {
    const product = JSON.parse(readFileSync(resolve(source, `${entry.id}.json`), 'utf8'));
    expect(readFileSync(resolve(published, `${entry.id}.json`))).toEqual(readFileSync(resolve(source, `${entry.id}.json`)));
    expect(product).toMatchObject({ schema_version: '1.0.0', id: entry.id, route: entry.route, status: entry.status });
    expect(product.provenance.approved_spec_sha256).toBe(index.approved_spec_sha256);
    expect(product.provenance.source_manifest_sha256).toMatch(/^[0-9a-f]{64}$/);
    expect(Object.keys(product.counts).sort()).toEqual(['participants', 'rooms', 'trials']);
    expect(product.question.length).toBeGreaterThan(0);
    expect(product.takeaway.length).toBeGreaterThan(0);
    if (entry.status === 'unavailable') expect(product.availability_reason).toBeTruthy();
    else for (const row of product.chart.rows) { expect(row).toHaveProperty(product.chart.x); expect(row).toHaveProperty(product.chart.y); }
  }
  const p3 = JSON.parse(readFileSync(resolve(source, 'P3.json'), 'utf8'));
  expect(p3.status).toBe('available');
  const comparators = p3.chart.rows.filter((row: { kind: string }) => row.kind === 'self_report_only_comparator');
  expect(comparators).toHaveLength(2);
  for (const [experiment, trials, participants, rooms] of [[2, 50, 5, 10], [3, 60, 6, 10]]) {
    expect(comparators.find((row: { experiment: number }) => row.experiment === experiment)).toMatchObject({
      target_type: 'original_signed_self_report', error_unit: 'signed source rating scale', trials, participants, rooms,
    });
  }
  const fusedRows = p3.chart.rows.filter((row: { kind: string }) => row.kind !== 'self_report_only_comparator');
  expect(fusedRows.length).toBeGreaterThan(0);
  for (const row of fusedRows) expect(row).toMatchObject({ error_unit: 'constructed-coordinate units', trials: 23, participants: 4, rooms: 10 });
});

test('eight published pages read real static products while live API is offline', async ({ page }) => {
  test.setTimeout(90_000);
  await page.route('**/v1/**', route => route.abort());
  const routeProducts: Record<string, string[]> = {
    '/study': ['S1', 'S2', 'S3', 'S5'],
    '/rooms': ['S4', 'R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8', 'R9'],
    '/body': ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8'],
    '/prediction': ['P1', 'P2', 'P3', 'P4', 'P5'],
    '/methods': ['Methods'],
  };
  for (const [path, heading] of [['/', 'What if space could be read through experience?'], ['/study', 'The Study'], ['/rooms', 'Rooms & Experience'], ['/body', 'Body & Experience'], ['/prediction', 'Prediction & Findings'], ['/studio', 'Design Studio'], ['/explore', 'Data Explorer'], ['/methods', 'Methods & Research Context']] as const) {
    await page.goto(path);
    await expect(page.getByRole('heading', { name: heading, exact: true })).toBeVisible();
    for (const id of routeProducts[path] || []) await expect(page.locator(`#analysis-${id}`)).toBeVisible();
    await expect(page.getByText('Analysis catalogue unavailable')).toHaveCount(0);
  }
  await page.goto('/studio');
  await expect(page.getByText('offline or unavailable')).toBeVisible();
});

test('real room profiles, affect densities and null controls use their dedicated encodings', async ({ page }) => {
  test.setTimeout(90_000);
  const product = (id: string) => JSON.parse(readFileSync(resolve(source, `${id}.json`), 'utf8'));
  for (const id of ['S3', 'R3', 'R7', 'B8', 'P2']) expect(product(id).status, `${id} should have source-derived rows`).toBe('available');
  expect(product('R7').chart.rows.filter((row: { kind: string }) => row.kind === 'observed_trial')).toHaveLength(120);
  expect(product('R7').chart.rows.filter((row: { kind: string }) => row.kind === 'function_mean')).toHaveLength(10);

  await page.goto('/study');
  const profile = page.locator('#analysis-S3');
  await expect(profile.locator('.research-plot svg[data-main-plot]')).toHaveCount(new Set(product('S3').chart.rows.map((row: { experiment: number }) => row.experiment)).size);
  await expect(profile.getByText(/Each line follows one studied room/)).toBeVisible();

  await page.goto('/rooms');
  const density = page.locator('#analysis-R3');
  await expect(density.locator('.density-panel')).toHaveCount(new Set(product('R3').chart.rows.map((row: { experiment: number; component?: string }) => `${row.experiment}|${row.component || 'all'}`)).size);
  await expect(density.getByText('Valence · signed coordinate').first()).toBeVisible();
  const functionRatings = page.locator('#analysis-R7');
  await expect(functionRatings.locator('.r7-observations')).toHaveCount(2);
  await expect(functionRatings.locator('.r7-means')).toHaveCount(2);
  await expect(functionRatings.getByText(/Blue dots show 120 individual ratings; larger amber diamonds show 10 exported function means/)).toBeVisible();

  await page.goto('/body');
  await expect(page.locator('#analysis-B8 .density-panel')).toHaveCount(new Set(product('B8').chart.rows.map((row: { experiment: number; component: string }) => `${row.experiment}|${row.component}`)).size);

  await page.goto('/prediction');
  await expect(page.locator('#analysis-P2 .research-plot svg text').filter({ hasText: 'Observed' })).toHaveCount(new Set(product('P2').chart.rows.map((row: { control: string }) => row.control)).size);
});

test('dense mobile research axes retain every category and readable plot units', async ({ page }) => {
  test.setTimeout(90_000);
  await page.setViewportSize({ width: 390, height: 844 });
  for (const [route, id, panel] of [['/study', 'S1', 0], ['/study', 'S3', 2], ['/rooms', 'S4', 2], ['/rooms', 'R2', 0]] as const) {
    await page.goto(route);
    const figure = page.locator(`#analysis-${id}`);
    const view = figure.locator('.plot-view').nth(panel);
    const plot = view.locator('.research-plot');
    await expect(plot.locator('svg[data-main-plot]')).toBeVisible();
    await expect(plot.locator('svg[data-main-plot]')).toHaveAttribute('aria-hidden', 'true');
    await expect(plot.locator('svg[data-main-plot]')).toHaveAttribute('focusable', 'false');
    await expect(view.getByText('Scroll the chart horizontally to read every category.')).toBeVisible();
    await expect(plot).toHaveAttribute('tabindex', '0');
    const widths = await plot.evaluate(element => ({ visible: element.clientWidth, full: element.scrollWidth }));
    expect(widths.full, `${id} should offer horizontal reading at 390px`).toBeGreaterThan(widths.visible + 100);
  }

  await page.goto('/rooms');
  const s4 = page.locator('#analysis-S4');
  await expect(s4.locator('.research-plot svg[data-main-plot]').last().getByText('Daylight Factor').first()).toBeVisible();
  await expect(s4.locator('.plot-axis-descriptors').first()).toContainText('Room attribute');
  await s4.locator('.chart-data summary').click();
  await expect(s4.locator('.chart-data table tbody tr').first()).toBeVisible();

  await page.goto('/prediction');
  const p5 = page.locator('#analysis-P5');
  await expect(p5.locator('.research-stages li')).toHaveCount(5);
  await expect(p5.locator('.research-stages')).toContainText('E3 Complete Raw Components And Reports');
  await expect(p5.locator('.research-stages')).toContainText('Independent E3 Room Groups');
  expect(await p5.evaluate(element => element.scrollWidth - element.clientWidth)).toBeLessThan(2);
  const p3 = page.locator('#analysis-P3');
  await expect(p3.locator('.plot-axis-descriptors')).toContainText('constructed fused-coordinate units');
  await expect(p3.locator('.research-plot')).toContainText('inner_selected');
  await expect(p3.locator('.research-plot')).toContainText('dummy_median');
  await expect(p3.locator('.research-plot')).not.toContainText('E2_self_report');
  await expect(p3.locator('.research-plot')).not.toContainText('random_forest');
  await expect(p3.locator('.chart-data')).toContainText('Read the plotted data (24 rows)');
});
