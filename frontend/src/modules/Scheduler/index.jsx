import React, { useState } from 'react';
import api from '../../services/api';
import { Download } from 'lucide-react';

export default function Scheduler() {
  const [logicalSize, setLogicalSize] = useState(3);
  const [edgesInput, setEdgesInput] = useState('0-1, 1-2');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

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

  const handleSchedule = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);

    // Parse edges input: "0-1, 1-2" -> [[0, 1], [1, 2]]
    const parsedEdges = [];
    if (edgesInput.trim()) {
      const pairs = edgesInput.split(',');
      for (let p of pairs) {
        const parts = p.trim().split('-');
        if (parts.length === 2) {
          const u = parseInt(parts[0], 10);
          const v = parseInt(parts[1], 10);
          if (!isNaN(u) && !isNaN(v)) {
            parsedEdges.push([u, v]);
          }
        }
      }
    }

    try {
      const response = await api.post('/scheduler/schedule', parsedEdges, {
        params: {
          logical_circuit_size: logicalSize,
          algorithm: 'QHI_Greedy'
        },
        headers: { 'Content-Type': 'application/json' }
      });
      setResult(response.data);
    } catch (err) {
      console.error(err);
      alert('Error scheduling layout mapping: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8 p-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-white font-outfit">Adaptive Qubit Scheduler</h1>
          <p className="text-slate-400">Compile logical quantum circuits onto time-varying physical layouts using QHI (Qubit Health Index) Greedy algorithm</p>
        </div>
        <div className="flex gap-2 print:hidden">
          <button
            onClick={() => downloadReport('scheduler', 'json')}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold rounded-lg border border-slate-700 text-sm flex items-center gap-2 transition"
          >
            <Download className="h-4 w-4" /> JSON Report
          </button>
          <button
            onClick={() => downloadReport('scheduler', 'csv')}
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

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Input Column containing form and Glossary */}
        <div className="space-y-6">
          <div className="glass-panel p-6">
            <h3 className="text-lg font-bold text-white mb-4 font-outfit">Circuit Parameters</h3>
            <form onSubmit={handleSchedule} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Logical Qubits (Width)</label>
                <input
                  type="number"
                  min="1"
                  max="5"
                  value={logicalSize}
                  onChange={(e) => setLogicalSize(Number(e.target.value))}
                  className="form-input"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Logical Gate Links (Interactions)
                </label>
                <input
                  type="text"
                  placeholder="e.g. 0-1, 1-2"
                  value={edgesInput}
                  onChange={(e) => setEdgesInput(e.target.value)}
                  className="form-input"
                  required
                />
                <span className="text-xs text-slate-500 mt-1 block">Format: source-target separated by commas.</span>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="glow-btn w-full"
              >
                {loading ? 'Compiling Layout...' : 'Compile Qubit Layout'}
              </button>
            </form>
          </div>

          {/* Adaptive Scheduler Glossary */}
          <div className="glass-panel p-6 space-y-4 text-xs">
            <h3 className="text-lg font-bold text-white font-outfit">Scheduler Glossary</h3>
            <div className="space-y-3 text-slate-400 text-left">
              <div>
                <strong className="text-slate-200">Logical Qubits (Width):</strong> The number of virtual qubits required by the user's quantum algorithm.
              </div>
              <div>
                <strong className="text-slate-200">Logical Gate Links:</strong> The entanglement interactions (e.g. CNOT links) between logical qubits that need to execute.
              </div>
              <div>
                <strong className="text-slate-200">Estimated Fidelity:</strong> The predicted probability of error-free execution of the circuit, computed by combining gate errors of selected physical qubits.
              </div>
              <div>
                <strong className="text-slate-200">SWAP Gates:</strong> Overhead routing gates inserted to physically entangle qubits that are not directly adjacent on the coupling map.
              </div>
              <div>
                <strong className="text-slate-200">Logical-to-Physical Mapping:</strong> The compiler allocation matching each logical circuit qubit to the most reliable physical qubit hardware node.
              </div>
            </div>
          </div>
        </div>

        {/* Results view */}
        <div className="glass-panel p-6 md:col-span-2 space-y-6">
          <h3 className="text-lg font-bold text-white font-outfit">Compiler Output Mapping</h3>
          {result ? (
            <div className="space-y-6">
              {/* Mapping Details */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="p-4 bg-slate-900/40 border border-slate-800 rounded-lg">
                  <span className="text-slate-400 text-xs uppercase font-semibold">Estimated Fidelity</span>
                  <p className="text-2xl font-bold mt-1 text-emerald-400">{(result.estimated_mapping_fidelity * 100).toFixed(2)}%</p>
                </div>
                <div className="p-4 bg-slate-900/40 border border-slate-800 rounded-lg">
                  <span className="text-slate-400 text-xs uppercase font-semibold">Routing SWAP Cost</span>
                  <p className="text-2xl font-bold mt-1 text-cyan-400">{result.estimated_coupling_cost} SWAPs</p>
                </div>
                <div className="p-4 bg-slate-900/40 border border-slate-800 rounded-lg">
                  <span className="text-slate-400 text-xs uppercase font-semibold">Compilation Status</span>
                  <p className="text-2xl font-bold mt-1 text-purple-400">{result.execution_status}</p>
                </div>
              </div>

              <div>
                <h4 className="text-sm font-semibold text-slate-300 mb-2">Logical-to-Physical Mapping Allocation</h4>
                <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
                  {Object.entries(result.mapping_selected).map(([logical, physical]) => (
                    <div key={logical} className="p-3 bg-slate-800 border border-slate-700 rounded-lg text-center">
                      <span className="text-xs text-slate-400 block">Logical Q{logical}</span>
                      <span className="text-lg font-mono font-bold text-cyan-400 mt-1 block">&rarr; Physical Q{physical}</span>
                    </div>
                  ))}
                </div>
              </div>

              {result.swaps_required.length > 0 && (
                <div>
                  <h4 className="text-sm font-semibold text-slate-300 mb-2">Inserted Routing SWAP Gates</h4>
                  <div className="flex flex-wrap gap-2">
                    {result.swaps_required.map(([u, v], idx) => (
                      <span key={idx} className="px-3 py-1 bg-red-950/20 border border-red-500/30 font-mono text-rose-400 rounded text-sm">
                        SWAP(Q{u}, Q{v})
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-16 text-slate-500">Submit logical circuit details on the left panel to schedule physical mappings.</div>
          )}
        </div>
      </div>
    </div>
  );
}
