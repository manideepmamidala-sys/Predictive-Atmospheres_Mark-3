import { useState } from 'react';
import { Figure } from '../ui';
import { repositoryFileUrl } from '../lib/repository';

export default function Panorama({ src, original, roomId, layout }: { src: string; original: string; roomId: string; layout: string }) {
  const [position, setPosition] = useState(50);
  const sourceUrl = repositoryFileUrl(original);
  return <Figure title={`${roomId} panorama`} caption={`Browser derivative of the original Lumion render. ${layout === 'stereo-over-under' ? 'Top eye was selected as an inferred presentation extraction from the stacked stereo source; eye convention and orientation remain unverified.' : 'Single equirectangular source.'} Visual lighting is not a calibrated exposure measurement.`}>
    <div style={{ overflow: 'hidden', aspectRatio: '16/9', background: 'var(--soft)' }}><img src={src} alt={`Equirectangular panorama for ${roomId}`} style={{ width: '200%', height: '100%', objectFit: 'cover', maxWidth: 'none', transform: `translateX(-${position / 2}%)` }} /></div>
    <label className="field">Explore horizontal view <input aria-label={`Pan ${roomId} view`} type="range" min="0" max="100" value={position} onChange={event => setPosition(Number(event.target.value))} /></label>
    <p className="figure-note">Use the slider with arrow keys to pan. {sourceUrl && <a href={sourceUrl} target="_blank" rel="noreferrer">Open preserved source image in the repository</a>}</p>
  </Figure>;
}
