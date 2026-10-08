import { useState } from 'react';
import { Figure } from '../ui';

type Geometry = { length: number; width: number; height: number };
type Point = [number, number];
export default function Massing({ geometry }: { geometry: Geometry | null }) {
  const [rotation, setRotation] = useState(35);
  const project = (x: number, y: number, z: number): Point => {
    const angle = rotation * Math.PI / 180;
    const scale = geometry ? 85 / Math.max(geometry.length, geometry.width, geometry.height) : 1;
    return [180 + (x * Math.cos(angle) - y * Math.sin(angle)) * scale,
      145 + (x * Math.sin(angle) + y * Math.cos(angle)) * scale * .48 - z * scale];
  };
  const corners = geometry ? [
    project(0, 0, 0), project(geometry.length, 0, 0),
    project(geometry.length, geometry.width, 0), project(0, geometry.width, 0),
    project(0, 0, geometry.height), project(geometry.length, 0, geometry.height),
    project(geometry.length, geometry.width, geometry.height), project(0, geometry.width, geometry.height),
  ] : [];
  const shape = (indices: number[]) => indices.map(index => corners[index].map(n => n.toFixed(1)).join(',')).join(' ');
  return <Figure title="Schematic massing" caption={geometry ? `${geometry.length} × ${geometry.width} × ${geometry.height} m entered geometry. Isometric schematic only: no window, material, light or affect simulation.` : 'Enter valid length, width and height to see a schematic room volume. This is not a source render.'}>
    {geometry ? <><svg viewBox="0 0 360 230" role="img" aria-label={`Schematic room volume, ${geometry.length} meters long, ${geometry.width} meters wide, ${geometry.height} meters high`}>
      <polygon points={shape([0, 1, 5, 4])} fill="var(--soft)" stroke="var(--ink)" strokeWidth="1.5" />
      <polygon points={shape([1, 2, 6, 5])} fill="var(--rule)" fillOpacity=".7" stroke="var(--ink)" strokeWidth="1.5" />
      <polygon points={shape([2, 3, 7, 6])} fill="var(--soft)" stroke="var(--ink)" strokeWidth="1.5" />
      <polygon points={shape([3, 0, 4, 7])} fill="var(--rule)" fillOpacity=".7" stroke="var(--ink)" strokeWidth="1.5" />
      <polygon points={shape([4, 5, 6, 7])} fill="var(--surface)" fillOpacity=".85" stroke="var(--ink)" strokeWidth="1.5" />
    </svg><label className="field">Rotate schematic <input type="range" min="0" max="360" value={rotation} onChange={event => setRotation(Number(event.target.value))} /></label></> : <p className="small-text">No geometry entered.</p>}
  </Figure>;
}
