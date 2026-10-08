import { useMemo, useState } from 'react';
import manifest from '../../../data/renders/manifest.json';
import { useResearch } from '../lib/research';
import Panorama from '../figures/Panorama';
import RoomComparison from '../figures/RoomComparison';
import Circumplex from '../figures/Circumplex';
import { Notice, PageHeading, Section } from '../ui';

export default function Rooms() {
  const state = useResearch();
  const data = state.status === 'ready' ? state.data : null;
  const [experiment, setExperiment] = useState('all');
  const [type, setType] = useState('all');
  const [lighting, setLighting] = useState('all');
  const [selected, setSelected] = useState<string[]>([]);
  const [active, setActive] = useState(manifest.rooms[0]?.id || '');
  const lookup = useMemo(() => new Map(data?.rooms.map(room => [room.id, room]) || []), [data]);
  const types = [...new Set(data?.rooms.map(room => room.space_type).filter((item): item is string => !!item) || [])].sort();
  const lightingValues = [...new Set(data?.rooms.map(room => room.lighting).filter((item): item is string => !!item) || [])].sort();
  const shown = manifest.rooms.filter(room => (experiment === 'all' || String(room.experiment) === experiment) && (type === 'all' || lookup.get(room.id)?.space_type === type) && (lighting === 'all' || (lighting === 'unavailable' ? !lookup.get(room.id)?.lighting : lookup.get(room.id)?.lighting === lighting)));
  const activeAsset = manifest.rooms.find(room => room.id === active) || manifest.rooms[0];
  const compare = selected.map(id => lookup.get(id)).filter((item): item is NonNullable<typeof item> => !!item);
  const points = data?.rooms.filter(room => room.mean_affect).map(room => ({ id: room.id, label: room.id, position: room.mean_affect!, cct: room.cct_kelvin })) || [];
  const toggle = (id: string) => setSelected(current => current.includes(id) ? current.filter(item => item !== id) : current.length < 3 ? [...current, id] : current);
  return <><PageHeading eyebrow="Spatial archive" title="Rooms" intro="Browse the source-matched renders and compare the documented geometry and lighting metadata. The images show visual stimuli; reported environmental values were not calibrated to headset exposure." />
    <div className="toolbar"><label>Experiment<select value={experiment} onChange={event => setExperiment(event.target.value)}><option value="all">All experiments</option>{[...new Set(manifest.rooms.map(room => room.experiment))].map(n => <option key={n} value={n}>Experiment {n}</option>)}</select></label><label>Space type<select value={type} onChange={event => setType(event.target.value)}><option value="all">All types</option>{types.map(item => <option key={item}>{item}</option>)}</select></label><label>Recorded lighting<select value={lighting} onChange={event => setLighting(event.target.value)}><option value="all">All available states</option>{lightingValues.map(item => <option key={item}>{item}</option>)}{data && <option value="unavailable">Not recorded</option>}</select></label><span className="status">{shown.length} source renders shown · {selected.length}/3 selected for comparison</span></div>
    <div className="page-grid"><div className="reading"><Section title="Render archive"><div className="rooms-grid">{shown.map(asset => { const room = lookup.get(asset.id); return <article className="room-card" key={asset.id}><img src={asset.preview} alt={`Preview of ${asset.id}`} loading="lazy" /><div><h3>{asset.id}</h3><p>Experiment {asset.experiment}{room?.space_type ? ` · ${room.space_type}` : ''}</p><div className="toolbar"><button type="button" className="subtle" onClick={() => setActive(asset.id)} aria-label={`Explore ${asset.id}`}>Explore</button><label><input type="checkbox" checked={selected.includes(asset.id)} disabled={!selected.includes(asset.id) && selected.length >= 3} onChange={() => toggle(asset.id)} /> Compare</label></div></div></article>; })}</div>{!shown.length && <Notice title="No matching room"><p>Choose another experiment or space type.</p></Notice>}</Section>
      <Section title="What the metadata means"><p>Room IDs map directly to the preserved source render filenames. Early experiments have fewer measured spatial fields; blanks remain unavailable. CCT and illuminance are supplied environmental values and should not be read as measured visual exposure in VR.</p><p className="small-text">{manifest.method}</p></Section></div>
      <div className="figure-column">{activeAsset && <Panorama roomId={activeAsset.id} src={activeAsset.panorama} original={activeAsset.source} layout={activeAsset.layout} />}{selected.length > 0 && <RoomComparison rooms={compare} />}{data && <Circumplex points={points} caption="Per-room mean of complete-fusion positions only. The number of contributing trials varies by room; see trial records for partial or missing components." />}{!data && <Notice title="Room metrics unavailable"><p>{state.status === 'error' ? state.message : 'Loading generated research metrics.'} Render browsing remains available.</p></Notice>}</div></div></>;
}
