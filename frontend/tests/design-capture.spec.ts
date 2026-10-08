import { mkdir } from 'node:fs/promises';
import { resolve } from 'node:path';
import { expect, test } from '@playwright/test';

const destination = resolve(import.meta.dirname, '../../docs/reports/screenshots');
test('capture design checkpoint in both themes and widths', async ({ page }) => {
  test.setTimeout(60_000);
  await mkdir(destination, { recursive: true });
  for (const width of [390, 1366]) {
    await page.setViewportSize({ width, height: 900 });
    for (const theme of ['light', 'dark'] as const) {
      await page.goto('/styleguide');
      await page.getByRole('combobox', { name: 'Appearance' }).selectOption(theme);
      await expect(page.getByRole('heading', { name: 'A visual language for careful reading' })).toBeVisible();
      await page.evaluate(() => document.fonts.ready);
      await page.screenshot({ path: resolve(destination, `design-${theme}-${width === 390 ? 'mobile' : 'desktop'}.png`), fullPage: true });
    }
  }
});
