import { existsSync } from 'node:fs';
import { mkdir } from 'node:fs/promises';
import { resolve } from 'node:path';
import { expect, test } from '@playwright/test';

const results = resolve(import.meta.dirname, '../../artifacts/results');
const destination = resolve(import.meta.dirname, '../../docs/screenshots');
const routes = [
  { path: '/', slug: 'landing', heading: 'What if space could be read through experience?', analyses: 0 },
  { path: '/study', slug: 'study', heading: 'The Study', analyses: 4 },
  { path: '/rooms', slug: 'rooms', heading: 'Rooms & Experience', analyses: 10 },
  { path: '/body', slug: 'body', heading: 'Body & Experience', analyses: 8 },
  { path: '/prediction', slug: 'prediction', heading: 'Prediction & Findings', analyses: 5 },
  { path: '/studio', slug: 'studio', heading: 'Design Studio', analyses: 0 },
  { path: '/explore', slug: 'explore', heading: 'Data Explorer', analyses: 0 },
  { path: '/methods', slug: 'methods', heading: 'Methods & Research Context', analyses: 1 },
] as const;

test.skip(!existsSync(resolve(results, 'bundle.json')) ||
  !existsSync(resolve(results, 'analysis/index.json')),
  'Final captures require the generated research bundle and complete analysis catalogue.');

test('capture eight real-data routes at both viewports and in both themes', async ({ page }) => {
  test.setTimeout(10 * 60_000);
  await mkdir(destination, { recursive: true });
  for (const viewport of [
    { name: 'desktop', width: 1440, height: 900 },
    { name: 'mobile', width: 390, height: 844 },
  ] as const) {
    await page.setViewportSize({ width: viewport.width, height: viewport.height });
    for (const theme of ['light', 'dark'] as const) {
      for (const route of routes) {
        await page.goto(route.path);
        await page.getByRole('combobox', { name: 'Appearance' }).selectOption(theme);
        await expect(page.getByRole('heading', { name: route.heading, exact: true })).toBeVisible();
        if (route.analyses) {
          await expect(page.locator('.analysis-row')).toHaveCount(route.analyses);
          await expect(page.locator('.analysis-row .research-figure')).toHaveCount(route.analyses);
        }
        await expect(page.getByText('Loading chart…')).toHaveCount(0);
        await expect(page.getByRole('alert').filter({ hasText: 'Analysis catalogue unavailable' })).toHaveCount(0);
        await page.evaluate(async () => {
          await document.fonts.ready;
          await new Promise<void>(resolve => requestAnimationFrame(() => requestAnimationFrame(() => resolve())));
        });
        await page.screenshot({
          path: resolve(destination, `${route.slug}-${theme}-${viewport.name}.png`),
          animations: 'disabled',
        });
        await page.screenshot({
          path: resolve(destination, `${route.slug}-${theme}-${viewport.name}-full.png`),
          animations: 'disabled',
          fullPage: true,
        });
      }
    }
  }
});

test('capture populated live Design Studio prediction and search', async ({ page }) => {
  test.skip(process.env.PA_LIVE_API_TEST !== '1', 'Requires a ready fitted API on port 8000.');
  test.setTimeout(6 * 60_000);
  await mkdir(destination, { recursive: true });
  for (const viewport of [
    { name: 'desktop', width: 1440, height: 900 },
    { name: 'mobile', width: 390, height: 844 },
  ] as const) {
    await page.setViewportSize({ width: viewport.width, height: viewport.height });
    for (const theme of ['light', 'dark'] as const) {
      await page.goto('/studio');
      await page.getByRole('combobox', { name: 'Appearance' }).selectOption(theme);
      await expect(page.getByText('Live model: ready for experimental requests')).toBeVisible();
      await expect(page.getByText('Baseline-only model')).toBeVisible();
      const preset = page.getByRole('combobox', { name: 'Studied-room preset' });
      await expect(preset.locator('option')).not.toHaveCount(1);
      await preset.selectOption({ index: 1 });
      const predictionResponse = page.waitForResponse(response => response.url().endsWith('/v1/predict'));
      await page.getByRole('button', { name: 'Predict fused response' }).click();
      expect((await (await predictionResponse).json()).status).toBe('ok');
      await expect(page.getByText(/Prediction ready\. Neuro-Score/)).toBeVisible();
      await page.screenshot({ path: resolve(destination, `studio-live-prediction-${theme}-${viewport.name}.png`), animations: 'disabled' });
      await page.screenshot({ path: resolve(destination, `studio-live-prediction-${theme}-${viewport.name}-full.png`), animations: 'disabled', fullPage: true });

      const generationResponse = page.waitForResponse(response => response.url().endsWith('/v1/optimize'));
      await page.getByRole('button', { name: 'Generate closest-score rooms' }).click();
      const generated = await (await generationResponse).json();
      expect(generated.status).toBe('ok');
      expect(generated.candidates.length).toBeGreaterThan(0);
      await expect(page.getByText(/closest-score candidates ready/)).toBeVisible();
      await page.screenshot({ path: resolve(destination, `studio-live-generation-${theme}-${viewport.name}.png`), animations: 'disabled' });
      await page.screenshot({ path: resolve(destination, `studio-live-generation-${theme}-${viewport.name}-full.png`), animations: 'disabled', fullPage: true });
    }
  }
});
