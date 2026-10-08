import { readFileSync, existsSync } from 'node:fs';
import { resolve } from 'node:path';
import { expect, test } from '@playwright/test';

const result = resolve(import.meta.dirname, '../../artifacts/results/bundle.json');
const available = existsSync(result);
test.skip(!available, 'Real research bundle is generated after the scientific pipeline gate.');

test('published research pages read the generated bundle with API offline', async ({ page }) => {
  const bundle = JSON.parse(readFileSync(result, 'utf8'));
  const signalRequests: string[] = [];
  page.on('request', request => { if (request.url().endsWith('/research/signals.json')) signalRequests.push(request.url()); });
  await page.route('**/v1/**', route => route.abort());
  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'How does a room feel in the body?' })).toBeVisible();
  await expect(page.getByText('Research results are being prepared')).toHaveCount(0);
  await expect(page.getByText(bundle.provenance.source, { exact: false })).toBeVisible();
  expect(signalRequests).toHaveLength(0);
  await page.goto('/signals');
  await expect(page.getByText('Signal export unavailable')).toHaveCount(0);
  await expect(page.getByText('Trial records in filter').locator('..').locator('.value')).toHaveText(String(bundle.trials.length));
  await expect(page.getByText(/source analytical scenario: 500 Hz/).first()).toBeVisible();
  expect(signalRequests).toHaveLength(1);
  for (const path of ['/rooms', '/affect', '/people', '/model']) {
    await page.goto(path);
    await expect(page.getByRole('main').locator('.page-heading')).toBeVisible();
    await expect(page.getByText('export unavailable', { exact: false })).toHaveCount(0);
  }
});

test('published experiment and participant filters use scoped generated summaries', async ({ page }) => {
  const bundle = JSON.parse(readFileSync(result, 'utf8'));
  const person = bundle.people.find((row: { id: string }) => row.id === 'Subj_M');
  expect(person).toBeTruthy();
  const first = person.by_experiment.find((row: { experiment: number }) => row.experiment === 1);
  expect(first).toMatchObject({ trials: 10, valid_fused: 0, mean_valence: null, mean_arousal: null });
  await page.goto('/people');
  await page.getByRole('combobox', { name: 'Participant' }).selectOption('Subj_M');
  await page.getByRole('combobox', { name: 'Experiment' }).selectOption('1');
  const row = page.getByRole('row', { name: /Subj_M/ });
  await expect(row.locator('td').nth(0)).toHaveText('10');
  await expect(row.locator('td').nth(1)).toHaveText('0');
  await expect(row.locator('td').nth(2)).toHaveText('Unavailable');
  await expect(row).toContainText('25 years');
  await expect(row).toContainText('Male');
  await page.getByRole('combobox', { name: 'Experiment' }).selectOption('3');
  await expect(row).toContainText('n=10');
  await page.goto('/');
  await expect(page.getByText('anonymized participant IDs')).toHaveCount(0);
});

test('published affect scopes sensitivity and paired disagreement to the chosen person', async ({ page }) => {
  const bundle = JSON.parse(readFileSync(result, 'utf8'));
  expect(bundle.sensitivity.some((row: { experiment: number; participant_id: string | null }) => row.experiment === 2 && row.participant_id === null)).toBe(true);
  expect(bundle.sensitivity.some((row: { experiment: number; participant_id: string | null }) => row.experiment === 2 && row.participant_id === 'Subj_B')).toBe(false);
  await page.goto('/affect');
  await page.getByRole('combobox', { name: 'Experiment' }).selectOption('2');
  await page.getByRole('combobox', { name: 'Participant' }).selectOption('Subj_B');
  await expect(page.locator('figure').filter({ hasText: 'Fusion weight sensitivity' }).getByText('No valid sensitivity result is available for this scope.')).toBeVisible();
  await expect(page.getByText('No paired disagreement result is available for this filter.')).toBeVisible();
  await page.getByRole('combobox', { name: 'Participant' }).selectOption('Subj_M');
  await expect(page.locator('figure').filter({ hasText: 'Fusion weight sensitivity' }).getByText('Subj_M').first()).toBeVisible();
  await expect(page.getByRole('region', { name: 'Objective minus self-report' }).getByText('Subj_M').first()).toBeVisible();
  await page.getByRole('combobox', { name: 'Experiment' }).selectOption('1');
  await expect(page.getByRole('region', { name: 'Experiment 1 comfort' }).getByRole('row')).toHaveCount(11);
  await expect(page.getByRole('img', { name: /Valence arousal plot with 0 positions/ })).toBeVisible();
});

test('published model report exposes generated cohort, selection and provenance evidence', async ({ page }) => {
  const bundle = JSON.parse(readFileSync(result, 'utf8'));
  const summary = bundle.model.summary;
  expect(summary).toMatchObject({ cohort_trials: 14, cohort_participants: 3, cohort_rooms: 10 });
  await page.goto('/model');
  await expect(page.getByText('Eligible trials').locator('..').locator('.value')).toHaveText('14');
  await expect(page.getByText('Participants', { exact: true }).locator('..').locator('.value')).toHaveText('3');
  await expect(page.getByText('Rooms', { exact: true }).locator('..').locator('.value')).toHaveText('10');
  await expect(page.getByRole('heading', { name: 'Fitted preparation and selection' })).toBeVisible();
  await expect(page.getByText('random_forest')).toBeVisible();
  await expect(page.getByText('fixed training-median baseline', { exact: false })).toBeVisible();
  await expect(page.getByText(summary.provenance.code_tree_sha256)).toBeVisible();
  await expect(page.getByRole('link', { name: 'evaluation' })).toHaveAttribute('href', /artifacts\/results\/model_evaluation\.json/);
});
