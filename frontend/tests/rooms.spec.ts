import { expect, test } from '@playwright/test';
import { useSyntheticResearch } from './fixtures';

test('real render gallery filters and pans with keyboard', async ({ page }) => {
  await page.goto('/rooms');
  await expect(page.locator('.room-card')).toHaveCount(30);
  await page.getByLabel('Experiment').selectOption('2');
  await expect(page.locator('.room-card')).toHaveCount(10);
  await page.getByRole('button', { name: 'Explore Rm_011' }).click();
  const slider = page.getByRole('slider', { name: 'Pan Rm_011 view' });
  await expect(slider).toHaveValue('50');
  await slider.focus(); await page.keyboard.press('ArrowRight');
  await expect(slider).toHaveValue('51');
  await expect(page.getByRole('link', { name: 'Open preserved source image in the repository' })).toHaveAttribute('href', /github\.com.*Rm_011\.jpg/);
  await expect(page.locator('.room-card img').first()).toHaveJSProperty('complete', true);
  expect(await page.locator('.room-card img').first().evaluate(image => (image as HTMLImageElement).naturalWidth)).toBeGreaterThan(0);
});

test('lighting and space filters use exported metadata and comparison keeps missing values', async ({ page }) => {
  await useSyntheticResearch(page);
  await page.goto('/rooms');
  await page.getByLabel('Recorded lighting').selectOption('Day');
  await expect(page.locator('.room-card')).toHaveCount(2);
  await page.getByLabel('Space type').selectOption('Bedroom');
  await expect(page.locator('.room-card')).toHaveCount(1);
  await page.getByLabel('Space type').selectOption('all');
  await page.locator('.room-card').first().getByRole('checkbox', { name: 'Compare' }).check();
  await page.locator('.room-card').nth(1).getByRole('checkbox', { name: 'Compare' }).check();
  await expect(page.getByRole('heading', { name: 'Room comparison' })).toBeVisible();
  await expect(page.getByRole('row', { name: /^CCT / })).toContainText('Unavailable');
});
