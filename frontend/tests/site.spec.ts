import { expect, test } from '@playwright/test';
import { useSyntheticResearch } from './fixtures';

const routes = [
  ['/', 'How does a room feel in the body?'], ['/rooms', 'Rooms'], ['/signals', 'Signals and quality'],
  ['/affect', 'Affect'], ['/people', 'People'], ['/simulator', 'Room simulator'], ['/model', 'Model report'],
] as const;

test('all seven routes remain readable with both themes at desktop and mobile widths', async ({ page }) => {
  test.setTimeout(90_000);
  await useSyntheticResearch(page);
  await page.route('**/v1/**', route => route.abort());
  for (const width of [390, 1366]) {
    await page.setViewportSize({ width, height: 850 });
    for (const theme of ['light', 'dark'] as const) {
      for (const [path, heading] of routes) {
        await page.goto(path);
        await page.getByRole('combobox', { name: 'Appearance' }).selectOption(theme);
        await expect(page.locator('html')).toHaveAttribute('data-theme', theme);
        await expect(page.getByRole('heading', { name: heading, exact: true })).toBeVisible();
        const overflow = await page.evaluate(() => ({ overflow: document.documentElement.scrollWidth > window.innerWidth + 1, offenders: [...document.querySelectorAll('*')].filter(element => element.getBoundingClientRect().right > window.innerWidth + 1).slice(0, 5).map(element => `${element.tagName}.${element.className} ${Math.round(element.getBoundingClientRect().right)}px`) }));
        expect(overflow.overflow, `${path} overflowed at ${width}px in ${theme}: ${overflow.offenders.join(', ')}`).toBe(false);
      }
    }
  }
});

test('keyboard skip link and reduced motion remain usable', async ({ page }) => {
  await useSyntheticResearch(page);
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.goto('/');
  await page.keyboard.press('Tab');
  await expect(page.getByRole('link', { name: 'Skip to content' })).toBeFocused();
  await page.keyboard.press('Enter');
  await expect(page.locator('#main')).toBeFocused();
  const behavior = await page.locator('html').evaluate(element => getComputedStyle(element).scrollBehavior);
  expect(behavior).toBe('auto');
});

test('research pages load from static export while the API is offline', async ({ page }) => {
  await useSyntheticResearch(page);
  await page.route('**/v1/**', route => route.abort());
  await page.goto('/');
  await expect(page.getByText('SYNTHETIC TEST FIXTURE')).toBeVisible();
  await page.goto('/signals');
  await expect(page.getByRole('row', { name: /synthetic-2/ })).toBeVisible();
  await page.goto('/model');
  await expect(page.getByText('Synthetic weak-model status for browser testing.')).toBeVisible();
});

test('missing static export shows a plain unavailable state', async ({ page }) => {
  await page.route('**/research/bundle.json', route => route.fulfill({ status: 200, contentType: 'text/html', body: '<!doctype html><html></html>' }));
  await page.goto('/');
  await expect(page.getByText('Validated research results are not published yet.')).toBeVisible();
  await expect(page.getByText('Unexpected token', { exact: false })).toHaveCount(0);
});
