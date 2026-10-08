import { expect, test } from '@playwright/test';
import { SYNTHETIC_RESEARCH, useSyntheticResearch } from './fixtures';

for (const theme of ['light', 'dark'] as const) {
  test(`affect chart computes distinct CCT colors and an open partial marker in ${theme}`, async ({ page }) => {
    const data = structuredClone(SYNTHETIC_RESEARCH);
    data.rooms[1].cct_kelvin = 2700;
    data.rooms[2].cct_kelvin = 6500;
    const cool = structuredClone(data.trials[1]);
    cool.id = 'synthetic-cool';
    cool.room_id = data.rooms[2].id;
    cool.cohort = 'partial_modality_fusion';
    const unknown = structuredClone(data.trials[1]);
    unknown.id = 'synthetic-unknown';
    unknown.room_id = data.rooms[0].id;
    data.trials.push(cool, unknown);
    await useSyntheticResearch(page, data);
    await page.goto('/affect');
    await page.getByRole('combobox', { name: 'Appearance' }).selectOption(theme);
    const chart = page.locator('figure').filter({ hasText: 'Atmosphere plane' });
    await expect(chart.locator('circle.point')).toHaveCount(3);
    const styles = await chart.locator('svg').evaluate(svg => {
      const rect = svg.querySelector('rect')!;
      return {
        plot: getComputedStyle(rect).fill,
        points: [...svg.querySelectorAll('circle.point')].map(point => ({ fill: getComputedStyle(point).fill, stroke: getComputedStyle(point).stroke })),
      };
    });
    expect(styles.points[0].fill).not.toBe(styles.points[1].stroke);
    expect(styles.points[0].fill).not.toBe(styles.points[2].fill);
    expect(styles.points[1].fill).toBe(styles.plot);
    expect(styles.points[1].stroke).not.toBe(styles.plot);
    expect(styles.points[2].fill).not.toBe(styles.plot);
  });
}
