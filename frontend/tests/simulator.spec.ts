import { expect, test } from '@playwright/test';
import { useSyntheticResearch } from './fixtures';

const ready = { schema_version: '1.0.0', data_manifest_sha256: 'synthetic', artifact_version: 'synthetic', model_status: 'baseline_only', ready: true, limitations: [] };
const prediction = { valence: .1, arousal: .2, raw_valence: .1, raw_arousal: .2, projected: false, neuro_score: .8 };
const support = { status: 'within_studied_support', nearest_room_id: 'Rm_021', standardized_distance: .2, threshold: 2 };
const candidateRoom = { length: 7, width: 6, height: 3, num_doors: 1, door_area: 2, num_windows: 2, window_area: 4, daylight_factor: 3, illuminance: 210, cct: 3300, walkable_floor_area: 38, day_or_night: 'Day', space_type: 'Bedroom' };

test('fused forward and closest-score generation preserve target, locks, ranges and score scale', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await useSyntheticResearch(page);
  await page.route('**/v1/meta', route => route.fulfill({ json: ready }));
  await page.route('**/v1/predict', route => {
    const body = route.request().postDataJSON();
    expect(body.target).toEqual({ valence: .3, arousal: -.2 });
    expect(body.room).toEqual(candidateRoom);
    return route.fulfill({ json: { schema_version: '1.0.0', status: 'ok', model_status: 'baseline_only', prediction, support, limitations: ['Synthetic baseline only'] } });
  });
  await page.route('**/v1/optimize', route => {
    const body = route.request().postDataJSON();
    expect(body.target).toEqual({ valence: .3, arousal: -.2 });
    expect(body.requested_score).toBe(65);
    expect(body.base_room).toEqual(candidateRoom);
    expect(body.locked_fields).toContain('length');
    expect(body.allowed_ranges.width).toEqual({ minimum: 5, maximum: 7 });
    return route.fulfill({ json: { schema_version: '1.0.0', status: 'ok', model_status: 'baseline_only', samples_evaluated: 3, reason: null, limitations: ['Synthetic baseline only'], candidates: [
      { room: candidateRoom, prediction, support, requested_score: 65, achieved_score: 80, absolute_difference: 15 },
      { room: { ...candidateRoom, width: 6.5, illuminance: 240, space_type: 'Classroom' }, prediction: { ...prediction, valence: -.1, arousal: .4, neuro_score: .9 }, support, requested_score: 65, achieved_score: 90, absolute_difference: 25 },
    ] } });
  });
  await page.goto('/studio');
  await expect(page.getByText('Baseline-only model')).toBeVisible();
  await page.getByRole('combobox', { name: 'Studied-room preset' }).selectOption('Rm_021');
  await expect(page.getByLabel('Length', { exact: true })).toHaveValue('7');
  await expect(page.getByRole('img', { name: /Schematic room volume/ })).toBeVisible();
  await page.getByLabel('Target valence').fill('0.3');
  await page.getByLabel('Target arousal').fill('-0.2');
  await page.getByRole('button', { name: 'Predict fused response' }).click();
  await expect(page.getByText('80.0', { exact: true })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'What the model returned' })).toBeFocused();
  await expect(page.getByRole('heading', { name: 'What the model returned' })).toBeInViewport();
  await expect(page.getByText('Closest studied-room reference: Rm_021')).toBeVisible();
  await expect(page.getByText(/not an image of the entered or generated room/)).toBeVisible();
  await page.getByLabel('Target arousal').fill('-0.1');
  await expect(page.getByText('80.0', { exact: true })).toHaveCount(0);
  await page.getByLabel('Target arousal').fill('-0.2');
  await page.getByLabel('Length', { exact: true }).locator('..').locator('..').getByRole('checkbox').check();
  await page.locator('summary').filter({ hasText: 'Allowed ranges for generation' }).click();
  await page.getByRole('spinbutton', { name: 'Width range minimum' }).fill('5');
  await page.getByRole('spinbutton', { name: 'Width range maximum' }).fill('7');
  await page.getByRole('button', { name: 'Generate closest-score rooms' }).click();
  await expect(page.getByRole('row', { name: /7.00 × 6.00 × 3.00/ })).toContainText('15');
  await expect(page.getByText('Requested score:')).toBeVisible();
  const candidates = page.locator('.candidate-parameters');
  await expect(candidates).toHaveCount(2);
  await expect(candidates.first()).toHaveAttribute('open', '');
  await expect(candidates.first().locator('dt')).toHaveCount(15);
  await expect(candidates.first()).toContainText('210 lux');
  await expect(candidates.first()).toContainText('Bedroom');
  await candidates.nth(1).locator('summary').click();
  await expect(candidates.nth(1)).toContainText('6.5 m');
  await expect(candidates.nth(1)).toContainText('240 lux');
  await expect(candidates.nth(1)).toContainText('Classroom');
  await expect(candidates.nth(1)).toContainText('Fused valence');
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(390);
});

