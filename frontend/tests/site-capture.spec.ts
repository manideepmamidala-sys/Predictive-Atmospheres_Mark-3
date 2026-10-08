import { existsSync } from 'node:fs';
import { mkdir } from 'node:fs/promises';
import { resolve } from 'node:path';
import { expect, test } from '@playwright/test';

const result = resolve(import.meta.dirname, '../../artifacts/results/bundle.json');
const destination = resolve(import.meta.dirname, '../../docs/reports/screenshots');
test.skip(!existsSync(result), 'Final screenshots require the generated research bundle.');
const routes = ['/', '/rooms', '/signals', '/affect', '/people', '/simulator', '/model'] as const;
const label = (route: string) => route === '/' ? 'study' : route.slice(1);

test('capture all seven routes in complementary theme and width views', async ({ page }) => {
  test.setTimeout(120_000);
  await mkdir(destination, { recursive: true });
  await page.route('**/v1/**', route => route.abort());
  for (const [width, theme] of [[1366, 'light'], [390, 'dark']] as const) {
    await page.setViewportSize({ width, height: 900 });
    for (const route of routes) {
      await page.goto(route);
      await page.getByRole('combobox', { name: 'Appearance' }).selectOption(theme);
      await expect(page.locator('.page-heading')).toBeVisible();
      if (route === '/signals') await expect(page.getByText(/source analytical scenario: 500 Hz/).first()).toBeVisible();
      await page.evaluate(() => document.fonts.ready);
      await page.screenshot({ path: resolve(destination, `final-${label(route)}-${theme}-${width === 390 ? 'mobile' : 'desktop'}.png`) });
    }
  }
});
