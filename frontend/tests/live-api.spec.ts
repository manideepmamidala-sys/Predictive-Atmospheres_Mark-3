import { expect, test } from '@playwright/test';

test.skip(process.env.PA_LIVE_API_TEST !== '1', 'Run with PA_LIVE_API_TEST=1 and the fitted backend service.');

test('real E3 preset predicts fused response and generates closest-score candidates', async ({ page }) => {
  test.setTimeout(90_000);
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('/studio');
  await expect(page.getByText('Live model: ready for experimental requests')).toBeVisible();
  const preset = page.getByRole('combobox', { name: 'Studied-room preset' });
  await expect(preset.locator('option')).not.toHaveCount(1);
  await preset.selectOption({ index: 1 });
  const predictionResponse = page.waitForResponse(response => response.url().endsWith('/v1/predict'));
  await page.getByRole('button', { name: 'Predict fused response' }).click();
  const forward = await (await predictionResponse).json();
  expect(forward).toMatchObject({ schema_version: '1.0.0', status: 'ok' });
  expect(forward.prediction.neuro_score).toBeGreaterThanOrEqual(0);
  expect(forward.prediction.neuro_score).toBeLessThanOrEqual(1);
  await expect(page.getByText(/Closest studied-room reference/)).toBeVisible();
  const generationResponse = page.waitForResponse(response => response.url().endsWith('/v1/optimize'));
  await page.getByRole('button', { name: 'Generate closest-score rooms' }).click();
  const generated = await (await generationResponse).json();
  expect(generated).toMatchObject({ schema_version: '1.0.0' });
  if (generated.status === 'ok') {
    expect(generated.candidates.length).toBeGreaterThan(0);
    expect(generated.candidates[0].absolute_difference).toBeLessThanOrEqual(generated.candidates.at(-1).absolute_difference);
    expect(generated.candidates[0].achieved_score).toBeCloseTo(generated.candidates[0].prediction.neuro_score * 100, 6);
    const details = page.locator('.candidate-parameters');
    await expect(details).toHaveCount(generated.candidates.length);
    await expect(details.first()).toHaveAttribute('open', '');
    for (const [index, candidate] of generated.candidates.entries()) {
      if (index) await details.nth(index).locator('summary').click();
      await expect(details.nth(index).locator('dt')).toHaveCount(15);
      await expect(details.nth(index)).toContainText(`${candidate.room.length} m`);
      await expect(details.nth(index)).toContainText(candidate.room.space_type);
      await expect(details.nth(index)).toContainText('Fused valence');
    }
    expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(390);
  } else await expect(page.getByText('No feasible candidate')).toBeVisible();
});
