import { expect, test } from '@playwright/test';
import { useSyntheticAnalysis, useSyntheticResearch } from './fixtures';

test('physiology-led component view distinguishes report, fusion and E1 comfort', async ({ page }) => {
  await useSyntheticResearch(page); await useSyntheticAnalysis(page);
  await page.goto('/body');
  await expect(page.getByRole('combobox', { name: 'Component' })).toHaveValue('objective');
  await expect(page.locator('circle.point')).toHaveCount(1);
  await page.getByRole('combobox', { name: 'Component' }).selectOption('subjective');
  await expect(page).toHaveURL(/component=subjective/);
  await expect(page.locator('circle.point')).toHaveCount(1);
  await page.getByRole('combobox', { name: 'Component' }).selectOption('fused');
  await expect(page.getByRole('table', { name: /Accessible plotted valence and arousal values/ })).toContainText('Fused');
  await page.getByRole('combobox', { name: 'Experiment' }).selectOption('1');
  await expect(page.locator('circle.point')).toHaveCount(0);
  await expect(page.getByText('No eligible position is available for this selection.')).toBeVisible();
  await page.goto('/explore?view=trials&experiment=1');
  await expect(page.getByRole('row', { name: /synthetic-1/ })).toContainText('Unavailable');
});

test('participant and room filters persist in explorer URL', async ({ page }) => {
  await useSyntheticResearch(page);
  await page.goto('/explore?view=people&person=P02');
  await expect(page.getByRole('row', { name: /P02/ })).toContainText('Unavailable');
  await page.getByRole('combobox', { name: 'View' }).selectOption('trials');
  await page.getByRole('combobox', { name: 'Room' }).selectOption('Rm_021');
  await expect(page).toHaveURL(/person=P02/);
  await expect(page).toHaveURL(/room=Rm_021/);
  await expect(page.getByRole('row', { name: /synthetic-3/ })).toBeVisible();
});

test('participant summaries follow experiment scope and label room filter limits', async ({ page }) => {
  await useSyntheticResearch(page);
  await page.goto('/explore?view=people&person=P01&experiment=1');
  const row = page.getByRole('row', { name: /P01/ });
  await expect(row.locator('td').first()).toHaveText('1');
  await expect(row.locator('td').nth(1)).toHaveText('0');
  await page.getByRole('combobox', { name: 'Experiment' }).selectOption('2');
  await expect(row.locator('td').nth(1)).toHaveText('1');
  await page.getByRole('combobox', { name: 'Room' }).selectOption('Rm_011');
  await expect(page.getByText(/summary metrics still cover the whole selected experiment/)).toBeVisible();
  await page.getByRole('combobox', { name: 'Room' }).selectOption('Rm_021');
  await expect(row).toHaveCount(0);
});
