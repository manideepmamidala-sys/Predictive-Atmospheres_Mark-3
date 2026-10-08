import { expect, test } from '@playwright/test';
import { useSyntheticResearch } from './fixtures';

async function fillGeometry(page: import('@playwright/test').Page) {
  await page.getByLabel('Length').fill('6');
  await page.getByLabel('Width').fill('5');
  await page.getByLabel('Height').fill('3');
}

test('typed prediction and optimization preserve user target and show support', async ({ page }) => {
  await useSyntheticResearch(page);
  await page.route('**/v1/meta', route => route.fulfill({ json: { schema_version: '1.0.0', data_manifest_sha256: 'synthetic', artifact_version: 'synthetic', model_status: 'weak', ready: true, limitations: [] } }));
  await page.route('**/v1/predict', async route => {
    const body = route.request().postDataJSON();
    expect(body.target).toEqual({ valence: 0.3, arousal: -0.2 });
    expect(body.room).toMatchObject({ length: 6, width: 5, height: 3, window_area: 2 });
    await route.fulfill({ json: { schema_version: '1.0.0', status: 'ok', model_status: 'weak', prediction: { valence: 0.1, arousal: 0.2, raw_valence: 0.1, raw_arousal: 0.2, projected: false, neuro_score: 0.8 }, support: { status: 'within_studied_support', nearest_room_id: 'Rm_011', standardized_distance: 0.3, threshold: 2 }, limitations: ['Weak against baseline'] } });
  });
  await page.route('**/v1/optimize', async route => {
    const body = route.request().postDataJSON();
    expect(body.target).toEqual({ valence: 0.3, arousal: -0.2 });
    expect(body.space_type).toBe('Bedroom');
    await route.fulfill({ json: { schema_version: '1.0.0', status: 'ok', model_status: 'weak', samples_evaluated: 3, reason: null, limitations: ['Experimental'], candidates: [{ room: { length: 6, width: 5, height: 3 }, prediction: { valence: 0.1, arousal: 0.1, raw_valence: 0.1, raw_arousal: 0.1, projected: false, neuro_score: 0.7 }, support: { status: 'within_studied_support', nearest_room_id: 'Rm_021', standardized_distance: 0.2, threshold: 2 } }] } });
  });
  await page.goto('/simulator');
  await fillGeometry(page);
  await expect(page.getByRole('img', { name: /Schematic room volume/ })).toBeVisible();
  const rotate = page.getByRole('slider', { name: 'Rotate schematic' });
  await rotate.focus(); await page.keyboard.press('ArrowRight');
  await expect(rotate).toHaveValue('36');
  await page.getByLabel('Total window area').fill('2');
  await page.getByLabel('Space type').selectOption('Bedroom');
  await page.getByLabel('Target valence').fill('0.3');
  await page.getByLabel('Target arousal').fill('-0.2');
  await page.getByRole('button', { name: 'Predict response' }).click();
  await expect(page.getByText('Nearest studied room: Rm_011')).toBeVisible();
  await expect(page.getByText('Weak against baseline')).toBeVisible();
  await page.getByRole('button', { name: 'Suggest rooms' }).click();
  await expect(page.getByRole('row', { name: /Rm_021/ })).toContainText('6.00 × 5.00 × 3.00');
});

test('offline and unavailable service errors preserve form inputs', async ({ page }) => {
  await useSyntheticResearch(page);
  await page.route('**/v1/meta', route => route.abort());
  await page.route('**/v1/predict', route => route.abort());
  await page.goto('/simulator');
  await fillGeometry(page);
  await page.getByLabel('Target valence').fill('0.3');
  await page.getByLabel('Target arousal').fill('-0.2');
  await page.getByRole('button', { name: 'Predict response' }).click();
  await expect(page.getByRole('alert')).toContainText('could not be reached');
  await expect(page.getByLabel('Length')).toHaveValue('6');
  await page.unroute('**/v1/predict');
  await page.route('**/v1/predict', route => route.fulfill({ status: 503, json: { error: { code: 'model_unavailable', message: 'Fitted artifact unavailable' } } }));
  await page.getByRole('button', { name: 'Predict response' }).click();
  await expect(page.getByRole('alert')).toContainText('Fitted artifact unavailable');
  await expect(page.getByLabel('Width')).toHaveValue('5');
});
