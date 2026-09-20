import React, { useState } from 'react';

export default function Settings() {
  const [t1Thresh, setT1Thresh] = useState(50.0);
  const [t2Thresh, setT2Thresh] = useState(30.0);
  const [readoutThresh, setReadoutThresh] = useState(0.05);

  const handleSave = (e) => {
    e.preventDefault();
    alert('Hardware thresholds saved locally.');
  };

  return (
    <div className="space-y-8 p-6">
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight text-white font-outfit">Hardware Settings</h1>
        <p className="text-slate-400">Configure Qubit Health Index (QHI) thresholds and weights configurations</p>
      </div>

      <div className="max-w-2xl glass-panel p-6">
        <form onSubmit={handleSave} className="space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">T1 Coherence Threshold (µs)</label>
              <input
                type="number"
                step="0.1"
                value={t1Thresh}
                onChange={(e) => setT1Thresh(Number(e.target.value))}
                className="form-input"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">T2 Coherence Threshold (µs)</label>
              <input
                type="number"
                step="0.1"
                value={t2Thresh}
                onChange={(e) => setT2Thresh(Number(e.target.value))}
                className="form-input"
                required
              />
            </div>

            <div className="sm:col-span-2">
              <label className="block text-sm font-medium text-slate-300 mb-2">Readout Error Threshold Rate</label>
              <input
                type="number"
                step="0.001"
                value={readoutThresh}
                onChange={(e) => setReadoutThresh(Number(e.target.value))}
                className="form-input"
                required
              />
            </div>
          </div>

          <button
            type="submit"
            className="glow-btn px-8"
          >
            Save Settings
          </button>
        </form>
      </div>
    </div>
  );
}
