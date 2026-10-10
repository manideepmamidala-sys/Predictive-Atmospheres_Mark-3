import { Suspense, lazy, useMemo, useRef, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import manifest from '../../../data/renders/manifest.json';
import { useResearch } from '../lib/research';
import Catalogue from './Catalogue';
import { Notice, PageHeading, Value } from '../ui';

const Panorama = lazy(() => import('../figures/Panorama'));

export default function Rooms() {
  const research = useResearch();
  const data = research.status === 'ready' ? research.data : null;
  const [params, setParams] = useSearchParams();
  const [showPanorama, setShowPanorama] = useState(false);
  const detailRef = useRef<HTMLElement>(null);
  const detailHeadingRef = useRef<HTMLHeadingElement>(null);
  const experiment = params.get('experiment') || 'all';
  const type = params.get('type') || 'all';
  const roomId = params.get('room') || manifest.rooms[0].id;
  const lookup = useMemo(() => new Map(data?.rooms.map(room => [room.id, room]) || []), [data]);
  const types = [...new Set(data?.rooms.map(item => item.space_type).filter((value): value is string => !!value) || [])].sort();
  const shown = manifest.rooms.filter(asset => (experiment === 'all' || String(asset.experiment) === experiment) && (type === 'all' || lookup.get(asset.id)?.space_type === type));
  const active = shown.find(asset => asset.id === roomId) || shown[0] || manifest.rooms[0];
  const room = lookup.get(active.id);
  const setFilter = (key: string, value: string) => setParams(previous => {
    const next = new URLSearchParams(previous);
    if (value === 'all') next.delete(key); else next.set(key, value);
    if (key !== 'room' && next.has('room')) {
      const selected = manifest.rooms.find(asset => asset.id === next.get('room'));
      if (!selected || (next.has('experiment') && String(selected.experiment) !== next.get('experiment')) || (next.has('type') && lookup.get(selected.id)?.space_type !== next.get('type'))) next.delete('room');
    }
    return next;
  });
  const selectRoom = (id: string) => {
    setFilter('room', id); setShowPanorama(false);
    if (window.matchMedia('(max-width: 1080px)').matches) requestAnimationFrame(() => {
      detailRef.current?.scrollIntoView({ block: 'start', behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth' });
      detailHeadingRef.current?.focus({ preventScroll: true });
    });
  };
  return <><PageHeading eyebrow="02 / Spatial metrics" title="Rooms & Experience" intro="What changes across the rendered rooms, and how do reported experiences relate to those spatial attributes? Browse the original stimuli, then inspect room-level analyses with their actual denominators." />
    <div className="rooms-layout"><div><div className="toolbar"><label>Experiment<select value={experiment} onChange={event => setFilter('experiment', event.target.value)}><option value="all">All experiments</option><option value="1">Form · 1</option><option value="2">Lighting · 2</option><option value="3">Function · 3</option></select></label><label>Space type<select value={type} onChange={event => setFilter('type', event.target.value)}><option value="all">All types</option>{types.map(value => <option key={value}>{value}</option>)}</select></label><span className="status">{shown.length} source renders</span></div>
      <div className="rooms-grid">{shown.map(asset => <button type="button" className={`room-tile ${active.id === asset.id ? 'active' : ''}`} key={asset.id} onClick={() => selectRoom(asset.id)} aria-pressed={active.id === asset.id}><img src={asset.preview} alt="" loading="lazy" /><span><strong>{asset.id}</strong><small>Experiment {asset.experiment}{lookup.get(asset.id)?.space_type ? ` · ${lookup.get(asset.id)?.space_type}` : ''}</small></span></button>)}</div>{!shown.length && <Notice title="No rooms match"><p>Adjust the filters to browse the source renders.</p></Notice>}</div>
      {shown.length > 0 && <aside className="room-detail" ref={detailRef}><img className="detail-image" src={active.preview} alt={`Original study render preview for ${active.id}`} /><div className="room-detail-body"><p className="eyebrow">Source stimulus · Experiment {active.experiment}</p><h2 ref={detailHeadingRef} tabIndex={-1}>{active.id}</h2><p>{room?.space_type || 'Space type unavailable'} · {room?.lighting || 'Lighting label unavailable'}</p><dl><div><dt>Illuminance</dt><dd><Value value={room?.illuminance_lux} unit="lux" /></dd></div><div><dt>Colour temperature</dt><dd><Value value={room?.cct_kelvin} unit="K" /></dd></div></dl><p className="small-text">These supplied values are room metadata, not calibrated headset exposure.</p><Link to={`/explore?room=${active.id}`}>See {active.id} trial records ↗</Link><button type="button" className="subtle" onClick={() => setShowPanorama(value => !value)}>{showPanorama ? 'Hide panorama' : 'Explore panorama'}</button></div>{showPanorama && <Suspense fallback={<p role="status">Loading panorama…</p>}><Panorama roomId={active.id} src={active.panorama} original={active.source} layout={active.layout} /></Suspense>}</aside>}</div>
    <Catalogue ids={['S4', 'R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8', 'R9']} title="Spatial metrics and reported experience" />
  </>;
}
