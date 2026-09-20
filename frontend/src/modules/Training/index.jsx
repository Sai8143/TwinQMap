import React, { useState, useEffect } from 'react';
import api from '../../services/api';
import { Download } from 'lucide-react';
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

export default function Training() {
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
  const [loading, setLoading] = useState(false);
  const [metrics, setMetrics] = useState([]);
  const [statusMessage, setStatusMessage] = useState('');
  const [activeTab, setActiveTab] = useState('metrics'); // 'metrics' or 'charts'
  
  const [runs, setRuns] = useState([]);
  const [selectedRunId, setSelectedRunId] = useState('');
  const [showExplanation, setShowExplanation] = useState(false);

  async function fetchRuns(targetQubits) {
    try {
      const res = await api.get('/training/runs', { params: { qubit_count: targetQubits } });
      const runsList = res.data.runs || [];
      setRuns(runsList);
      if (runsList.length > 0) {
        setSelectedRunId(runsList[0]);
      } else {
        setSelectedRunId('');
        setMetrics([]);
      }
    } catch (err) {
      console.error("Failed to fetch runs list", err);
    }
  }

  async function fetchMetrics(runId) {
    try {
      const activeRun = runId || selectedRunId;
      if (!activeRun) return;
      const res = await api.get('/training/metrics', { 
        params: { 
          run_id: activeRun,
          qubit_count: qubits,
          limit: 150 
        } 
      });
      setMetrics(res.data);
    } catch (err) {
      console.error(err);
    }
  }

  // Load runs on qubit configuration changes
  useEffect(() => {
    fetchRuns(qubits);
  }, [qubits]);

  // Load metrics when run ID changes
  useEffect(() => {
    if (selectedRunId) {
      fetchMetrics(selectedRunId);
    }
  }, [selectedRunId]);

  // Constantly poll active run and status parameters
  useEffect(() => {
    // Check initial state
    api.get('/training/status').then(res => {
      if (res.data.status === 'RUNNING') {
        setLoading(true);
        setStatusMessage('Simulation running. Autonomic learning loop active in background...');
        if (res.data.run_id) {
          setSelectedRunId(res.data.run_id);
        }
      } else if (res.data.status === 'COMPLETED') {
        setLoading(false);
        setStatusMessage('Self-learning loop run finished compiling.');
      }
    }).catch(console.error);

    const interval = setInterval(() => {
      api.get('/training/status').then(res => {
        if (res.data.status === 'COMPLETED' || res.data.status === 'IDLE') {
          setLoading(false);
          setStatusMessage('Self-learning loop run finished compiling.');
        } else if (res.data.status === 'RUNNING') {
          setLoading(true);
          setStatusMessage('Simulation running. Autonomic learning loop active in background...');
          if (res.data.run_id) {
            setSelectedRunId(res.data.run_id);
          }
        }
      }).catch(console.error);

      if (selectedRunId) {
        fetchMetrics(selectedRunId);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [selectedRunId, qubits]);

  const handleRunSimulation = async (e) => {
    e.preventDefault();
    setLoading(true);
    setStatusMessage('Simulation triggered. Autonomic learning loop active in background...');
    try {
      const res = await api.post('/training/run', null, {
        params: { qubit_count: qubits, max_epochs: epochs }
      });
      if (res.data.run_id) {
        setSelectedRunId(res.data.run_id);
        setRuns(prev => {
          if (!prev.includes(res.data.run_id)) {
            return [res.data.run_id, ...prev];
          }
          return prev;
        });
      }
    } catch (err) {
      console.error(err);
      setStatusMessage('Simulation run failed.');
      setLoading(false);
    }
  };

  const handleForceReset = async () => {
    if (!window.confirm("Are you sure you want to force reset the simulation loop? This will clear any active running state.")) {
      return;
    }
    try {
      await api.post('/training/reset');
      setLoading(false);
      setStatusMessage('Simulation runner forcefully reset to IDLE.');
      fetchRuns(qubits);
    } catch (err) {
      console.error(err);
      alert('Failed to reset simulation runner.');
    }
  };

  const latestStats = metrics[metrics.length - 1] || null;

  return (
    <div className="space-y-8 p-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-white font-outfit">Autonomous Self-Learning</h1>
          <p className="text-slate-400">Completely offline mathematical NISQ qubit drift simulation and model evaluation pipeline</p>
        </div>
        <div className="flex gap-2 print:hidden">
          <button
            onClick={() => downloadReport('training', 'json')}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold rounded-lg border border-slate-700 text-sm flex items-center gap-2 transition"
          >
            <Download className="h-4 w-4" /> JSON Report
          </button>
          <button
            onClick={() => downloadReport('training', 'csv')}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold rounded-lg border border-slate-700 text-sm flex items-center gap-2 transition"
          >
            <Download className="h-4 w-4" /> CSV Report
          </button>
          <button
            onClick={() => window.print()}
            className="px-4 py-2 bg-violet-600 hover:bg-violet-500 text-white font-semibold rounded-lg text-sm flex items-center gap-2 transition shadow-lg shadow-violet-500/20"
          >
            <Download className="h-4 w-4" /> Print PDF
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Configurations Column */}
        <div className="glass-panel p-6 space-y-6 h-fit">
          <h3 className="text-lg font-bold text-white font-outfit">Control panel</h3>
          
          <form onSubmit={handleRunSimulation} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Qubit Count (Experiment Configuration)</label>
              <select
                value={qubits}
                onChange={(e) => setQubits(Number(e.target.value))}
                className="form-input"
              >
                {[1, 2, 3, 4, 5].map((n) => (
                  <option key={n} value={n}>{n} Qubits (Experiment {n})</option>
                ))}
                <option value={11}>11 Qubits (IonQ Aria Live Calibrations)</option>
                <option value={25}>25 Qubits (IonQ Forte Live Calibrations)</option>
                <option value={133}>133 Qubits (IBM Torino Live Tracking)</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Simulation Run Epochs</label>
              <input
                type="number"
                min="10"
                max="500"
                value={epochs}
                onChange={(e) => setEpochs(Number(e.target.value))}
                className="form-input"
              />
            </div>

            {runs.length > 0 && (
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Historical Run Sessions (Date/Time)</label>
                <select
                  value={selectedRunId}
                  onChange={(e) => setSelectedRunId(e.target.value)}
                  className="form-input"
                >
                  {runs.map((r) => (
                    <option key={r} value={r}>{r}</option>
                  ))}
                </select>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="glow-btn w-full py-3"
            >
              {loading ? 'Learning in Progress...' : 'Start Self-Learning Loop'}
            </button>
            {loading && (
              <button
                type="button"
                onClick={handleForceReset}
                className="w-full py-2 border border-rose-500/30 bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 font-semibold rounded-lg text-sm transition mt-2"
              >
                Force Reset Runner
              </button>
            )}
          </form>

          {statusMessage && (
            <div className="p-3 bg-violet-500/10 border border-violet-500/30 text-violet-300 rounded-lg text-sm text-center font-medium">
              {statusMessage}
            </div>
          )}
        </div>

        {/* Visualizations Column */}
        <div className="glass-panel p-6 lg:col-span-2 space-y-6">
          <div className="flex justify-between items-center border-b border-slate-800 pb-4">
            <h3 className="text-lg font-bold text-white font-outfit">Real-time learning stats</h3>
            <div className="flex gap-2">
              <button 
                onClick={() => setActiveTab('metrics')} 
                className={`px-3 py-1 rounded text-sm font-semibold transition ${activeTab === 'metrics' ? 'bg-cyan-500/20 text-cyan-400' : 'text-slate-400 hover:text-slate-200'}`}
              >
                Metrics
              </button>
              <button 
                onClick={() => setActiveTab('charts')} 
                className={`px-3 py-1 rounded text-sm font-semibold transition ${activeTab === 'charts' ? 'bg-cyan-500/20 text-cyan-400' : 'text-slate-400 hover:text-slate-200'}`}
              >
                Loss Curves
              </button>
            </div>
          </div>

          {activeTab === 'metrics' ? (
            <div className="space-y-6">
              {latestStats ? (
                <>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="p-4 bg-slate-900/40 rounded-lg border border-slate-800">
                      <span className="text-slate-400 text-xs block uppercase font-medium">Current Epoch</span>
                      <span className="text-2xl font-bold font-mono text-cyan-400 mt-1 block">#{latestStats.epoch_number}</span>
                    </div>
                    <div className="p-4 bg-slate-900/40 rounded-lg border border-slate-800">
                      <span className="text-slate-400 text-xs block uppercase font-medium">MAE Loss</span>
                      <span className="text-2xl font-bold font-mono text-purple-400 mt-1 block">{latestStats.mae != null ? `${(latestStats.mae / 1000000).toFixed(6)} s` : '—'}</span>
                    </div>
                    <div className="p-4 bg-slate-900/40 rounded-lg border border-slate-800">
                      <span className="text-slate-400 text-xs block uppercase font-medium">MSE Loss</span>
                      <span className="text-2xl font-bold font-mono text-fuchsia-400 mt-1 block">{latestStats.mse != null ? `${(latestStats.mse / 1e12).toExponential(4)} s²` : '—'}</span>
                    </div>
                    <div className="p-4 bg-slate-900/40 rounded-lg border border-slate-800">
                      <span className="text-slate-400 text-xs block uppercase font-medium">R2 Score</span>
                      <span className="text-2xl font-bold font-mono text-emerald-400 mt-1 block">{latestStats.r2 != null ? `${(latestStats.r2 * 100).toFixed(2)}%` : '—'}</span>
                    </div>
                  </div>

                  <div className="overflow-x-auto max-h-80 border border-slate-800 rounded-lg">
                    <table className="w-full text-left border-collapse text-sm">
                      <thead>
                        <tr className="border-b border-slate-800 bg-slate-950/40 text-slate-400 font-semibold">
                          <th className="p-3">Epoch</th>
                          <th className="p-3">MAE (seconds)</th>
                          <th className="p-3">MSE (seconds²)</th>
                          <th className="p-3">RMSE (seconds)</th>
                          <th className="p-3">R2</th>
                        </tr>
                      </thead>
                      <tbody>
                        {[...metrics].reverse().map((m) => (
                          <tr key={m.epoch_number} className="border-b border-slate-800/40 hover:bg-slate-900/10">
                            <td className="p-3 font-mono">#{m.epoch_number}</td>
                            <td className="p-3 font-mono">{m.mae != null ? (m.mae / 1000000).toFixed(6) : '—'}</td>
                            <td className="p-3 font-mono">{m.mse != null ? (m.mse / 1e12).toExponential(4) : '—'}</td>
                            <td className="p-3 font-mono">{m.rmse != null ? (m.rmse / 1000000).toFixed(6) : '—'}</td>
                            <td className="p-3 font-mono">{m.r2 != null ? `${(m.r2 * 100).toFixed(2)}%` : '—'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </>
              ) : (
                <div className="text-center py-20 text-slate-500 font-medium">
                  Trigger a self-learning loop experiment to start compiling time-series forecast losses.
                </div>
              )}
            </div>
          ) : (
            <div className="space-y-4">
              <div className="flex justify-between items-center mb-2">
                <span className="text-xs text-slate-400 font-semibold uppercase">Forecasting Training Loss Curves</span>
                <button
                  onClick={() => setShowExplanation(!showExplanation)}
                  className="px-2 py-0.5 bg-slate-800 hover:bg-slate-700 text-xxs text-slate-300 font-semibold rounded border border-slate-700 transition"
                >
                  {showExplanation ? 'Hide Interpretation' : 'Explain Loss Graph'}
                </button>
              </div>
              <div className="h-64 w-full">
                {metrics.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart 
                      data={metrics.filter(m => m.mae != null && m.rmse != null).map(m => ({
                        ...m,
                        mae_sec: m.mae / 1000000,
                        rmse_sec: m.rmse / 1000000
                      }))} 
                      margin={{ top: 15, right: 25, left: 30, bottom: 20 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                      <XAxis 
                        dataKey="epoch_number" 
                        stroke="#94a3b8" 
                        height={45}
                      >
                        <Label value="Training Epoch Number" offset={-2} position="insideBottom" fill="#94a3b8" fontSize={11} fontWeight="bold" />
                      </XAxis>
                      <YAxis 
                        stroke="#94a3b8" 
                        width={75}
                      >
                        <Label value="Error Loss Metric (seconds)" angle={-90} position="insideLeft" offset={10} fill="#94a3b8" fontSize={11} fontWeight="bold" style={{ textAnchor: 'middle' }} />
                      </YAxis>
                      <Tooltip 
                        contentStyle={{ background: '#0f172a', borderColor: '#334155' }} 
                        formatter={(value, name) => [`${value.toFixed(6)} s`, name]}
                      />
                      <Legend />
                      <Line type="monotone" dataKey="mae_sec" stroke="#c084fc" strokeWidth={2} name="MAE Loss (seconds)" />
                      <Line type="monotone" dataKey="rmse_sec" stroke="#38bdf8" strokeWidth={2} name="RMSE Loss (seconds)" />
                    </LineChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="text-center py-20 text-slate-500 font-medium">No metrics recorded to plot yet.</div>
                )}
              </div>
              {showExplanation && (
                <div className="p-3 bg-slate-900/50 border border-slate-800 rounded-lg text-xs text-slate-400 space-y-1">
                  <p>
                    <strong>What is happening:</strong> This chart tracks the decreasing validation error loss of the estimators across training epochs. It displays Mean Absolute Error (MAE, purple) and Root Mean Squared Error (RMSE, blue).
                  </p>
                  <p>
                    <strong>Purpose:</strong> Tracing the validation loss verifies that our model optimization algorithms are converging successfully and learning the underlying quantum parameters drift patterns without overfitting.
                  </p>
                  <p>
                    <strong>Conclusion:</strong> A steadily declining error curve confirms that the Digital Twin is successfully training itself to forecast upcoming hardware degradations with high accuracy.
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Metrics Glossary and Definitions Section */}
      <div className="glass-panel p-6 space-y-4">
        <h3 className="text-xl font-extrabold text-white font-outfit">Machine Learning Loss Metrics Glossary</h3>
        <p className="text-slate-400 text-sm">Definitions and mathematical formulations of the statistics tracked during the autonomous quantum calibration forecasting loop:</p>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 pt-2">
          <div className="space-y-1">
            <h4 className="text-sm font-bold text-purple-400 font-outfit uppercase">MAE (Mean Absolute Error)</h4>
            <p className="text-slate-300 text-xs leading-relaxed">
              The average of the absolute differences between the predictions and actual calibrations. It represents the average magnitude of the forecasting error.
            </p>
          </div>
          <div className="space-y-1">
            <h4 className="text-sm font-bold text-cyan-400 font-outfit uppercase">MSE (Mean Squared Error)</h4>
            <p className="text-slate-300 text-xs leading-relaxed">
              The average of the squared differences between predicted and actual values. Since the errors are squared, it penalizes larger drift outliers more heavily.
            </p>
          </div>
          <div className="space-y-1">
            <h4 className="text-sm font-bold text-emerald-400 font-outfit uppercase">RMSE (Root Mean Squared Error)</h4>
            <p className="text-slate-300 text-xs leading-relaxed">
              The square root of the MSE, translating the squared error back into the original units of calibration measurement (microseconds or readout error rates).
            </p>
          </div>
          <div className="space-y-1">
            <h4 className="text-sm font-bold text-pink-400 font-outfit uppercase">R² (Coefficient of Determination)</h4>
            <p className="text-slate-300 text-xs leading-relaxed">
              Indicates the proportion of variance in the qubit parameters explained by the MLP and Random Forest regression models. 1.0 represents a perfect prediction.
            </p>
          </div>
          <div className="space-y-1">
            <h4 className="text-sm font-bold text-orange-400 font-outfit uppercase">MAPE (Mean Absolute Percentage Error)</h4>
            <p className="text-slate-300 text-xs leading-relaxed">
              The average of the absolute percentage errors relative to the actual ground truth parameters. Measures forecasting accuracy as a percentage.
            </p>
          </div>
          <div className="space-y-1">
            <h4 className="text-sm font-bold text-violet-400 font-outfit uppercase">Epoch / Run Loop</h4>
            <p className="text-slate-300 text-xs leading-relaxed">
              A single cycle in the training process. During each epoch, the simulator advances time, drifts qubit calibrations, updates the twin versions, and trains the machine learning estimators.
            </p>
          </div>
          <div className="space-y-1">
            <h4 className="text-sm font-bold text-yellow-500 font-outfit uppercase">Warmup / Bootstrapping</h4>
            <p className="text-slate-300 text-xs leading-relaxed">
              The initial stages of training (Epochs 1 and 2). At these steps, model evaluation calculations return null/dashes since there are not yet enough historical data points to validate fold splits.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
