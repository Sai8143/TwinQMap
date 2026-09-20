import React, { useState, useEffect } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Label } from 'recharts';
import { Activity, ShieldAlert, Cpu, Database, Download, Clock, Brain, Layers, Server } from 'lucide-react';
import { motion } from 'framer-motion';
import api from '../../services/api';

export default function Dashboard() {
  const [qhiList, setQhiList] = useState([]);
  const [forecast, setForecast] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showExplanation, setShowExplanation] = useState(false);

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

  const [systemInfo, setSystemInfo] = useState(null);
  const [lastCalibSeconds, setLastCalibSeconds] = useState(115);
  const [currentEpoch, setCurrentEpoch] = useState(95);

  useEffect(() => {
    async function fetchData() {
      try {
        const qhiRes = await api.get('/scheduler/health-indices');
        setQhiList(qhiRes.data);

        // Fetch forecast for Q0
        const forecastRes = await api.get('/predictions/forecast', {
          params: { qubit_id: 'Q0', horizon_hours: 24 }
        });
        setForecast(forecastRes.data.predictions);

        const healthRes = await api.get('/health');
        setSystemInfo(healthRes.data);
      } catch (err) {
        console.error("Dashboard error loading data", err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  // Real-time ticking simulation effect
  useEffect(() => {
    if (loading) return;
    const interval = setInterval(() => {
      // 1. Tick last calibration counter
      setLastCalibSeconds((prev) => {
        if (prev >= 120) {
          return 0; // reset calibration timer
        }
        return prev + 1;
      });

      // 2. Cycle simulation epochs
      setCurrentEpoch((prev) => {
        if (prev < 100) {
          return prev + 1;
        } else {
          // Once 100 is reached, hold for 10 ticks, then restart calibration loop
          if (Math.random() < 0.08) {
            return 1;
          }
          return 100;
        }
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [loading]);

  if (loading) {
    return <div className="p-8 text-center text-slate-400">Loading Dashboard Metrics...</div>;
  }

  const averageQhi = qhiList.reduce((acc, q) => acc + q.health_index, 0) / (qhiList.length || 1);

  // Derive dynamic statuses
  const isCalibrating = lastCalibSeconds < 5;
  const isTraining = currentEpoch < 100;

  const systemStatusText = isCalibrating ? 'CALIBRATING' : isTraining ? 'EVOLVING' : 'HEALTHY';
  const systemStatusColor = isCalibrating ? 'text-amber-400' : isTraining ? 'text-violet-400' : 'text-emerald-400';

  const mlEngineText = isTraining ? 'RETRAINING' : 'AUTO-RETRAINED';
  const mlEngineColor = isTraining ? 'text-amber-400' : 'text-emerald-400';

  const calibText = isCalibrating 
    ? 'JUST NOW' 
    : lastCalibSeconds < 60 
      ? `${lastCalibSeconds}s AGO` 
      : `${Math.floor(lastCalibSeconds / 60)}m ${lastCalibSeconds % 60}s AGO`;

  return (
    <motion.div 
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: 'easeOut' }}
      className="space-y-8 p-6"
    >
      {/* Hero Dashboard Section */}
      <div className="glass-panel p-6 bg-slate-900/40 relative overflow-hidden">
        {/* Glowing abstract circles in background */}
        <div className="absolute right-0 top-0 w-80 h-80 bg-cyan-500/5 rounded-full filter blur-3xl pointer-events-none"></div>
        <div className="absolute left-1/3 bottom-0 w-64 h-64 bg-violet-500/5 rounded-full filter blur-3xl pointer-events-none"></div>

        <div className="flex flex-col lg:flex-row justify-between lg:items-center gap-6 pb-6 border-b border-slate-800/60">
          <div>
            <h1 className="text-4xl font-extrabold tracking-tight text-white font-outfit bg-clip-text bg-gradient-to-r from-white via-slate-100 to-slate-400">
              TwinQ-Map
            </h1>
            <p className="text-slate-400 text-xs sm:text-sm mt-2 max-w-3xl leading-relaxed">
              Closed-Loop Digital Twin Ecosystem for Dynamic Qubit Mapping and Parameter Drift Forecasting on NISQ Processors
            </p>
          </div>
          <div className="flex flex-wrap gap-2 print:hidden">
            <button
              onClick={() => downloadReport('digital_twin', 'json')}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold rounded-lg border border-slate-700 text-xs flex items-center gap-2 transition"
            >
              <Download className="h-3.5 w-3.5" /> JSON Report
            </button>
            <button
              onClick={() => downloadReport('digital_twin', 'csv')}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold rounded-lg border border-slate-700 text-xs flex items-center gap-2 transition"
            >
              <Download className="h-3.5 w-3.5" /> CSV Report
            </button>
            <button
              onClick={() => window.print()}
              className="px-4 py-2 bg-violet-600 hover:bg-violet-500 text-white font-semibold rounded-lg text-xs flex items-center gap-2 transition shadow-lg shadow-violet-500/20"
            >
              <Download className="h-3.5 w-3.5" /> Print PDF
            </button>
          </div>
        </div>

        {/* 7 Live Status Cards Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4 pt-6">
          <div className="glass-panel p-3 text-center space-y-1.5 flex flex-col justify-between hover:scale-102 transition duration-200">
            <span className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider block">System Status</span>
            <div className={`flex justify-center ${systemStatusColor}`}><Activity className="h-5 w-5 animate-pulse" /></div>
            <span className={`text-xs font-bold ${systemStatusColor} uppercase tracking-wide`}>{systemStatusText}</span>
          </div>

          <div className="glass-panel p-3 text-center space-y-1.5 flex flex-col justify-between hover:scale-102 transition duration-200">
            <span className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider block">Digital Twin</span>
            <div className="flex justify-center text-violet-400"><Layers className="h-5 w-5" /></div>
            <span className="text-xs font-bold text-violet-400 uppercase tracking-wide">V101 Active</span>
          </div>

          <div className="glass-panel p-3 text-center space-y-1.5 flex flex-col justify-between hover:scale-102 transition duration-200">
            <span className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider block">Active Provider</span>
            <div className="flex justify-center text-cyan-400"><Cpu className="h-5 w-5" /></div>
            <span className="text-xs font-bold text-cyan-400 uppercase tracking-wide">IBM Inspired</span>
          </div>

          <div className="glass-panel p-3 text-center space-y-1.5 flex flex-col justify-between hover:scale-102 transition duration-200">
            <span className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider block">ML Engine</span>
            <div className={`flex justify-center ${mlEngineColor}`}><Brain className="h-5 w-5" /></div>
            <span className={`text-xs font-bold ${mlEngineColor} uppercase tracking-wide`}>{mlEngineText}</span>
          </div>

          <div className="glass-panel p-3 text-center space-y-1.5 flex flex-col justify-between hover:scale-102 transition duration-200">
            <span className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider block">Forecast Engine</span>
            <div className="flex justify-center text-cyan-400"><Server className="h-5 w-5" /></div>
            <span className="text-xs font-bold text-cyan-400 uppercase tracking-wide">24h Horizon</span>
          </div>

          <div className="glass-panel p-3 text-center space-y-1.5 flex flex-col justify-between hover:scale-102 transition duration-200">
            <span className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider block">Last Calib</span>
            <div className="flex justify-center text-amber-400"><Clock className="h-5 w-5" /></div>
            <span className="text-xs font-bold text-amber-400 uppercase tracking-wide">{calibText}</span>
          </div>

          <div className="glass-panel p-3 text-center space-y-1.5 flex flex-col justify-between hover:scale-102 transition duration-200">
            <span className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider block">Simulation Epoch</span>
            <div className="flex justify-center text-indigo-400"><Layers className="h-5 w-5" /></div>
            <span className="text-xs font-bold text-indigo-400 uppercase tracking-wide">{currentEpoch} / 100</span>
          </div>
        </div>
      </div>

      {/* Grid of KPI cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="glass-panel p-6 flex items-center justify-between">
          <div>
            <p className="text-slate-400 text-sm">System Health Index (QHI)</p>
            <h2 className="text-3xl font-bold mt-1 text-emerald-400">{(averageQhi * 100).toFixed(1)}%</h2>
          </div>
          <div className="p-3 bg-emerald-500/10 text-emerald-400 rounded-lg">
            <Activity className="h-6 w-6" />
          </div>
        </div>

        <div className="glass-panel p-6 flex items-center justify-between">
          <div>
            <p className="text-slate-400 text-sm">Active Qubits</p>
            <h2 className="text-3xl font-bold mt-1 text-cyan-400">
              {qhiList.length} / {qhiList.length}
            </h2>
          </div>
          <div className="p-3 bg-cyan-500/10 text-cyan-400 rounded-lg">
            <Cpu className="h-6 w-6" />
          </div>
        </div>

        <div className="glass-panel p-6 flex items-center justify-between">
          <div>
            <p className="text-slate-400 text-sm">Operations Mode</p>
            <h2 className="text-3xl font-bold mt-1 text-emerald-400">
              {qhiList.length === 133 ? 'IBM Quantum' : (qhiList.length === 11 || qhiList.length === 25) ? 'IonQ Cloud' : 'Simulated'}
            </h2>
          </div>
          <div className="p-3 bg-violet-500/10 text-violet-400 rounded-lg">
            <Database className="h-6 w-6" />
          </div>
        </div>

        <div className="glass-panel p-6 flex items-center justify-between">
          <div>
            <p className="text-slate-400 text-sm">Alerts</p>
            <h2 className="text-3xl font-bold mt-1 text-rose-500">0</h2>
          </div>
          <div className="p-3 bg-rose-500/10 text-rose-500 rounded-lg">
            <ShieldAlert className="h-6 w-6" />
          </div>
        </div>
      </div>

      {/* Coherence predictions curve */}
      <div className="glass-panel p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-xl font-bold text-white font-outfit">Forecasting Coherence Trend: Q0</h3>
          <button
            onClick={() => setShowExplanation(!showExplanation)}
            className="px-3 py-1 bg-slate-800 hover:bg-slate-700 text-xs text-slate-300 font-semibold rounded border border-slate-700 transition"
          >
            {showExplanation ? 'Hide Interpretation' : 'Explain Graph Dynamics'}
          </button>
        </div>
        <div className="h-80 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart 
              data={forecast.map(f => ({ ...f, predicted_t1_sec: f.predicted_t1 / 1000000 }))} 
              margin={{ top: 20, right: 30, left: 55, bottom: 40 }}
            >
              <defs>
                <linearGradient id="colorT1" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#8884d8" stopOpacity={0.4}/>
                  <stop offset="95%" stopColor="#8884d8" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis 
                dataKey="timestamp_forecast" 
                stroke="#94a3b8" 
                height={55} 
              >
                <Label value="Forecast Timeline (Hours Ahead)" offset={-20} position="insideBottom" fill="#94a3b8" fontSize={12} fontWeight="bold" />
              </XAxis>
              <YAxis 
                stroke="#94a3b8" 
                width={80} 
              >
                <Label value="Coherence Time T1 (seconds)" angle={-90} position="insideLeft" offset={-35} fill="#94a3b8" fontSize={12} fontWeight="bold" style={{ textAnchor: 'middle' }} />
              </YAxis>
              <Tooltip 
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#fff' }} 
                formatter={(value) => [`${value.toFixed(6)} s`, "Predicted T1"]}
              />
              <Area type="monotone" dataKey="predicted_t1_sec" stroke="#8884d8" fillOpacity={1} fill="url(#colorT1)" name="Predicted T1" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
        {showExplanation && (
          <div className="mt-4 p-4 bg-slate-900/50 border border-slate-800 rounded-lg text-xs text-slate-400 space-y-2">
            <p>
              <strong>What is happening:</strong> This chart illustrates the predicted longitudinal relaxation lifetime (\(T_1\)) of qubit Q0 over the next 24 hours. The line represents the multi-target regression forecast, showing a declining trajectory as relaxation coherence degrades over time.
            </p>
            <p>
              <strong>Purpose:</strong> By projecting the decay rate of the coherence time constant, the framework alerts the system compiler to preemptively bypass this qubit node before it crosses the decoherence threshold.
            </p>
            <p>
              <strong>Conclusion:</strong> Proactive forecasting of the \(T_1\) decay prevents gate operation failures, ensuring layout mappings maintain a high coherence lifetime ceiling throughout scheduling cycles.
            </p>
          </div>
        )}
      </div>

      {/* Health status lineup and Glossary grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 glass-panel p-6">
          <h3 className="text-xl font-bold text-white mb-4">Qubit Status Lineup</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 text-sm">
                  <th className="py-3 px-4">Qubit ID</th>
                  <th className="py-3 px-4">Health Score (QHI)</th>
                  <th className="py-3 px-4">Readout Weight</th>
                  <th className="py-3 px-4">Gate Weight</th>
                  <th className="py-3 px-4 text-right">Status</th>
                </tr>
              </thead>
              <tbody>
                {qhiList.map((q) => (
                  <tr key={q.qubit_id} className="border-b border-slate-800/50 hover:bg-slate-900/30">
                    <td className="py-4 px-4 font-mono text-cyan-400">{q.qubit_id}</td>
                    <td className="py-4 px-4 font-semibold">{(q.health_index * 100).toFixed(1)}%</td>
                    <td className="py-4 px-4 font-mono text-slate-400">{q.weights.readout}</td>
                    <td className="py-4 px-4 font-mono text-slate-400">{q.weights.gate}</td>
                    <td className="py-4 px-4 text-right">
                      <span className={`status-badge ${q.status}`}>{q.status}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* System & QHI Glossary */}
        <div className="glass-panel p-6 space-y-4 h-fit">
          <h3 className="text-xl font-bold text-white font-outfit">QHI & Metric Glossary</h3>
          <div className="space-y-3 text-xs text-slate-400">
            <div>
              <strong className="text-slate-200">QHI (Quantum Health Index):</strong> An aggregate reliability indicator (0% to 100%) indicating physical state quality. Calculated by evaluating deviations in qubit relaxation time (T1), dephasing time (T2), single/two-qubit gate error rates, and readout errors.
            </div>
            <div>
              <strong className="text-slate-200">Readout Weight:</strong> The coefficient weight (usually 0.3 or 30%) applied to measurement readout error rates when calculating the overall QHI.
            </div>
            <div>
              <strong className="text-slate-200">Gate Weight:</strong> The coefficient weight (usually 0.3 or 30%) applied to physical gate error rates when calculating the overall QHI.
            </div>
            <div>
              <strong className="text-slate-200">Operations Mode:</strong> Indicates whether the metrics represent mathematical quantum evolution simulator drift datasets or live hardware token tracking feeds.
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
