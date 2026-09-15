import React, { useEffect } from 'react';
import Plot from 'react-plotly.js';
import { usePlatformStore } from '../store/usePlatformStore';

const InputSlider = ({ label, field, min, max, step = 0.1, unit = '' }: any) => {
  const value = usePlatformStore((state: any) => state[field]);
  const setField = usePlatformStore((state: any) => state.setField);
  const error422 = usePlatformStore((state) => state.error422);

  return (
    <div className="mb-4 w-full">
      <div className="flex justify-between items-center mb-1">
        <label className="text-xs font-bold uppercase tracking-wider opacity-80">{label}</label>
        <span className="text-sm font-mono">{value} {unit}</span>
      </div>
      <input 
        type="range" 
        min={min} 
        max={max} 
        step={step} 
        value={value} 
        onChange={(e) => setField(field, parseFloat(e.target.value))}
        className="w-full accent-white h-1 bg-white/20 appearance-none rounded-none outline-none"
      />
      {error422 && <span className="text-red-500 text-xs mt-1 block">{error422}</span>}
    </div>
  );
};

const InteractiveStudio: React.FC = () => {
  const { 
    predicted_neuro_score, 
    predicted_valence, 
    predicted_arousal, 
    confidence_pct, 
    atmospheric_label,
    fetchPrediction,
    setField,
    space_use_type
  } = usePlatformStore();

  useEffect(() => {
    fetchPrediction();
  }, [fetchPrediction]);

  const scatterTrace = {
    x: predicted_valence !== null ? [predicted_valence] : [0],
    y: predicted_arousal !== null ? [predicted_arousal] : [0],
    mode: 'markers',
    type: 'scatter',
    marker: { size: 24, color: '#FFFFFF', line: { width: 2, color: '#000000' } },
    name: 'Current Prediction'
  };

  const layout = {
    paper_bgcolor: 'transparent',
    plot_bgcolor: 'transparent',
    font: { color: '#FFFFFF' },
    xaxis: { title: 'Valence', range: [-1, 1], gridcolor: 'rgba(255,255,255,0.1)', zerolinecolor: 'rgba(255,255,255,0.4)' },
    yaxis: { title: 'Arousal', range: [-1, 1], gridcolor: 'rgba(255,255,255,0.1)', zerolinecolor: 'rgba(255,255,255,0.4)' },
    margin: { l: 40, r: 20, t: 20, b: 40 },
    showlegend: false
  };

  return (
    <section className="w-full min-h-screen grid grid-cols-1 md:grid-cols-2">
      {/* Left Column: Inputs */}
      <div className="p-8 border-b md:border-b-0 md:border-r border-border overflow-y-auto">
        <h2 className="text-2xl font-bold uppercase tracking-widest mb-8">Spatial Parameters</h2>
        
        <div className="space-y-6">
          <div>
            <h3 className="text-sm border-b border-border pb-1 mb-4 uppercase tracking-widest text-white/50">Geometry</h3>
            <InputSlider label="Length" field="length_m" min={2.0} max={30.0} unit="m" />
            <InputSlider label="Width" field="width_m" min={2.0} max={30.0} unit="m" />
            <InputSlider label="Height" field="height_m" min={2.0} max={10.0} unit="m" />
            <InputSlider label="Volume" field="room_volume_m3" min={10.0} max={1000.0} step={1} unit="m³" />
          </div>

          <div>
            <h3 className="text-sm border-b border-border pb-1 mb-4 uppercase tracking-widest text-white/50">Openings</h3>
            <InputSlider label="Num Doors" field="num_doors" min={0} max={10} step={1} />
            <InputSlider label="Door Area" field="door_area_m2" min={0.0} max={20.0} unit="m²" />
            <InputSlider label="Num Windows" field="num_windows" min={0} max={20} step={1} />
            <InputSlider label="Window Area" field="window_area_m2" min={0.0} max={100.0} unit="m²" />
          </div>

          <div>
            <h3 className="text-sm border-b border-border pb-1 mb-4 uppercase tracking-widest text-white/50">Atmospherics</h3>
            <InputSlider label="Daylight Factor" field="daylight_factor_pct" min={0.0} max={10.0} unit="%" />
            <InputSlider label="Illuminance" field="illuminance_lux" min={0} max={2000} step={10} unit="lux" />
            <InputSlider label="Color Temp" field="cct_k" min={2000} max={6500} step={100} unit="K" />
            <InputSlider label="Walkable Area" field="walkable_floor_area_m2" min={0.0} max={500.0} unit="m²" />
          </div>

          <div>
            <h3 className="text-sm border-b border-border pb-1 mb-4 uppercase tracking-widest text-white/50">Context</h3>
            <label className="text-xs font-bold uppercase tracking-wider opacity-80 block mb-2">Space Type</label>
            <select 
              value={space_use_type}
              onChange={(e) => setField('space_use_type', e.target.value)}
              className="w-full bg-transparent border border-border p-2 text-white outline-none rounded-none"
            >
              <option value="Bedroom">Bedroom</option>
              <option value="Living Room">Living Room</option>
              <option value="Workplace">Workplace</option>
              <option value="Classroom">Classroom</option>
              <option value="Cafeteria">Cafeteria</option>
            </select>
          </div>
        </div>
      </div>

      {/* Right Column: Outputs */}
      <div className="p-8 flex flex-col justify-start">
        <h2 className="text-2xl font-bold uppercase tracking-widest mb-8">Prediction Output</h2>
        
        <div className="grid grid-cols-2 gap-4 mb-8">
          <div className="border border-border p-6 text-center">
            <div className="text-xs font-bold uppercase tracking-widest opacity-50 mb-2">Neuro-Score</div>
            <div className="text-5xl font-mono">{predicted_neuro_score !== null ? predicted_neuro_score.toFixed(3) : '---'}</div>
          </div>
          <div className="border border-border p-6 text-center">
            <div className="text-xs font-bold uppercase tracking-widest opacity-50 mb-2">Confidence</div>
            <div className="text-5xl font-mono">{confidence_pct !== null ? `${confidence_pct.toFixed(1)}%` : '---'}</div>
          </div>
        </div>

        <div className="w-full border border-border p-4 mb-4 bg-[#141820] flex-grow flex items-center justify-center">
          <Plot
            data={[scatterTrace]}
            layout={layout as any}
            useResizeHandler={true}
            style={{ width: '100%', height: '100%', minHeight: '350px' }}
            config={{ displayModeBar: false }}
          />
        </div>

        <div className="border border-border p-4 text-center">
          <div className="text-xs font-bold uppercase tracking-widest opacity-50 mb-1">Atmosphere</div>
          <div className="text-xl tracking-widest uppercase">{atmospheric_label || 'COMPUTING...'}</div>
        </div>
      </div>
    </section>
  );
};

export default InteractiveStudio;