test('populated generation stays within the mobile viewport in both themes', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await useSyntheticResearch(page);
  await page.route('**/v1/meta', route => route.fulfill({ json: ready }));
  await page.route('**/v1/optimize', route => route.fulfill({ json: { schema_version: '1.0.0', status: 'ok', model_status: 'baseline_only', samples_evaluated: 2, reason: null, limitations: [], candidates: [
    { room: candidateRoom, prediction, support, requested_score: 65, achieved_score: 80, absolute_difference: 15 },
    { room: { ...candidateRoom, width: 6.5 }, prediction, support, requested_score: 65, achieved_score: 80, absolute_difference: 15 },
  ] } }));
  for (const theme of ['Light', 'Dark'] as const) {
    await page.goto('/studio');
    await page.getByRole('combobox', { name: 'Appearance' }).selectOption(theme.toLowerCase());
    await page.getByRole('combobox', { name: 'Studied-room preset' }).selectOption('Rm_021');
    await page.getByRole('button', { name: 'Generate closest-score rooms' }).click();
    await expect(page.locator('.candidate-parameters')).toHaveCount(2);
    await page.locator('.candidate-parameters').nth(1).locator('summary').click();
    expect(await page.evaluate(() => document.documentElement.scrollWidth), `${theme} populated Studio should fit`).toBeLessThanOrEqual(390);
    const ranking = page.locator('.studio-result .table-wrap');
    expect(await ranking.evaluate(element => element.scrollWidth)).toBeGreaterThan(await ranking.evaluate(element => element.clientWidth));
  }
});

test('target plane is keyboard controlled and input wheel does not change a value', async ({ page }) => {
  await useSyntheticResearch(page);
  await page.route('**/v1/meta', route => route.fulfill({ json: ready }));
  await page.goto('/studio');
  const marker = page.getByRole('button', { name: /Emotional target on valence and arousal plane/ });
  await marker.focus(); await page.keyboard.press('ArrowRight');
  await expect(page.getByLabel('Target valence')).toHaveValue('0.05');
  await page.keyboard.press('Shift+ArrowUp');
  await expect(page.getByLabel('Target arousal')).toHaveValue('0.01');
  await page.keyboard.press('Home');
  await expect(page.getByLabel('Target valence')).toHaveValue('0');
  const score = page.getByLabel('Requested Neuro-Score (0–100)');
  await score.focus();
  await score.hover();
  await page.mouse.wheel(0, 400);
  await expect(score).toHaveValue('65');
});

test('offline readiness is visible before submit and invalid candidates are rejected', async ({ page }) => {
  await useSyntheticResearch(page);
  await page.route('**/v1/meta', route => route.abort());
  await page.goto('/studio');
  await expect(page.getByText('Live model: offline or unavailable')).toBeVisible();
  await expect(page.getByRole('button', { name: 'Predict fused response' })).toBeDisabled();
  await expect(page.getByRole('button', { name: 'Generate closest-score rooms' })).toBeDisabled();
  await page.unroute('**/v1/meta');
  await page.route('**/v1/meta', route => route.fulfill({ json: ready }));
  await page.getByRole('button', { name: 'Check again' }).click();
  await page.getByRole('combobox', { name: 'Studied-room preset' }).selectOption('Rm_021');
  await page.getByLabel('Length', { exact: true }).locator('..').locator('..').getByRole('checkbox').check();
  await page.route('**/v1/optimize', route => route.fulfill({ json: { schema_version: '1.0.0', status: 'ok', model_status: 'baseline_only', samples_evaluated: 1, reason: null, limitations: [], candidates: [{ room: { ...candidateRoom, length: 8 }, prediction, support, requested_score: 65, achieved_score: 80, absolute_difference: 15 }] } }));
  await page.getByRole('button', { name: 'Generate closest-score rooms' }).click();
  await expect(page.getByRole('alert')).toContainText('did not preserve locked length');
  await expect(page.getByLabel('Length', { exact: true })).toHaveValue('7');
});

test('no feasible candidate keeps the request and explains the empty result', async ({ page }) => {
  await useSyntheticResearch(page);
  await page.route('**/v1/meta', route => route.fulfill({ json: ready }));
  await page.route('**/v1/optimize', route => route.fulfill({ json: { schema_version: '1.0.0', status: 'empty', model_status: 'baseline_only', samples_evaluated: 0, reason: 'No feasible room satisfies locked dimensions and ranges.', limitations: [], candidates: [] } }));
  await page.goto('/studio');
  await page.getByRole('combobox', { name: 'Studied-room preset' }).selectOption('Rm_021');
  await page.getByRole('button', { name: 'Generate closest-score rooms' }).click();
  await expect(page.getByText('No feasible candidate', { exact: true })).toBeVisible();
  await expect(page.getByText('No feasible room satisfies locked dimensions and ranges.')).toBeVisible();
  await expect(page.getByLabel('Requested Neuro-Score (0–100)')).toHaveValue('65');
});
