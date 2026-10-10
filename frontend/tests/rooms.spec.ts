import { expect, test } from '@playwright/test';
import { useSyntheticAnalysis, useSyntheticResearch } from './fixtures';

test('source room gallery filters in URL and lazy panorama pans with keyboard', async ({ page }) => {
  await useSyntheticResearch(page); await useSyntheticAnalysis(page);
  await page.goto('/rooms');
  await expect(page.locator('.room-tile')).toHaveCount(30);
  await page.getByRole('combobox', { name: 'Experiment' }).selectOption('2');
  await expect(page).toHaveURL(/experiment=2/);
  await expect(page.locator('.room-tile')).toHaveCount(10);
  await page.getByRole('button', { name: /Rm_011/ }).click();
  await expect(page).toHaveURL(/room=Rm_011/);
  await expect(page.getByRole('heading', { name: 'Rm_011' })).toBeVisible();
  await page.getByRole('button', { name: 'Explore panorama' }).click();
  const slider = page.getByRole('slider', { name: 'Pan Rm_011 view' });
  await expect(slider).toHaveValue('50');
  await slider.focus(); await page.keyboard.press('ArrowRight');
  await expect(slider).toHaveValue('51');
  await expect(page.getByRole('link', { name: /Open preserved source image/ })).toHaveAttribute('href', /Mark%2002_/);
  const preview = page.getByRole('img', { name: /Original study render preview for Rm_011/ });
  await expect(preview).toHaveJSProperty('complete', true);
  expect(await preview.evaluate(image => (image as HTMLImageElement).naturalWidth)).toBeGreaterThan(0);
  await page.getByRole('combobox', { name: 'Experiment' }).selectOption('3');
  await expect(page).not.toHaveURL(/room=Rm_011/);
  await expect(page.getByRole('heading', { name: 'Rm_021', exact: true })).toBeVisible();
});

test('mobile selected room detail is reachable immediately after selection', async ({ page }) => {
  await useSyntheticResearch(page);
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('/rooms');
  await page.getByRole('button', { name: /Rm_021/ }).click();
  await expect(page.getByRole('heading', { name: 'Rm_021' })).toBeVisible();
  await expect.poll(() => page.getByRole('heading', { name: 'Rm_021' }).evaluate(element => element.getBoundingClientRect().top)).toBeLessThan(844);
  await expect(page.getByRole('heading', { name: 'Rm_021' })).toBeFocused();
  await expect(page.getByRole('link', { name: /See Rm_021 trial records/ })).toHaveAttribute('href', '/explore?room=Rm_021');
});
