import { useEffect, useState, type FormEvent } from 'react';
import { Link } from 'react-router-dom';
import manifest from '../../../data/renders/manifest.json';
import Massing from '../figures/Massing';
import { useResearch } from '../lib/research';
import { getMeta, optimizeRoom, predictRoom, type AffectTarget, type MetaResponse, type OptimizeResponse, type PredictResponse, type RoomInput } from '../api/client';
import { Notice, PageHeading, Section, Value, modelStatusLabel } from '../ui';

type NumericField = { name: keyof RoomInput; label: string; unit?: string; min: number; max?: number; step?: string; required?: boolean };
const dimensions: NumericField[] = [
  { name: 'length', label: 'Length', unit: 'm', min: 0.001, max: 100, required: true },
  { name: 'width', label: 'Width', unit: 'm', min: 0.001, max: 100, required: true },
  { name: 'height', label: 'Height', unit: 'm', min: 0.001, max: 30, required: true },
];
const optional: NumericField[] = [
  { name: 'num_doors', label: 'Door count', min: 0, max: 100, step: '1' },
  { name: 'door_area', label: 'Total door area', unit: 'm²', min: 0 },
  { name: 'num_windows', label: 'Window count', min: 0, max: 100, step: '1' },
  { name: 'window_area', label: 'Total window area', unit: 'm²', min: 0 },
  { name: 'daylight_factor', label: 'Daylight factor', unit: '%', min: 0, max: 100 },
  { name: 'illuminance', label: 'Illuminance', unit: 'lux', min: 0 },
  { name: 'cct', label: 'CCT', unit: 'K', min: 0.001 },
  { name: 'walkable_floor_area', label: 'Walkable floor area', unit: 'm²', min: 0 },
];
const spaceTypes: NonNullable<RoomInput['space_type']>[] = ['General', 'Bedroom', 'Living Room', 'Workplace', 'Classroom', 'Cafeteria'];
function fieldValue(form: FormData, name: string): number | null {
  const text = String(form.get(name) ?? '').trim();
  return text === '' ? null : Number(text);
}
function input(field: NumericField) {
  return <label className="field" key={field.name}>{field.label}{field.unit && <small>{field.unit}</small>}
    <input name={field.name} type="number" step={field.step || 'any'} min={field.min} max={field.max} required={field.required} />
  </label>;
}
function nearestRender(roomId: string | null) {
  return manifest.rooms.find(room => room.id === roomId);
}

