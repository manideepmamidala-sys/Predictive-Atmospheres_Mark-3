import { existsSync, readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { expect, test } from '@playwright/test';

const path = resolve(import.meta.dirname, '../../artifacts/results/bundle.json');
test.skip(!existsSync(path), 'Validated source bundle is not generated yet.');

test('actual E3 presets carry every independent source attribute without filling E2 gaps', async ({ page }) => {
  const bundle = JSON.parse(readFileSync(path, 'utf8'));
  const complete = bundle.rooms.filter((room: { experiment: number; independent_attributes?: Record<string, unknown> }) => room.experiment === 3 && Object.values(room.independent_attributes || {}).every(value => value != null));
  expect(complete).toHaveLength(10);
  const first = complete[0];
  await page.route('**/v1/meta', route => route.fulfill({ json: { schema_version: '1.0.0', data_manifest_sha256: 'source-fixture', artifact_version: 'source-fixture', model_status: 'baseline_only', ready: true, limitations: [] } }));
  await page.goto('/studio');
  const presets = page.getByRole('combobox', { name: 'Studied-room preset' });
  await expect(presets.locator('option')).toHaveCount(11);
  await expect(presets.locator('option[value="Rm_011"]')).toHaveCount(0);
  await presets.selectOption(first.id);
  const labels: Record<string, string> = {
    length: 'Length', width: 'Width', height: 'Height', num_doors: 'Door count', door_area: 'Total door area',
    num_windows: 'Window count', window_area: 'Total window area', daylight_factor: 'Daylight factor',
    illuminance: 'Illuminance', cct: 'Colour temperature', walkable_floor_area: 'Walkable floor area',
  };
  for (const [key, label] of Object.entries(labels)) await expect(page.getByLabel(label, { exact: true })).toHaveValue(String(first.independent_attributes[key]));
  await expect(page.getByRole('combobox', { name: 'Time of day' })).toHaveValue(first.independent_attributes.day_or_night);
  await expect(page.getByRole('combobox', { name: 'Space type' })).toHaveValue(first.independent_attributes.space_type);
});
