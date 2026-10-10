import { expect, test } from '@playwright/test';
import { useSyntheticResearch } from './fixtures';

test('explorer loads separate signals only on signal view and keeps missingness visible', async ({ page }) => {
  await useSyntheticResearch(page);
  const requests: string[] = [];
  page.on('request', request => { if (request.url().endsWith('/research/signals.json')) requests.push(request.url()); });
  await page.goto('/explore?experiment=3&person=P02');
  await expect(page.getByRole('row', { name: /synthetic-3/ })).toContainText('ECG peaks absent');
  expect(requests).toHaveLength(0);
  await page.getByRole('combobox', { name: 'View' }).selectOption('signals');
  await expect(page).toHaveURL(/view=signals/);
  await expect(page.getByText(/Signal traces ready for 3 trial records/)).toBeVisible();
  expect(requests).toHaveLength(1);
  await expect(page.getByText('No raw trace was exported for this trial.')).toBeVisible();
  await page.getByRole('combobox', { name: 'Trace state' }).selectOption('cleaned');
  await expect(page.getByText('No cleaned trace was exported for this trial.').first()).toBeVisible();
  await page.getByRole('combobox', { name: 'Experiment' }).selectOption('2');
  await page.getByRole('combobox', { name: 'Room' }).selectOption('all');
  await page.getByRole('combobox', { name: 'Participant' }).selectOption('all');
  await page.getByRole('combobox', { name: 'Trace state' }).selectOption('cleaned');
  await expect(page.getByRole('img', { name: /EEG trace cleaned trace/ })).toBeVisible();
  await expect(page.getByText(/unit: µV; display rate: 4 Hz/)).toBeVisible();
});

test('changing signal filters never shows a stale trial outside the visible scope', async ({ page }) => {
  await useSyntheticResearch(page);
  await page.goto('/explore?view=signals&experiment=2');
  await expect(page.getByRole('combobox', { name: 'Trial' })).toHaveValue('synthetic-2');
  await page.getByRole('combobox', { name: 'Experiment' }).selectOption('3');
  await expect(page.getByRole('combobox', { name: 'Trial' })).toHaveValue('synthetic-3');
  await page.getByRole('combobox', { name: 'Participant' }).selectOption('P01');
  await expect(page.getByText('No trial matches these filters, so no trace is selected.')).toBeVisible();
  await expect(page.getByRole('combobox', { name: 'Trial' })).toHaveCount(0);
});
