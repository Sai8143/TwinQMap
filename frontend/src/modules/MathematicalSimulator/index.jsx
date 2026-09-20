import React, { useState, useEffect, useRef } from 'react';
import api from '../../services/api';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  Label
} from 'recharts';
import { 
  Activity, 
  Play, 
  Pause, 
  ChevronRight, 
  Database, 
  Info, 
  RefreshCw,
  Award,
  Square,
  Download
} from 'lucide-react';

export default function MathematicalSimulator() {
  const downloadReport = async (reportType, format = 'json') => {
    try {
      const response = await api.get('/reports/generate', {
        params: { report_type: reportType, report_format: format },
        responseType: 'blob'
      });
      const blob = new Blob([response.data], { type: response.headers['content-type'] });
      const link = document.createElement('a');
      link.href = window.URL.createObjectURL(blob);
      link.download = `${reportType}_report.${format}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (err) {
      console.error(err);
      alert('Failed to download report.');
    }
  };
  const [qubits, setQubits] = useState(5);
  const [epochs, setEpochs] = useState(100);
  const [status, setStatus] = useState({
    status: 'IDLE',
    current_epoch: 0,
    max_epochs: 100,
    qubit_count: 5,
    dataset_rows: 0,
    latest_metrics: null,
    latest_calibrations: []
  });
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]); // local history buffer to plot parameters
  const [showExplanation, setShowExplanation] = useState(false);
  const isInitializingRef = useRef(false);

  async function fetchStatus() {
    if (isInitializingRef.current) return;
    try {
      const res = await api.get('/training/status');
      setStatus(res.data);
      
      // If running or paused and has latest calibrations, append to history plot
      if (res.data.latest_calibrations.length > 0) {
        setHistory(prev => {
          const epoch = res.data.current_epoch;
          if (prev.some(h => h.epoch === epoch)) return prev;
          
          const row = { epoch };
          res.data.latest_calibrations.forEach(c => {
            row[`${c.qubit_id}_t1`] = c.t1;
            row[`${c.qubit_id}_t2`] = c.t2;
            row[`${c.qubit_id}_readout`] = c.readout_error;
          });
          return [...prev, row].slice(-40); // keep last 40 epochs for visibility
        });
      }
    } catch (err) {
      console.error(err);
    }
  }

  // Poll status
  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 1000);
    return () => clearInterval(interval);
  }, []);

  const handleStartSession = async (e) => {
    e.preventDefault();
    setLoading(true);
    isInitializingRef.current = true;
    setHistory([]);
    try {
      const res = await api.post('/training/start', null, {
        params: { qubit_count: qubits, max_epochs: epochs }
      });
      setStatus(res.data);
      setHistory([]); // clear again after start API completes to prevent race overlaps
    } catch (err) {
      console.error(err);
      alert('Error initializing research session');
    } finally {
      isInitializingRef.current = false;
      setLoading(false);
    }
  };

  const handlePlay = async () => {
    try {
      const res = await api.post('/training/resume');
      setStatus(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const handlePause = async () => {
    try {
      const res = await api.post('/training/pause');
      setStatus(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleStep = async () => {
    try {
      const res = await api.post('/training/step');
      setStatus(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const getStatusColor = () => {
    switch (status.status) {
      case 'RUNNING': return 'text-violet-400 bg-violet-500/10 border-violet-500/30 animate-pulse';
      case 'PAUSED': return 'text-yellow-400 bg-yellow-500/10 border-yellow-500/30';
      case 'COMPLETED': return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30';
      default: return 'text-slate-400 bg-slate-900/40 border-slate-800';
    }
  };

  return (
    <div className="space-y-8 p-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-white font-outfit">Mathematical Simulator</h1>
          <p className="text-slate-400">Control and monitor stateful, closed-loop training runs for qubit experiments 1-5</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex gap-2 print:hidden">
            <button
              onClick={() => downloadReport('training', 'json')}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold rounded-lg border border-slate-700 text-sm flex items-center gap-2 transition"
            >
              <Download className="h-4 w-4" /> JSON Report
            </button>
            <button
              onClick={() => window.print()}
              className="px-4 py-2 bg-violet-600 hover:bg-violet-500 text-white font-semibold rounded-lg text-sm flex items-center gap-2 transition shadow-lg shadow-violet-500/20"
            >
              <Download className="h-4 w-4" /> Print PDF
            </button>
          </div>
          <div className={`flex items-center gap-2 px-4 py-2 border rounded-full text-sm font-semibold transition ${getStatusColor()}`}>
            <Activity className="h-4 w-4" />
            <span>Status: {status.status}</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Configurations & Stateful Controls Column */}
        <div className="glass-panel p-6 space-y-6 h-fit">
          <h3 className="text-lg font-bold text-white font-outfit">Interactive controls</h3>

          {status.status === 'IDLE' || status.status === 'COMPLETED' ? (
            <form onSubmit={handleStartSession} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Qubit Configuration</label>
                <select
                  value={qubits}
                  onChange={(e) => setQubits(Number(e.target.value))}
                  className="form-input"
                >
                  {[1, 2, 3, 4, 5].map((n) => (
                    <option key={n} value={n}>{n} Active Qubits (Experiment {n})</option>
                  ))}
                  <option value={11}>11 Active Qubits (IonQ Aria Live Calibrations)</option>
                  <option value={25}>25 Active Qubits (IonQ Forte Live Calibrations)</option>
                  <option value={133}>133 Active Qubits (IBM Torino Live Tracking)</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Max Loop Epochs</label>
                <input
                  type="number"
                  min="10"
                  max="500"
                  value={epochs}
                  onChange={(e) => setEpochs(Number(e.target.value))}
                  className="form-input"
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="glow-btn w-full py-3"
              >
                {loading ? 'Initializing...' : 'Initialize Experiment'}
              </button>
            </form>
          ) : (
            <div className="space-y-4">
              <span className="text-slate-400 text-xs font-semibold uppercase block">Closed-Loop Controls</span>
              
              <div className="grid grid-cols-3 gap-3">
                {status.status === 'RUNNING' ? (
                  <button
                    onClick={handlePause}
                    className="p-3 bg-yellow-500/10 hover:bg-yellow-500/20 border border-yellow-500/30 text-yellow-400 rounded-lg flex flex-col items-center gap-1 font-semibold text-xs transition"
                  >
                    <Pause className="h-4 w-4" />
                    Pause
                  </button>
                ) : (
                  <button
                    onClick={handlePlay}
                    className="p-3 bg-violet-500/10 hover:bg-violet-500/20 border border-violet-500/30 text-violet-400 rounded-lg flex flex-col items-center gap-1 font-semibold text-xs transition"
                  >
                    <Play className="h-4 w-4 fill-current" />
                    Play
                  </button>
                )}

                <button
                  onClick={handleStep}
                  disabled={status.status === 'RUNNING'}
                  className="p-3 bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/30 text-cyan-400 rounded-lg flex flex-col items-center gap-1 font-semibold text-xs transition disabled:opacity-50"
                >
                  <ChevronRight className="h-4 w-4" />
                  Step Epoch
                </button>

                <button
                  onClick={() => setStatus({ ...status, status: 'IDLE' })}
                  className="p-3 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 rounded-lg flex flex-col items-center gap-1 font-semibold text-xs transition"
                >
                  <Square className="h-4 w-4 fill-current" />
                  Reset
                </button>
              </div>
            </div>
          )}

          {/* Engine Parameters */}
          <div className="p-4 bg-slate-900/40 border border-slate-800 rounded-lg space-y-3 text-xs">
            <div className="flex items-center gap-2 text-cyan-400 font-semibold">
              <Info className="h-4 w-4" />
              <span>Experiment Metadata</span>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-slate-500">Experiment ID:</span>
                <span className="font-mono text-slate-300">{status.qubit_count} Qubits</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">ML Retrained:</span>
                <span className="font-mono text-slate-300">{status.current_epoch >= 5 ? 'Yes (Epoch >= 5)' : 'Waiting...'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Models Fitted:</span>
                <span className="font-mono text-slate-300">RF, GBDT, MLP, XGBoost</span>
              </div>
            </div>
          </div>

          {/* Quantum Physics Glossary */}
          <div className="p-4 bg-slate-900/40 border border-slate-800 rounded-lg space-y-3 text-xs">
            <div className="flex items-center gap-2 text-purple-400 font-semibold">
              <Info className="h-4 w-4" />
              <span>Quantum Parameter Glossary</span>
            </div>
            <div className="space-y-3 text-slate-400">
              <div>
                <strong className="text-slate-200">Epoch:</strong> A single sequence step in the continuous time-evolution simulation of the quantum hardware parameters.
              </div>
              <div>
                <strong className="text-slate-200">T₁ Longitudinal Relaxation (µs):</strong> The thermal decay time constant for a qubit to relax from excited state |1⟩ to ground state |0⟩.
              </div>
              <div>
                <strong className="text-slate-200">T₂ Transverse Dephasing (µs):</strong> The phase coherence lifetime indicating how long a qubit stays in a superposition state.
              </div>
              <div>
                <strong className="text-slate-200">Readout Error:</strong> The measurement error rate indicating the probability of reading the incorrect qubit basis state.
              </div>
              <div>
                <strong className="text-slate-200">Frequency (GHz):</strong> Operating microwave frequency needed to address and transition the physical qubit.
              </div>
              <div>
                <strong className="text-slate-200">Temperature (mK):</strong> Cryogenic temperature in milli-Kelvins inside the dilution refrigerator.
              </div>
            </div>
          </div>
        </div>

        {/* Live Tracking Engine */}
        <div className="glass-panel p-6 lg:col-span-2 space-y-6">
          <h3 className="text-lg font-bold text-white font-outfit">Live telemetry</h3>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="p-4 bg-slate-900/20 border border-slate-800/80 rounded-lg">
              <span className="text-slate-500 text-xs uppercase block">Current Epoch</span>
              <span className="text-2xl font-bold font-mono text-cyan-400 mt-1 block">#{status.current_epoch}</span>
            </div>
            <div className="p-4 bg-slate-900/20 border border-slate-800/80 rounded-lg">
              <span className="text-slate-500 text-xs uppercase block">Max Epochs</span>
              <span className="text-2xl font-bold font-mono text-purple-400 mt-1 block">#{status.max_epochs}</span>
            </div>
            <div className="p-4 bg-slate-900/20 border border-slate-800/80 rounded-lg">
              <span className="text-slate-500 text-xs uppercase block">Dataset Size</span>
              <span className="text-2xl font-bold font-mono text-fuchsia-400 mt-1 block">{status.dataset_rows} rows</span>
            </div>
            <div className="p-4 bg-slate-900/20 border border-slate-800/80 rounded-lg">
              <span className="text-slate-500 text-xs uppercase block">Qubits Count</span>
              <span className="text-2xl font-bold font-mono text-emerald-400 mt-1 block">{status.qubit_count} Q</span>
            </div>
          </div>

          {/* Model Validation Metrics snippet */}
          {status.latest_metrics && (
            <div className="p-4 bg-slate-900/40 border border-slate-800 rounded-lg flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-emerald-500/10 text-emerald-400 rounded-lg">
                  <Award className="h-5 w-5" />
                </div>
                <div>
                  <h4 className="text-sm font-bold text-white font-outfit">Epoch #{status.latest_metrics.epoch_number} ML Retrained Metrics</h4>
                  <p className="text-xs text-slate-400">Models successfully retrained on growing {status.dataset_rows} rows dataset</p>
                </div>
              </div>
              <div className="text-right font-mono text-xs space-y-1">
                <div>MAE (Mean Absolute Error): <span className="text-cyan-400 font-bold">{status.latest_metrics.mae != null ? status.latest_metrics.mae.toFixed(5) : '—'}</span></div>
                <div>R² Score (Coefficient of Determination): <span className="text-emerald-400 font-bold">{status.latest_metrics.r2 != null ? `${(status.latest_metrics.r2 * 100).toFixed(2)}%` : '—'}</span></div>
              </div>
            </div>
          )}

          {/* Parameters Evolution Chart */}
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <h4 className="text-sm font-semibold text-slate-300">Live Qubit Coherence parameter evolution (T1 decay times) {status.qubit_count > 5 && <span className="text-xs text-slate-500 font-normal ml-1">(showing first 5 qubits)</span>}</h4>
              <button
                onClick={() => setShowExplanation(!showExplanation)}
                className="px-3 py-1 bg-slate-800 hover:bg-slate-700 text-xs text-slate-300 font-semibold rounded border border-slate-700 transition"
              >
                {showExplanation ? 'Hide Interpretation' : 'Explain Graph Dynamics'}
              </button>
            </div>
            <div className="h-64 w-full">
              {history.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart 
                    data={history.map(h => {
                      const mapped = { ...h };
                      Object.keys(h).forEach(k => {
                        if (k.endsWith('_t1')) {
                          mapped[`${k}_sec`] = h[k] / 1000000;
                        }
                      });
                      return mapped;
                    })} 
                    margin={{ top: 15, right: 25, left: 30, bottom: 20 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                    <XAxis 
                      dataKey="epoch" 
                      stroke="#94a3b8" 
                      height={45}
                    >
                      <Label value="Simulation Epoch Number" offset={-2} position="insideBottom" fill="#94a3b8" fontSize={11} fontWeight="bold" />
                    </XAxis>
                    <YAxis 
                      stroke="#94a3b8" 
                      width={75}
                    >
                      <Label value="T1 Coherence Decay (seconds)" angle={-90} position="insideLeft" offset={10} fill="#94a3b8" fontSize={11} fontWeight="bold" style={{ textAnchor: 'middle' }} />
                    </YAxis>
                    <Tooltip 
                      contentStyle={{ background: '#0f172a', borderColor: '#334155' }} 
                      formatter={(value, name) => [`${value.toFixed(6)} s`, name]}
                    />
                    <Legend />
                    {Array.from({ length: Math.min(5, status.qubit_count) }).map((_, i) => (
                      <Line 
                        key={i} 
                        type="monotone" 
                        dataKey={`Q${i}_t1_sec`} 
                        stroke={['#38bdf8', '#c084fc', '#f472b6', '#fbbf24', '#34d399'][i]} 
                        strokeWidth={2} 
                        name={`Q${i} T1 (seconds)`} 
                        dot={false}
                      />
                    ))}
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex flex-col items-center justify-center h-full border border-dashed border-slate-800 rounded-lg text-slate-500 text-sm">
                  <span>Initialize the experiment on the left to start telemetry tracking.</span>
                </div>
              )}
            </div>
            {showExplanation && (
              <div className="p-4 bg-slate-900/50 border border-slate-800 rounded-lg text-xs text-slate-400 space-y-2">
                <p>
                  <strong>What is happening:</strong> This graph displays the continuous exponential decay of longitudinal coherence lifetimes (\(T_1\)) across simulated physical qubits. You will notice sinusoidal ripples superimposed on the curves, which represent ambient thermal fluctuations.
                </p>
                <p>
                  <strong>Purpose:</strong> The simulator generates this realistic parameters evolution dataset to provide telemetry calibration inputs for training our machine learning regressors offline.
                </p>
                <p>
                  <strong>Conclusion:</strong> Physical parameters drift continuously due to environmental noise. Capturing this drift sequence in the calibrations database forms the foundation of self-learning digital twins.
                </p>
              </div>
            )}
          </div>

          {/* Current Epoch Generated Calibrations table */}
          {status.latest_calibrations.length > 0 && (
            <div className="space-y-3">
              <h4 className="text-sm font-semibold text-slate-300">Epoch #{status.current_epoch} Generated Calibration Ground Truth</h4>
              <div className="overflow-x-auto border border-slate-800 rounded-lg max-h-80 overflow-y-auto">
                <table className="w-full text-left border-collapse text-xs">
                  <thead>
                    <tr className="border-b border-slate-800 bg-slate-950/40 text-slate-400 font-semibold">
                      <th className="p-3">Qubit ID</th>
                      <th className="p-3">T1 (µs)</th>
                      <th className="p-3">T2 (µs)</th>
                      <th className="p-3">Readout Error</th>
                      <th className="p-3">Frequency (GHz)</th>
                      <th className="p-3">Temp (K)</th>
                    </tr>
                  </thead>
                  <tbody>
                    {status.latest_calibrations.map((c) => (
                      <tr key={c.qubit_id} className="border-b border-slate-800/40 hover:bg-slate-900/10">
                        <td className="p-3 font-mono text-cyan-400">{c.qubit_id}</td>
                        <td className="p-3 font-mono">{c.t1.toFixed(3)}</td>
                        <td className="p-3 font-mono">{c.t2.toFixed(3)}</td>
                        <td className="p-3 font-mono">{(c.readout_error * 100).toFixed(3)}%</td>
                        <td className="p-3 font-mono">{c.frequency.toFixed(4)}</td>
                        <td className="p-3 font-mono">{c.temperature.toFixed(4)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
