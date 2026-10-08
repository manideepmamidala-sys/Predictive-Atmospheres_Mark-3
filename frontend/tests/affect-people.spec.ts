import { expect, test } from '@playwright/test';
import { SYNTHETIC_RESEARCH, useSyntheticResearch } from './fixtures';

test('affect filters distinguish components, cohorts and alpha summaries', async ({ page }) => {
  await useSyntheticResearch(page);
  await page.goto('/affect');
  await expect(page.getByText('1 complete + 0 partial-modality fused positions from 3 trials')).toBeVisible();
  await expect(page.getByRole('table', { name: 'Accessible plotted values' }).getByRole('row')).toHaveCount(2);
  await page.getByRole('combobox', { name: 'Experiment' }).selectOption('3');
  await expect(page.getByText('0 complete + 0 partial-modality fused positions from 1 trial')).toBeVisible();
  await expect(page.getByText('objective_only')).toBeVisible();
  await page.getByRole('combobox', { name: 'Component' }).selectOption('subjective');
  await expect(page.getByText('No eligible position is available for this selection.')).toBeVisible();
  await page.getByLabel('Sensitivity α').selectOption('0.5');
  const sensitivity = page.locator('figure').filter({ hasText: 'Fusion weight sensitivity' });
  await expect(sensitivity.getByRole('row')).toHaveCount(2);
  await expect(sensitivity.getByRole('row').last()).toContainText('0');
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
  await expect(page.getByText('1 participant summary')).toBeVisible();
  await expect(page.getByRole('row', { name: /P02/ })).toContainText('Unavailable');
  await expect(page.getByRole('row', { name: /P02/ })).toContainText('n=1');
  await expect(page.getByText('No eligible position is available for this selection.')).toBeVisible();
});

test('experiment summaries do not reuse all-experiment fusion means', async ({ page }) => {
  await useSyntheticResearch(page);
  await page.goto('/people');
  await page.getByRole('combobox', { name: 'Participant' }).selectOption('P01');
  await page.getByRole('combobox', { name: 'Experiment' }).selectOption('1');
  const row = page.getByRole('row', { name: /P01/ });
  await expect(row).toContainText('Unavailable');
  await expect(row.locator('td').nth(0)).toHaveText('1');
  await expect(row.locator('td').nth(1)).toHaveText('0');
  await expect(page.getByRole('img', { name: /Valence arousal plot with 0 positions/ })).toBeVisible();
  await page.getByRole('combobox', { name: 'Experiment' }).selectOption('2');
  await expect(row.locator('td').nth(1)).toHaveText('1');
});

test('affect participant selection excludes global sensitivity and disagreement rows', async ({ page }) => {
  await useSyntheticResearch(page);
  await page.goto('/affect');
  await expect(page.locator('figure').filter({ hasText: 'Fusion weight sensitivity' }).getByRole('row')).toHaveCount(4);
  await page.getByRole('combobox', { name: 'Participant' }).selectOption('P02');
  await expect(page.locator('figure').filter({ hasText: 'Fusion weight sensitivity' }).getByText('No valid sensitivity result is available for this scope.')).toBeVisible();
  await expect(page.getByText('No paired disagreement result is available for this filter.')).toBeVisible();
  await page.getByRole('combobox', { name: 'Participant' }).selectOption('P01');
  await expect(page.locator('figure').filter({ hasText: 'Fusion weight sensitivity' }).getByRole('row')).toHaveCount(2);
  await expect(page.locator('figure').filter({ hasText: 'Fusion weight sensitivity' }).getByText('All eligible IDs')).toHaveCount(0);
  await expect(page.getByText('No paired disagreement result is available for this filter.')).toHaveCount(0);
  await page.getByRole('combobox', { name: 'Experiment' }).selectOption('1');
  await expect(page.getByRole('heading', { name: 'Experiment 1 comfort' })).toBeVisible();
  await expect(page.getByRole('region', { name: 'Experiment 1 comfort' }).getByRole('row', { name: /synthetic-1/ })).toContainText('0.1');
  await expect(page.getByRole('img', { name: /Valence arousal plot with 0 positions/ })).toBeVisible();
});
