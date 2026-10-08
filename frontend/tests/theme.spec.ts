import { expect, test } from '@playwright/test';

test('theme choice persists and system preference responds', async ({ page }) => {
  await page.emulateMedia({ colorScheme: 'dark' });
  await page.goto('/styleguide');
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark');
  await page.getByLabel('Appearance').first().selectOption('light');
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'light');
  await page.reload();
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'light');
  await page.getByLabel('Appearance').first().selectOption('system');
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark');
  await page.emulateMedia({ colorScheme: 'light' });
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'light');
});

test('styleguide remains usable at mobile width', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('/styleguide');
  await expect(page.getByRole('heading', { name: 'A visual language for careful reading' })).toBeVisible();
  await expect(page.getByRole('navigation', { name: 'Research sections' })).toBeVisible();
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1);
  expect(overflow).toBe(false);
});
