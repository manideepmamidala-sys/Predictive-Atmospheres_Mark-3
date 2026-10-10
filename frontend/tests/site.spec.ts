import { expect, test } from '@playwright/test';
import { useSyntheticAnalysis, useSyntheticResearch } from './fixtures';

const routes = [
  ['/', 'What if space could be read through experience?'], ['/study', 'The Study'], ['/rooms', 'Rooms & Experience'],
  ['/body', 'Body & Experience'], ['/prediction', 'Prediction & Findings'], ['/studio', 'Design Studio'],
  ['/explore', 'Data Explorer'], ['/methods', 'Methods & Research Context'],
] as const;

test('all eight routes, navigation and themes fit desktop and mobile viewports', async ({ page }) => {
  test.setTimeout(150_000);
  await useSyntheticResearch(page); await useSyntheticAnalysis(page);
  await page.route('**/v1/**', route => route.abort());
  for (const { width, height } of [{ width: 1440, height: 900 }, { width: 390, height: 844 }]) {
    await page.setViewportSize({ width, height });
    for (const theme of ['light', 'dark'] as const) {
      for (const [path, heading] of routes) {
        await page.goto(path);
        await page.getByRole('combobox', { name: 'Appearance' }).selectOption(theme);
        await expect(page.getByRole('heading', { name: heading, exact: true })).toBeVisible();
        await expect(page.getByRole('navigation', { name: 'Research sections' }).getByRole('link', { name: path === '/' ? 'Predictive Atmospheres' : heading })).toHaveAttribute('aria-current', 'page');
        const overflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1);
        expect(overflow, `${path} overflowed at ${width}px in ${theme}`).toBe(false);
      }
    }
  }
});

test('old links preserve useful filters and unknown paths show a real 404', async ({ page }) => {
  await useSyntheticResearch(page);
  await page.goto('/signals?experiment=3&person=P02#trace');
  await expect(page).toHaveURL(/\/explore\?experiment=3&person=P02&view=signals#trace/);
  await expect(page.getByRole('heading', { name: 'Data Explorer' })).toBeVisible();
  await page.goto('/affect?experiment=2&component=subjective');
  await expect(page).toHaveURL(/\/body\?experiment=2&component=subjective/);
  await page.goto('/people?person=P02');
  await expect(page).toHaveURL(/\/explore\?person=P02&view=people/);
  await page.goto('/simulator?room=Rm_021');
  await expect(page).toHaveURL(/\/studio\?room=Rm_021/);
  await expect(page.getByRole('combobox', { name: 'Studied-room preset' })).toHaveValue('Rm_021');
  await expect(page.getByLabel('Length', { exact: true })).toHaveValue('7');
  await page.goto('/model');
  await expect(page).toHaveURL(/\/prediction$/);
  await page.goto('/unknown-research-route');
  await expect(page.getByText('404 · Page not found')).toBeVisible();
  await expect(page).toHaveTitle('Page not found | Predictive Atmospheres');
  await expect(page.locator('.not-found').getByRole('link', { name: /The Study/ })).toBeVisible();
});

test('keyboard skip link, reduced motion and offline research reading', async ({ page }) => {
  await useSyntheticResearch(page); await useSyntheticAnalysis(page);
  await page.route('**/v1/**', route => route.abort());
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.goto('/');
  await page.keyboard.press('Tab');
  await expect(page.getByRole('link', { name: 'Skip to content' })).toBeFocused();
  await page.keyboard.press('Enter');
  await expect(page.locator('#main')).toBeFocused();
  expect(await page.locator('html').evaluate(element => getComputedStyle(element).scrollBehavior)).toBe('auto');
  await page.goto('/body');
  await expect(page.getByRole('heading', { name: 'Synthetic B8 question' })).toBeVisible();
  await page.goto('/prediction');
  await expect(page.getByRole('heading', { name: 'Synthetic P5 question' })).toBeVisible();
});

test('route navigation resets focus and scroll, while delayed chart anchors find their target', async ({ page }) => {
  await useSyntheticResearch(page); await useSyntheticAnalysis(page);
  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'What if space could be read through experience?' })).toBeVisible();
  await page.evaluate(() => window.scrollTo({ top: document.body.scrollHeight, behavior: 'instant' }));
  expect(await page.evaluate(() => window.scrollY)).toBeGreaterThan(1000);
  await page.getByRole('navigation', { name: 'Research sections' }).getByRole('link', { name: 'The Study' }).click();
  await expect(page.getByRole('heading', { name: 'The Study', exact: true })).toBeVisible();
  await expect(page.locator('#main')).toBeFocused();
  await expect.poll(() => page.evaluate(() => window.scrollY)).toBeLessThan(20);
  await expect(page).toHaveTitle('The Study | Predictive Atmospheres');

  const chart = page.locator('#analysis-S3');
  await expect(chart).toBeVisible();
  await page.locator('.analysis-row').filter({ has: chart }).getByRole('link', { name: 'See related data ↗' }).click();
  await expect(page.getByRole('heading', { name: 'Data Explorer', exact: true })).toBeVisible();
  await expect(page.locator('#main')).toBeFocused();
  await expect(page).toHaveTitle('Data Explorer | Predictive Atmospheres');
  await page.getByRole('link', { name: 'Return to the chart ↗' }).click();
  await expect(page).toHaveURL(/\/study#analysis-S3$/);
  await expect(chart).toBeFocused();
  await expect.poll(() => chart.evaluate(element => Math.round(element.getBoundingClientRect().top)))
    .toBeGreaterThanOrEqual(110);
  await expect.poll(() => chart.evaluate(element => Math.round(element.getBoundingClientRect().top)))
    .toBeLessThan(180);
  await page.goto('/study#analysis-S3');
  await expect(chart).toBeFocused();
  await expect.poll(() => chart.evaluate(element => Math.round(element.getBoundingClientRect().top)))
    .toBeGreaterThanOrEqual(110);
});

test('Explorer query-filter changes keep the current reading position', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await useSyntheticResearch(page);
  await page.goto('/explore');
  const experiment = page.getByRole('combobox', { name: 'Experiment', exact: true });
  await experiment.scrollIntoViewIfNeeded();
  const before = await page.evaluate(() => window.scrollY);
  await experiment.selectOption('2');
  await expect(page).toHaveURL(/\/explore\?experiment=2$/);
  expect(Math.abs(await page.evaluate(() => window.scrollY) - before)).toBeLessThan(5);
});
