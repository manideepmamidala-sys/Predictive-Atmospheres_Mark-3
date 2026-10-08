import { expect, test } from '@playwright/test';
import { useSyntheticResearch } from './fixtures';

test('signal filters keep QC, missingness, units and trace mode visible', async ({ page }) => {
  await useSyntheticResearch(page);
  await page.goto('/signals');
  await expect(page.getByRole('heading', { name: 'Signals and quality' })).toBeVisible();
  await expect(page.getByText('3', { exact: true }).first()).toBeVisible();
  await page.getByLabel('Experiment').selectOption('3');
  await expect(page.getByRole('combobox', { name: 'Trial' }).locator('option')).toHaveCount(1);
  await expect(page.getByRole('region', { name: 'Eligibility for this trial' }).getByText('ECG peaks absent')).toBeVisible();
  await expect(page.getByText('No raw trace was exported for this trial.')).toBeVisible();
  await page.getByRole('combobox', { name: 'Trace' }).selectOption('cleaned');
  await expect(page.getByText('No cleaned trace was exported for this trial.').first()).toBeVisible();
  await page.getByLabel('Experiment').selectOption('2');
  await expect(page.getByRole('img', { name: /EEG trace cleaned trace/ })).toBeVisible();
  await expect(page.getByText(/unit: µV; display rate: 4 Hz; source analytical scenario: unconfirmed Hz; window: 2.0–3.0 s/i)).toBeVisible();
});
