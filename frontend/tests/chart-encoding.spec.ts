import { expect, test } from '@playwright/test';
import { SYNTHETIC_ANALYSIS_INDEX, syntheticProduct, useSyntheticAnalysis, useSyntheticResearch } from './fixtures';
import type { AnalysisId } from '../src/lib/research';

for (const theme of ['light', 'dark'] as const) {
  test(`signed affect plot has ticks, quadrants, keyboard points and full table in ${theme}`, async ({ page }) => {
    await useSyntheticResearch(page); await useSyntheticAnalysis(page);
    await page.goto('/body');
    await page.getByRole('combobox', { name: 'Appearance' }).selectOption(theme);
    const chart = page.locator('figure').filter({ hasText: 'Valence–arousal plane' });
    await expect(chart.getByText('activated · unpleasant')).toBeVisible();
    await expect(chart.getByText('calm · pleasant')).toBeVisible();
    await expect(chart.getByText('−1').first()).toBeVisible();
    await expect(chart.getByText('+1').first()).toBeVisible();
    await page.getByRole('combobox', { name: 'Component' }).selectOption('fused');
    await expect(chart.locator('circle.point')).toHaveCount(1);
    await chart.locator('circle.point').focus();
    await expect(chart.locator('circle.point')).toBeFocused();
    await expect(chart.getByRole('table', { name: /Accessible plotted valence and arousal values/ })).toContainText('P01, Rm_011');
  });
}

test('versioned chart shows question, encodings, counts, full data and unavailable reason', async ({ page }) => {
  await useSyntheticResearch(page);
  await page.route('**/research/analysis/*.json', route => {
    const id = route.request().url().split('/').pop()?.replace('.json', '') as AnalysisId;
    const product = syntheticProduct(id);
    if (id === 'B8') { product.status = 'unavailable'; product.availability_reason = 'Insufficient eligible complete pairs.'; product.chart.rows = []; }
    return route.fulfill({ json: product });
  });
  await page.route('**/research/analysis/index.json', route => route.fulfill({ json: { ...SYNTHETIC_ANALYSIS_INDEX, products: SYNTHETIC_ANALYSIS_INDEX.products.map(item => item.id === 'B8' ? { ...item, status: 'unavailable' } : item) } }));
  await page.goto('/body');
  const b1 = page.locator('#analysis-B1');
  await expect(b1.getByRole('heading', { name: 'Synthetic B1 question' })).toBeVisible();
  await expect(b1.getByText('2 trials · 1 person · 2 rooms')).toBeVisible();
  await expect(b1.locator('.research-plot svg')).toBeVisible();
  await b1.getByText('Read the plotted data (2 rows)').click();
  await expect(b1.getByRole('table')).toContainText('X Value (unit)');
  await expect(b1.getByRole('row')).toHaveCount(3);
  await expect(page.locator('#analysis-B8').getByText('Insufficient eligible complete pairs.')).toBeVisible();
});

