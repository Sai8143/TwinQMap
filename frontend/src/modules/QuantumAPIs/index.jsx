import React, { useState, useEffect } from 'react';
import api from '../../services/api';

export default function QuantumAPIs() {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function getStatus() {
      try {
        const res = await api.get('/quantum/status');
        setStatus(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    getStatus();
  }, []);

  return (
    <div className="space-y-8 p-6">
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight text-white font-outfit">Quantum Provider Status</h1>
        <p className="text-slate-400">View active backend provider integrations and cloud API online status</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass-panel p-6 space-y-4">
          <h3 className="text-lg font-bold text-white font-outfit">Mathematical Quantum Simulator</h3>
          
          {loading ? (
            <p className="text-slate-500">Querying status...</p>
          ) : status && status.simulator ? (
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-slate-400 text-sm">Status Indicator</span>
                <span className="px-3 py-1 bg-emerald-500/15 text-emerald-400 font-semibold rounded-full text-xs uppercase border border-emerald-500/20">
                  {status.simulator.status}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-slate-400 text-sm">Active Provider Name</span>
                <span className="font-mono text-cyan-400 text-sm">{status.simulator.backend_name}</span>
              </div>
            </div>
          ) : (
            <p className="text-rose-500 text-sm">Provider Offline or Connectivity Lost.</p>
          )}
        </div>

        <div className={`glass-panel p-6 space-y-4 transition ${(!status || (status.ibm && !status.ibm.configured)) ? 'opacity-50' : ''}`}>
          <h3 className="text-lg font-bold text-white font-outfit">IBM Quantum Runtime (Cloud API)</h3>
          
          {loading ? (
            <p className="text-slate-500">Querying status...</p>
          ) : status && status.ibm ? (
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-slate-400 text-sm">Status Indicator</span>
                <span className={`px-3 py-1 font-semibold rounded-full text-xs uppercase border ${status.ibm.configured ? 'bg-emerald-500/15 text-emerald-400 border-emerald-500/20' : 'bg-slate-800 text-slate-400 border-slate-700'}`}>
                  {status.ibm.status}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-slate-400 text-sm">Active Provider Name</span>
                <span className="font-mono text-cyan-400 text-sm">{status.ibm.backend_name}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-slate-400 text-sm">Active Token</span>
                <span className="font-mono text-slate-300 text-sm">{status.ibm.token_masked}</span>
              </div>
              {status.ibm.configured && (
                <div className="flex justify-between items-center text-xs text-slate-500">
                  <span>Queued Jobs</span>
                  <span className="font-mono font-bold text-slate-300">{status.ibm.pending_jobs}</span>
                </div>
              )}
            </div>
          ) : (
            <p className="text-rose-500 text-sm">Provider Offline or Connectivity Lost.</p>
          )}
        </div>

        <div className={`glass-panel p-6 space-y-4 transition ${(!status || (status.ionq && !status.ionq.configured)) ? 'opacity-50' : ''}`}>
          <h3 className="text-lg font-bold text-white font-outfit">IonQ Trapped-Ion (Cloud API)</h3>
          
          {loading ? (
            <p className="text-slate-500">Querying status...</p>
          ) : status && status.ionq ? (
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-slate-400 text-sm">Status Indicator</span>
                <span className={`px-3 py-1 font-semibold rounded-full text-xs uppercase border ${status.ionq.configured ? 'bg-emerald-500/15 text-emerald-400 border-emerald-500/20' : 'bg-slate-800 text-slate-400 border-slate-700'}`}>
                  {status.ionq.status}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-slate-400 text-sm">Active Provider Name</span>
                <span className="font-mono text-cyan-400 text-sm">{status.ionq.backend_name}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-slate-400 text-sm">Active Token</span>
                <span className="font-mono text-slate-300 text-sm">{status.ionq.token_masked}</span>
              </div>
              {status.ionq.configured && (
                <div className="flex justify-between items-center text-xs text-slate-500">
                  <span>Queued Jobs</span>
                  <span className="font-mono font-bold text-slate-300">{status.ionq.pending_jobs}</span>
                </div>
              )}
            </div>
          ) : (
            <p className="text-rose-500 text-sm">Provider Offline or Connectivity Lost.</p>
          )}
        </div>
      </div>
    </div>
  );
}
