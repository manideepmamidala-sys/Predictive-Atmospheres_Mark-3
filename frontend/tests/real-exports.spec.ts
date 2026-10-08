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
