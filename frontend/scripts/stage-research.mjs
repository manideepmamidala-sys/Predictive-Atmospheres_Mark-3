import fs from 'node:fs/promises';
import path from 'node:path';
import { createHash } from 'node:crypto';

const frontend = path.resolve(import.meta.dirname, '..');
const results = path.resolve(frontend, '../artifacts/results');
const published = path.join(frontend, 'public/research');
const manifestPath = path.join(results, 'manifest.json');
const required = process.env.PA_REQUIRE_RESEARCH_EXPORT === '1';

await fs.mkdir(published, { recursive: true });
let manifest;
try {
  manifest = JSON.parse(await fs.readFile(manifestPath, 'utf8'));
} catch (error) {
  await Promise.all(['bundle.json', 'signals.json'].map(name => fs.rm(path.join(published, name), { force: true })));
  if (required) throw new Error(`Validated research bundle is required: ${error.message}`);
  console.log('Research bundle has not been generated; site will show explicit unavailable states.');
  process.exit(0);
}

if (manifest.schema_version !== '1.0.0') throw new Error('Research manifest schema is incompatible.');
const products = {};
for (const name of ['bundle', 'signals']) {
  const fileName = `${name}.json`;
  const bytes = await fs.readFile(path.join(results, fileName));
  const digest = createHash('sha256').update(bytes).digest('hex');
  if (manifest.products?.[name]?.file !== fileName || manifest.products?.[name]?.sha256 !== digest) {
    throw new Error(`${fileName} digest does not match generated manifest.`);
  }
  products[name] = { bytes, data: JSON.parse(bytes.toString('utf8')), digest };
}
const bundle = products.bundle.data;
const signals = products.signals.data;
if (bundle.schema_version !== '1.0.0' || !Array.isArray(bundle.rooms) || !Array.isArray(bundle.trials) || signals.schema_version !== '1.0.0' || !Array.isArray(signals.trials)) {
  throw new Error('Research bundle has an incompatible top-level shape.');
}
const bundleIds = new Set(bundle.trials.map(trial => trial.id));
const signalIds = new Set(signals.trials.map(trial => trial.id));
if (bundleIds.size !== bundle.trials.length || signalIds.size !== signals.trials.length || bundleIds.size !== signalIds.size || [...bundleIds].some(id => !signalIds.has(id))) {
  throw new Error('Research bundle and signal trial IDs do not match.');
}
await Promise.all(Object.entries(products).map(([name, { bytes }]) => fs.writeFile(path.join(published, `${name}.json`), bytes)));
console.log(`Staged validated research products (${bundle.trials.length} trial records, bundle ${products.bundle.bytes.length} bytes, signals ${products.signals.bytes.length} bytes).`);
