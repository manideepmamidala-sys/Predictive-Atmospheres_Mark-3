import { expect, test } from '@playwright/test';

test.skip(process.env.PA_LIVE_API_TEST !== '1', 'Run with PA_LIVE_API_TEST=1 and the fitted backend service.');

test('real fitted service responds through the room simulator', async ({ page }) => {
  test.setTimeout(60_000);
  await page.goto('/simulator');
  await expect(page.getByText(/Live service: ready \(not_better_than_baseline\)/)).toBeVisible();
  await expect(page.getByText(/Held-out error is not better than the reported baseline/)).toBeVisible();
  await page.getByLabel('Length').fill('6');
  await page.getByLabel('Width').fill('5');
  await page.getByLabel('Height').fill('3');
  await page.getByLabel('Target valence').fill('0.3');
  await page.getByLabel('Target arousal').fill('-0.2');

  const predictionResponse = page.waitForResponse(response => response.url().endsWith('/v1/predict'));
  await page.getByRole('button', { name: 'Predict response' }).click();
  const prediction = await (await predictionResponse).json();
  expect(prediction).toMatchObject({ schema_version: '1.0.0', status: 'ok', model_status: 'not_better_than_baseline' });
  expect(Number.isFinite(prediction.prediction.valence)).toBe(true);
  await expect(page.getByText(/Predicted valence:/)).toBeVisible();
  await expect(page.getByText(/Studied support:/)).toContainText(prediction.support.status);

  const optimizationResponse = page.waitForResponse(response => response.url().endsWith('/v1/optimize'));
  await page.getByRole('button', { name: 'Suggest rooms' }).click();
  const optimization = await (await optimizationResponse).json();
  expect(optimization).toMatchObject({ schema_version: '1.0.0', model_status: 'not_better_than_baseline' });
  expect(optimization.candidates.length).toBeGreaterThan(0);
  const first = optimization.candidates[0].room;
  await expect(page.getByRole('table').last().locator('tbody tr').first()).toContainText(`${first.length.toFixed(2)} × ${first.width.toFixed(2)} × ${first.height.toFixed(2)}`);
});
