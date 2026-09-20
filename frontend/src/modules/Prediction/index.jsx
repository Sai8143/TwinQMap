import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Label } from 'recharts';
import { Download } from 'lucide-react';
import api from '../../services/api';

export default function Prediction() {
  const [qubitId, setQubitId] = useState('Q0');
  const [horizon, setHorizon] = useState(24);
  const [forecast, setForecast] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modelName, setModelName] = useState('');
  const [showCoherenceExplanation, setShowCoherenceExplanation] = useState(false);
  const [showReadoutExplanation, setShowReadoutExplanation] = useState(false);
  const [qubitCount, setQubitCount] = useState(5);

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

  const fetchForecast = async () => {
    setLoading(true);
    try {
      const res = await api.get('/predictions/forecast', {
        params: { qubit_id: qubitId, horizon_hours: horizon }
      });
      setForecast(res.data.predictions);
      setModelName(res.data.model_used);
    } catch (err) {
      console.error(err);
      alert('Error fetching prediction forecast');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    async function getStatus() {
      try {
        const res = await api.get('/training/status');
        if (res.data && res.data.qubit_count) {
          setQubitCount(res.data.qubit_count);
        }
      } catch (err) {
        console.error("Error fetching status", err);
      }
    }
    getStatus();
  }, []);

  useEffect(() => {
    fetchForecast();
  }, [qubitId, horizon]);

  return (
    <div className="space-y-8 p-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-white font-outfit">Calibration Forecasting</h1>
          <p className="text-slate-400">Forecast dynamic drift parameters using the trained QubitDecayPredictor ML model</p>
        </div>
        <div className="flex gap-2 print:hidden">
          <button
            onClick={() => downloadReport('prediction', 'json')}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold rounded-lg border border-slate-700 text-sm flex items-center gap-2 transition"
          >
            <Download className="h-4 w-4" /> JSON Report
          </button>
          <button
            onClick={() => downloadReport('prediction', 'csv')}
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

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {/* Controls Column containing select and Glossary */}
        <div className="space-y-6">
          <div className="glass-panel p-6 space-y-6">
            <h3 className="text-lg font-bold text-white font-outfit">Forecast Controls</h3>
            
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Qubit Selection</label>
              <select
                value={qubitId}
                onChange={(e) => setQubitId(e.target.value)}
                className="form-input"
              >
                {Array.from({ length: qubitCount }).map((_, i) => (
                  <option key={`Q${i}`} value={`Q${i}`}>{`Q${i}`}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Horizon (Hours)</label>
              <select
                value={horizon}
                onChange={(e) => setHorizon(Number(e.target.value))}
                className="form-input"
              >
                {[12, 24, 48, 72].map((h) => (
                  <option key={h} value={h}>{h} Hours</option>
                ))}
              </select>
            </div>

            {modelName && (
              <div className="p-3 bg-slate-900/40 border border-slate-800 rounded-lg">
                <span className="text-slate-500 text-xs uppercase block font-semibold">Active Predictor</span>
                <span className="text-cyan-400 font-mono text-xs font-semibold mt-1 block">{modelName}</span>
              </div>
            )}
          </div>

          {/* Forecasting parameter glossary */}
          <div className="glass-panel p-6 space-y-4 text-xs">
            <h3 className="text-lg font-bold text-white font-outfit">Forecasting Glossary</h3>
            <div className="space-y-3 text-slate-400 text-left">
              <div>
                <strong className="text-slate-200">Horizon (Hours):</strong> The prediction timeline offset specifying how far into the future (e.g. 24 or 48 hours) the ML models will forecast.
              </div>
              <div>
                <strong className="text-slate-200">Predicted T₁ (µs):</strong> The forecasted longitudinal relaxation coherence lifetime predicted for the target horizon hours.
              </div>
              <div>
                <strong className="text-slate-200">Predicted T₂ (µs):</strong> The forecasted transverse dephasing coherence lifetime predicted for the target horizon hours.
              </div>
              <div>
                <strong className="text-slate-200">Predicted Readout:</strong> The forecasted readout measurement error rate compiled by the Random Forest regressor.
              </div>
              <div>
                <strong className="text-slate-200">Active Predictor:</strong> The machine learning model type (e.g. Random Forest) currently loaded to compile forecasts.
              </div>
            </div>
          </div>
        </div>

        <div className="glass-panel p-6 md:col-span-3 space-y-6">
          <h3 className="text-lg font-bold text-white font-outfit">Predictive Forecast Trends: {qubitId}</h3>
          
          {loading ? (
            <div className="text-center py-20 text-slate-400">Evaluating multi-target regressions...</div>
          ) : (
            <div className="space-y-8">
              {/* Coherence predictions */}
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <h4 className="text-sm font-semibold text-slate-400">Coherence Lifetimes (T1 & T2 Predictions)</h4>
                  <button
                    onClick={() => setShowCoherenceExplanation(!showCoherenceExplanation)}
                    className="px-2 py-0.5 bg-slate-800 hover:bg-slate-700 text-xxs text-slate-300 font-semibold rounded border border-slate-700 transition"
                  >
                    {showCoherenceExplanation ? 'Hide Interpretation' : 'Explain Coherence Graph'}
                  </button>
                </div>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart 
                      data={forecast.map(f => ({
                        ...f,
                        predicted_t1_sec: f.predicted_t1 / 1000000,
                        predicted_t2_sec: f.predicted_t2 / 1000000
                      }))} 
                      margin={{ top: 15, right: 25, left: 30, bottom: 20 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                      <XAxis 
                        dataKey="timestamp_forecast" 
                        stroke="#94a3b8" 
                        height={45}
                      >
                        <Label value="Future Timeline (Hours Ahead)" offset={-2} position="insideBottom" fill="#94a3b8" fontSize={11} fontWeight="bold" />
                      </XAxis>
                      <YAxis 
                        stroke="#94a3b8" 
                        width={75}
                      >
                        <Label value="Coherence Time (seconds)" angle={-90} position="insideLeft" offset={10} fill="#94a3b8" fontSize={11} fontWeight="bold" style={{ textAnchor: 'middle' }} />
                      </YAxis>
                      <Tooltip 
                        contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#fff' }} 
                        formatter={(value, name) => [`${value.toFixed(6)} s`, name]}
                      />
                      <Legend />
                      <Line type="monotone" dataKey="predicted_t1_sec" stroke="#a78bfa" activeDot={{ r: 8 }} name="Predicted T1 (seconds)" />
                      <Line type="monotone" dataKey="predicted_t2_sec" stroke="#22d3ee" name="Predicted T2 (seconds)" />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
                {showCoherenceExplanation && (
                  <div className="p-3 bg-slate-900/50 border border-slate-800 rounded-lg text-xs text-slate-400 space-y-1">
                    <p>
                      <strong>What is happening:</strong> This chart plots the recursive multi-step forecasts for dephasing ($T_2$, blue) and thermal relaxation ($T_1$, violet) over the forecast horizon.
                    </p>
                    <p>
                      <strong>Purpose:</strong> By projecting the decay rate of coherence lifetimes, the scheduler identifies when a qubit node is transitioning from a "healthy superposition" state to a "highly dephased" state.
                    </p>
                    <p>
                      <strong>Conclusion:</strong> The downward curves illustrate progressive quantum decoherence. The scheduler relies on this trend to prevent allocating gate sequences to physical channels that will experience phase errors.
                    </p>
                  </div>
                )}
              </div>

              {/* Readout error predictions */}
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <h4 className="text-sm font-semibold text-slate-400">Readout Error Evolution Prediction</h4>
                  <button
                    onClick={() => setShowReadoutExplanation(!showReadoutExplanation)}
                    className="px-2 py-0.5 bg-slate-800 hover:bg-slate-700 text-xxs text-slate-300 font-semibold rounded border border-slate-700 transition"
                  >
                    {showReadoutExplanation ? 'Hide Interpretation' : 'Explain Readout Graph'}
                  </button>
                </div>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={forecast} margin={{ top: 15, right: 25, left: 30, bottom: 20 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                      <XAxis 
                        dataKey="timestamp_forecast" 
                        stroke="#94a3b8" 
                        height={45}
                      >
                        <Label value="Future Timeline (Hours Ahead)" offset={-2} position="insideBottom" fill="#94a3b8" fontSize={11} fontWeight="bold" />
                      </XAxis>
                      <YAxis 
                        stroke="#94a3b8" 
                        width={75}
                      >
                        <Label value="Readout Error Rate" angle={-90} position="insideLeft" offset={10} fill="#94a3b8" fontSize={11} fontWeight="bold" style={{ textAnchor: 'middle' }} />
                      </YAxis>
                      <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#fff' }} />
                      <Legend />
                      <Line type="monotone" dataKey="predicted_readout_error" stroke="#f43f5e" name="Predicted Readout Error" />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
                {showReadoutExplanation && (
                  <div className="p-3 bg-slate-900/50 border border-slate-800 rounded-lg text-xs text-slate-400 space-y-1">
                    <p>
                      <strong>What is happening:</strong> This chart forecasts the measurement readout error rate of the target qubit, showing how readout errors drift upward over the selected timeline.
                    </p>
                    <p>
                      <strong>Purpose:</strong> Readout errors directly compromise quantum circuit measurement outcomes. Projecting these rates allows the compiler to evaluate circuit measurement fidelity.
                    </p>
                    <p>
                      <strong>Conclusion:</strong> If readout errors are predicted to exceed the noise threshold, the system triggers calibration updates to stabilize measurement gates.
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
