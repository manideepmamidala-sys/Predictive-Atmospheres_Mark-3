import fs from 'node:fs/promises';
import path from 'node:path';
import { createHash } from 'node:crypto';

const frontend = path.resolve(import.meta.dirname, '..');
const results = path.resolve(frontend, '../artifacts/results');
const published = path.join(frontend, 'public/research');
const manifestPath = path.join(results, 'manifest.json');
const required = process.env.PA_REQUIRE_RESEARCH_EXPORT === '1';
const analysisIds = ['S1', 'S2', 'S3', 'S4', 'S5', 'R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8', 'R9', 'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'P1', 'P2', 'P3', 'P4', 'P5', 'Methods'];
const analysisSource = path.join(results, 'analysis');
const analysisPublished = path.join(published, 'analysis');

await fs.mkdir(published, { recursive: true });
let manifest;
try {
  manifest = JSON.parse(await fs.readFile(manifestPath, 'utf8'));
} catch (error) {
  await Promise.all(['bundle.json', 'signals.json'].map(name => fs.rm(path.join(published, name), { force: true })));
  await fs.rm(analysisPublished, { recursive: true, force: true });
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

let analysisIndex;
try { analysisIndex = JSON.parse(await fs.readFile(path.join(analysisSource, 'index.json'), 'utf8')); }
catch (error) {
  await fs.rm(analysisPublished, { recursive: true, force: true });
  if (required) throw new Error(`Complete analysis catalogue is required: ${error.message}`);
  console.log('Analysis catalogue has not been generated; research pages will show an explicit unavailable state.');
  process.exit(0);
}
const hash = value => typeof value === 'string' && /^[0-9a-f]{64}$/.test(value);
if (analysisIndex.schema_version !== '1.0.0' || analysisIndex.method_version !== '1.2.0' || !hash(analysisIndex.approved_spec_sha256) || !Array.isArray(analysisIndex.products)) throw new Error('Analysis catalogue index has an incompatible shape.');
const listedIds = analysisIndex.products.map(item => item.id);
if (listedIds.length !== analysisIds.length || new Set(listedIds).size !== analysisIds.length || analysisIds.some(id => !listedIds.includes(id))) throw new Error('Analysis catalogue index must list all 28 IDs exactly once.');
const validated = [];
for (const entry of analysisIndex.products) {
  if (entry.path !== `/research/analysis/${entry.id}.json` || !['available', 'unavailable'].includes(entry.status) || !entry.route?.startsWith('/')) throw new Error(`Analysis index entry ${entry.id} is invalid.`);
  const bytes = await fs.readFile(path.join(analysisSource, `${entry.id}.json`));
  const product = JSON.parse(bytes.toString('utf8'));
  const counts = product.counts;
  const provenance = product.provenance;
  const chart = product.chart;
  if (product.schema_version !== '1.0.0' || product.id !== entry.id || product.route !== entry.route || product.status !== entry.status || !product.question || !product.takeaway || !product.method || !Array.isArray(product.caveats) || !counts || !['trials', 'participants', 'rooms'].every(key => Number.isInteger(counts[key]) && counts[key] >= 0) || !product.units || !provenance || provenance.method_version !== '1.2.0' || provenance.approved_spec_sha256 !== analysisIndex.approved_spec_sha256 || !hash(provenance.source_manifest_sha256) || !provenance.generated_at_utc || !chart || !['line', 'bar', 'scatter', 'heatmap', 'table'].includes(chart.type) || !Array.isArray(chart.rows) || typeof chart.x !== 'string' || typeof chart.y !== 'string' || typeof chart.x_label !== 'string' || typeof chart.y_label !== 'string' || (product.status === 'unavailable' && !product.availability_reason)) throw new Error(`Analysis product ${entry.id} failed staging validation.`);
  validated.push({ id: entry.id, bytes });
}
await fs.rm(analysisPublished, { recursive: true, force: true });
await fs.mkdir(analysisPublished, { recursive: true });
await fs.writeFile(path.join(analysisPublished, 'index.json'), JSON.stringify(analysisIndex));
await Promise.all(validated.map(product => fs.writeFile(path.join(analysisPublished, `${product.id}.json`), product.bytes)));
console.log(`Staged complete analysis catalogue (${validated.length} validated products).`);
