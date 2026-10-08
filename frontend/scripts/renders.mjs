import fs from 'node:fs/promises';
import path from 'node:path';
import sharp from 'sharp';

const root = path.resolve(import.meta.dirname, '../..');
const out = path.join(root, 'frontend/public/rooms');
await fs.mkdir(out, { recursive: true });
const entries = [];
for (let number = 1; number <= 30; number++) {
  const experiment = Math.ceil(number / 10);
  const id = `Rm_${String(number).padStart(3, '0')}`;
  const folder = `Mark 0${experiment}_ 360 Renders`;
  const extension = experiment === 1 ? 'png' : 'jpg';
  const source = path.join(root, 'data/renders/raw', folder, `${id}.${extension}`);
  const metadata = await sharp(source).metadata();
  const stereoOverUnder = metadata.height === metadata.width;
  const eye = stereoOverUnder ? { left: 0, top: 0, width: metadata.width, height: metadata.height / 2 } : undefined;
  const image = sharp(source).extract(eye ?? { left: 0, top: 0, width: metadata.width, height: metadata.height });
  await image.clone().resize(1600, 800).webp({ quality: 82 }).toFile(path.join(out, `${id}-panorama.webp`));
  await image.clone().resize(800, 400).webp({ quality: 74 }).toFile(path.join(out, `${id}-preview.webp`));
  entries.push({ id, experiment, source: path.relative(root, source), original_width: metadata.width, original_height: metadata.height, layout: stereoOverUnder ? 'stereo-over-under' : 'mono-equirectangular', selected_eye: stereoOverUnder ? 'top' : 'single', panorama: `/rooms/${id}-panorama.webp`, preview: `/rooms/${id}-preview.webp` });
}
await fs.writeFile(path.join(root, 'data/renders/manifest.json'), JSON.stringify({ schema_version: '1', method: 'Browser derivatives from byte-preserved Lumion source renders. Square stereo over/under files use the top eye; orientation is not established.', rooms: entries }, null, 2) + '\n');
console.log(`Created ${entries.length} render pairs and manifest.`);