export default function Simulator() {
  const research = useResearch();
  const model = research.status === 'ready' ? research.data.model : null;
  const [live, setLive] = useState<MetaResponse | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [prediction, setPrediction] = useState<PredictResponse | null>(null);
  const [optimization, setOptimization] = useState<OptimizeResponse | null>(null);
  const [geometry, setGeometry] = useState<{ length: number; width: number; height: number } | null>(null);
  useEffect(() => { let active = true; getMeta().then(meta => { if (active) setLive(meta); }).catch(() => { if (active) setLive(null); }); return () => { active = false; }; }, []);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const action = (event.nativeEvent as SubmitEvent).submitter?.getAttribute('value') || 'predict';
    const form = new FormData(event.currentTarget);
    const targetValence = fieldValue(form, 'target_valence'), targetArousal = fieldValue(form, 'target_arousal');
    if (targetValence == null || targetArousal == null || ![targetValence, targetArousal].every(value => Number.isFinite(value) && value >= -1 && value <= 1)) {
      setError('Choose target valence and arousal between −1 and 1.'); return;
    }
    const target: AffectTarget = { valence: targetValence, arousal: targetArousal };
    const day = String(form.get('day_or_night') || '') as RoomInput['day_or_night'];
    const space = String(form.get('space_type') || '') as RoomInput['space_type'];
    setBusy(true); setError(''); setPrediction(null); setOptimization(null);
    try {
      if (action === 'optimize') {
        setOptimization(await optimizeRoom({ target, day_or_night: day || null, space_type: space || null, budget: 500, n_candidates: 5, seed: 2718 }));
      } else {
        const room: RoomInput = {
          length: Number(form.get('length')), width: Number(form.get('width')), height: Number(form.get('height')),
          num_doors: fieldValue(form, 'num_doors'), door_area: fieldValue(form, 'door_area'),
          num_windows: fieldValue(form, 'num_windows'), window_area: fieldValue(form, 'window_area'),
          daylight_factor: fieldValue(form, 'daylight_factor'), illuminance: fieldValue(form, 'illuminance'),
          cct: fieldValue(form, 'cct'), walkable_floor_area: fieldValue(form, 'walkable_floor_area'),
          day_or_night: day || null, space_type: space || null,
        };
        setPrediction(await predictRoom(room, target));
      }
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'The prediction service is unavailable.');
    } finally { setBusy(false); }
  }
  function updateGeometry(event: FormEvent<HTMLFormElement>) {
    const form = new FormData(event.currentTarget);
    const length = Number(form.get('length')), width = Number(form.get('width')), height = Number(form.get('height'));
    setGeometry([length, width, height].every(value => Number.isFinite(value) && value > 0) ? { length, width, height } : null);
  }
  const nearest = nearestRender(prediction?.support.nearest_room_id ?? null);
  return <><PageHeading eyebrow="Experimental demonstrator" title="Room simulator" intro="Enter physical room parameters and choose the affective position you want to explore. Predictions and suggestions depend on a separately evaluated model; they are not measured experiences or design recommendations." />
    <Notice title={`Model status: ${model ? modelStatusLabel(model.status) : 'Unavailable'}`} warning={!model || model.status !== 'ready'}>
      <p>{model?.explanation || 'The validated model report has not been published.'} <Link to="/model">Read the evaluation</Link>.</p>
      {model?.status === 'not_better_than_baseline' && <p className="small-text">Held-out error is not better than the reported baseline. Use this only to inspect an experimental model response.</p>}
      <p className="small-text">Live service: {live ? (live.ready ? `ready (${live.model_status})` : `not ready (${live.model_status})`) : 'offline or starting'}.</p>
    </Notice>
    <div className="page-grid"><div className="reading"><Section title="Physical room inputs">
      <form onSubmit={submit} onInput={updateGeometry}>
        <div className="form-grid">{dimensions.map(input)}{optional.map(input)}
          <label className="field">Time of day<select name="day_or_night"><option value="">Unspecified</option><option value="Day">Day</option><option value="Night">Night</option></select></label>
          <label className="field">Space type<select name="space_type"><option value="">Unspecified</option>{spaceTypes.map(value => <option key={value}>{value}</option>)}</select></label>
        </div>
        <h3 style={{ marginTop: '2rem' }}>Your target</h3><p>Target coordinates are your choice. Room type does not set them automatically.</p>
        <div className="form-grid"><label className="field">Target valence<input name="target_valence" type="number" min="-1" max="1" step="0.01" required /></label>
          <label className="field">Target arousal<input name="target_arousal" type="number" min="-1" max="1" step="0.01" required /></label></div>
        <div className="toolbar"><button type="submit" value="predict" disabled={busy}>Predict response</button>
          <button type="submit" value="optimize" formNoValidate className="subtle" disabled={busy}>Suggest rooms</button></div>
      </form>
      <p className="small-text">Door and window areas are total opening areas. Suggest rooms uses the target and optional space/time restrictions, not the dimensions above. The search is seeded and bounded. Blank observations remain missing. Neuro-Score measures distance from your selected target on a 0–1 scale; it is not confidence or a success probability.</p>
    </Section></div>
      <div className="figure-column"><Massing geometry={geometry} /><div className="card" aria-live="polite"><h3>Response</h3>
        {busy && <p role="status">Contacting prediction service…</p>}
        {error && <p className="status error" role="alert">{error}</p>}
        {prediction && <><p>Predicted valence: <strong><Value value={prediction.prediction.valence} /></strong></p>
          <p>Predicted arousal: <strong><Value value={prediction.prediction.arousal} /></strong></p>
          <p>Neuro-Score at your target: <strong><Value value={prediction.prediction.neuro_score} /></strong></p>
          <p className="small-text">Model: {modelStatusLabel(prediction.model_status)}. Studied support: {prediction.support.status}{prediction.support.reason ? ` — ${prediction.support.reason}` : ''}. {prediction.prediction.projected ? 'Raw output was projected into the declared affect domain before scoring.' : 'Raw output was inside the declared affect domain.'}</p>
          {prediction.limitations.map((item, i) => <p className="small-text" key={i}>{item}</p>)}
          {nearest && <div className="room-card"><img src={nearest.preview} alt={`Preview of nearest studied room ${nearest.id}`} /><div><h3>Nearest studied room: {nearest.id}</h3><p>This is a studied neighbor, not the simulated room.</p></div></div>}
        </>}
        {optimization && (optimization.candidates.length ? <div className="table-wrap"><table className="data-table"><thead><tr><th scope="col">Candidate</th><th scope="col">Dimensions (m)</th><th scope="col">Space / time</th><th scope="col">Illuminance / CCT</th><th scope="col">Neuro-Score</th><th scope="col">Support</th><th scope="col">Nearest studied room</th></tr></thead>
          <tbody>{optimization.candidates.map((item, i) => <tr key={i}><th scope="row">{i + 1}</th><td>{item.room.length.toFixed(2)} × {item.room.width.toFixed(2)} × {item.room.height.toFixed(2)}</td><td>{item.room.space_type || 'Unspecified'} / {item.room.day_or_night || 'unspecified'}</td><td><Value value={item.room.illuminance} unit="lux" /> / <Value value={item.room.cct} unit="K" /></td><td><Value value={item.prediction.neuro_score} /></td><td>{item.support.status}</td><td>{item.support.nearest_room_id || 'Unavailable'}</td></tr>)}</tbody></table></div>
          : <p>{optimization.reason || 'No supported candidate was found within the search budget.'}</p>)}
        {!busy && !error && !prediction && !optimization && <p className="small-text">A request result will appear here. An unavailable model or offline service will explain its status.</p>}
      </div></div></div></>;
}
