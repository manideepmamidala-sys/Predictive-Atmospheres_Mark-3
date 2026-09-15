import React from 'react';
import Plot from 'react-plotly.js';

const FindingsVisualizer: React.FC = () => {
  // Placeholder data for Findings Visualizer
  const trace1 = {
    x: [-0.5, 0.2, 0.8, -0.1, 0.4, 0.9],
    y: [0.1, 0.6, -0.4, 0.2, 0.7, -0.1],
    mode: 'markers',
    type: 'scatter',
    marker: { size: 12, color: 'rgba(255, 255, 255, 0.7)' },
    name: 'Observed Data'
  };

  const layout = {
    paper_bgcolor: 'transparent',
    plot_bgcolor: 'transparent',
    font: { color: '#FFFFFF' },
    xaxis: { title: 'Valence (Pleasure)', range: [-1, 1], gridcolor: 'rgba(255,255,255,0.1)', zerolinecolor: 'rgba(255,255,255,0.3)' },
    yaxis: { title: 'Arousal (Energy)', range: [-1, 1], gridcolor: 'rgba(255,255,255,0.1)', zerolinecolor: 'rgba(255,255,255,0.3)' },
    margin: { l: 50, r: 20, t: 30, b: 50 },
    showlegend: false
  };

  return (
    <section className="w-full py-24 px-8 border-b border-border flex flex-col items-center">
      <div className="max-w-4xl w-full">
        <h2 className="text-3xl font-bold mb-8 uppercase tracking-wide text-center">Target Density Field</h2>
        <div className="w-full border border-border p-4 bg-[#141820]">
          <Plot
            data={[trace1]}
            layout={layout as any}
            useResizeHandler={true}
            style={{ width: '100%', height: '400px' }}
            config={{ displayModeBar: false }}
          />
        </div>
      </div>
    </section>
  );
};

export default FindingsVisualizer;
