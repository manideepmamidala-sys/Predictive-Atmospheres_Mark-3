import { expect, test } from '@playwright/test';
import { SYNTHETIC_RESEARCH, useSyntheticResearch } from './fixtures';

test('affect filters distinguish components, cohorts and alpha summaries', async ({ page }) => {
  await useSyntheticResearch(page);
  await page.goto('/affect');
  await expect(page.getByText('1 complete + 0 partial-modality fused positions from 3 trials')).toBeVisible();
  await expect(page.getByRole('table', { name: 'Accessible plotted values' }).getByRole('row')).toHaveCount(2);
  await page.getByLabel('Experiment').selectOption('3');
  await expect(page.getByText('0 complete + 0 partial-modality fused positions from 1 trial')).toBeVisible();
  await expect(page.getByText('objective_only')).toBeVisible();
  await page.getByRole('combobox', { name: 'Component' }).selectOption('subjective');
  await expect(page.getByText('No eligible position is available for this selection.')).toBeVisible();
  await page.getByLabel('Sensitivity α').selectOption('0.5');
  await expect(page.getByRole('table').last().getByRole('row')).toHaveCount(2);
});

test('partial fused records remain separate from complete headline counts', async ({ page }) => {
  const changed = structuredClone(SYNTHETIC_RESEARCH);
  changed.trials[1].cohort = 'partial_modality_fusion';
  await useSyntheticResearch(page, changed);
  await page.goto('/');
  await expect(page.getByText('Complete-fusion positions').locator('..').locator('.value')).toHaveText('0');
  await expect(page.getByText('Partial-modality fused positions').locator('..').locator('.value')).toHaveText('1');
  await page.goto('/affect');
  await expect(page.getByText('Partial-modality fusion').locator('..').locator('.value')).toHaveText('1');
  await expect(page.getByRole('table', { name: 'Accessible plotted values' }).getByText('partial_modality_fusion')).toBeVisible();
});

test('people filters retain structural missingness', async ({ page }) => {
  await useSyntheticResearch(page);
  await page.goto('/people');
  await page.getByRole('combobox', { name: 'Participant' }).selectOption('P02');
  await expect(page.getByText('1 participant summaries')).toBeVisible();
  await expect(page.getByRole('row', { name: /P02/ })).toContainText('Unavailable');
  await expect(page.getByRole('row', { name: /P02/ })).toContainText('7 h');
  await expect(page.getByText('No eligible position is available for this selection.')).toBeVisible();
});
