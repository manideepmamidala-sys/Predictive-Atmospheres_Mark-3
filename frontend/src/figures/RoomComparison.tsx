import type { Room } from '../lib/research';
import { Figure, Value } from '../ui';

export default function RoomComparison({ rooms }: { rooms: Room[] }) {
  const keys = [...new Set(rooms.flatMap(room => Object.keys(room.dimensions)))];
  return <Figure title="Room comparison" caption="Reported architectural and environmental metadata. Blank values reflect unavailable source fields, not zero. Source: generated room export.">
    {rooms.length ? <div className="table-wrap"><table className="data-table"><thead><tr><th scope="col">Parameter</th>{rooms.map(room => <th scope="col" key={room.id}>{room.id}</th>)}</tr></thead><tbody><tr><th scope="row">Experiment</th>{rooms.map(room => <td key={room.id}>{room.experiment}</td>)}</tr><tr><th scope="row">Space type</th>{rooms.map(room => <td key={room.id}>{room.space_type || 'Unavailable'}</td>)}</tr><tr><th scope="row">Illuminance</th>{rooms.map(room => <td key={room.id}><Value value={room.illuminance_lux} unit="lux" /></td>)}</tr><tr><th scope="row">CCT</th>{rooms.map(room => <td key={room.id}><Value value={room.cct_kelvin} unit="K" /></td>)}</tr>{keys.map(key => <tr key={key}><th scope="row">{key.replaceAll('_', ' ')}</th>{rooms.map(room => <td key={room.id}><Value value={room.dimensions[key]} /></td>)}</tr>)}</tbody></table></div> : <p>Select up to three rooms to compare.</p>}
  </Figure>;
}