test('branch counts and signed correlations retain separate experiments and missing cells', async ({ page }) => {
  await useSyntheticResearch(page);
  await page.route('**/research/analysis/*.json', route => {
    const id = route.request().url().split('/').pop()?.replace('.json', '') as AnalysisId;
    const product = syntheticProduct(id);
    if (id === 'S2') product.chart = {
      type: 'bar', x: 'branch', y: 'trials', facet: 'experiment', series: null,
      x_label: 'Eligibility branch', y_label: 'Trials',
      rows: [{ experiment: 1, branch: 'source', trials: 10 }, { experiment: 2, branch: 'source', trials: 20 }],
    };
    if (id === 'S4') product.chart = {
      type: 'heatmap', x: 'attribute_x', y: 'attribute_y', facet: 'experiment', series: 'spearman_rho',
      x_label: 'Attribute', y_label: 'Attribute',
      rows: [{ experiment: 1, attribute_x: 'length', attribute_y: 'width', spearman_rho: -0.8 }, { experiment: 1, attribute_x: 'height', attribute_y: 'width', spearman_rho: null }],
    };
    if (id === 'R7') product.chart = {
      type: 'scatter', x: 'space_type', y: 'mean_rating', facet: 'axis', series: 'kind',
      x_label: 'Recorded function', y_label: 'Observed report / function mean',
      rows: [
        { kind: 'function_mean', space_type: 'Bedroom', axis: 'valence', mean_rating: 0.2, trials: 1, participants: 1, rooms: 1, participant_id: null, room_id: null },
        { kind: 'observed_trial', space_type: 'Bedroom', axis: 'valence', mean_rating: 0.1, trials: 1, participants: 1, rooms: 1, participant_id: 'P01', room_id: 'Rm_021' },
        { kind: 'function_mean', space_type: 'Bedroom', axis: 'arousal', mean_rating: -0.3, trials: 1, participants: 1, rooms: 1, participant_id: null, room_id: null },
        { kind: 'observed_trial', space_type: 'Bedroom', axis: 'arousal', mean_rating: -0.4, trials: 1, participants: 1, rooms: 1, participant_id: 'P01', room_id: 'Rm_021' },
      ],
    };
    if (id === 'P2') product.chart = {
      type: 'bar', x: 'bin_center', y: 'draw_count', facet: 'control',
      x_label: 'Null metric', y_label: 'Draws',
      rows: [{ control: 'ratings shuffle', bin_left: 0.05, bin_center: 0.1, bin_right: 0.15, draw_count: 20, observed: 0.35 }, { control: 'spatial shuffle', bin_left: 0.15, bin_center: 0.2, bin_right: 0.25, draw_count: 18, observed: 0.4 }],
    };
    if (id === 'R3') product.chart = {
      type: 'heatmap', x: 'valence', y: 'arousal', series: 'density', facet: 'experiment',
      x_label: 'Valence', y_label: 'Arousal',
      rows: [{ experiment: 2, kind: 'density_grid', valence: 0, arousal: 0, density: 1 }, { experiment: 2, kind: 'target_vector', valence: 0, arousal: 0, density: null, source_valence: 0, source_arousal: 0, target_valence: 0.2, target_arousal: -0.1 }],
    };
    return route.fulfill({ json: product });
  });
  await page.route('**/research/analysis/index.json', route => route.fulfill({ json: SYNTHETIC_ANALYSIS_INDEX }));
  await page.goto('/study');
  const branches = page.locator('#analysis-S2');
  await expect(branches.getByRole('heading', { name: 'Experiment 1' })).toBeVisible();
  await expect(branches.getByRole('heading', { name: 'Experiment 2' })).toBeVisible();
  await expect(branches.locator('.research-plot svg')).toHaveCount(2);
  await page.goto('/rooms');
  const correlations = page.locator('#analysis-S4');
  await expect(correlations.getByRole('heading', { name: 'Experiment 1' })).toBeVisible();
  await correlations.getByText('Read the plotted data (2 rows)').click();
  await expect(correlations.getByRole('table')).toContainText('Unavailable');
  await expect(correlations.locator('.research-plot svg').last()).toBeVisible();
  const functionRatings = page.locator('#analysis-R7');
  await expect(functionRatings.getByRole('heading', { name: 'Axis valence' })).toBeVisible();
  await expect(functionRatings.getByRole('heading', { name: 'Axis arousal' })).toBeVisible();
  await expect(functionRatings.locator('.research-plot svg')).toHaveCount(2);
  await expect(functionRatings.locator('.r7-observations')).toHaveCount(2);
  await expect(functionRatings.locator('.r7-means')).toHaveCount(2);
  await expect(functionRatings.getByText(/Blue dots show 2 individual ratings; larger amber diamonds show 2 exported function means/)).toBeVisible();
  await functionRatings.getByText('Read the plotted data (4 rows)').click();
  await expect(functionRatings.getByRole('table')).toContainText('Individual rating (observed_trial)');
  await expect(functionRatings.getByRole('table')).toContainText('Function mean (function_mean)');
  const density = page.locator('#analysis-R3');
  await density.getByText('Read the plotted data (2 rows)').click();
  await expect(density.getByRole('columnheader', { name: 'Target Valence' })).toBeVisible();
  await expect(density.getByRole('table')).toContainText('Unavailable');
  await page.goto('/prediction');
  const nulls = page.locator('#analysis-P2');
  await expect(nulls.getByRole('heading', { name: 'Control ratings shuffle' })).toBeVisible();
  await expect(nulls.getByRole('heading', { name: 'Control spatial shuffle' })).toBeVisible();
  await expect(nulls.locator('.research-plot svg text').filter({ hasText: 'Observed' })).toHaveCount(2);
});
