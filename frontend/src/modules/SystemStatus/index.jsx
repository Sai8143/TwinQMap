import React, { useState, useEffect } from 'react';
import api from '../../services/api';

export default function SystemStatus() {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function getStatus() {
      try {
        const res = await api.get('/health');
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
        <h1 className="text-3xl font-extrabold tracking-tight text-white font-outfit">System Status</h1>
        <p className="text-slate-400">Monitoring logs, backend readiness probes, and database connections</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="glass-panel p-6 space-y-4">
          <h3 className="text-lg font-bold text-white font-outfit">System Verification Probes</h3>
          {loading ? (
            <p className="text-slate-500">Querying probes...</p>
          ) : status ? (
            <div className="space-y-4">
              <div className="flex justify-between items-center text-sm">
                <span className="text-slate-400">Liveness State</span>
                <span className="px-2 py-0.5 bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 rounded-full font-semibold uppercase text-xs">
                  {status.status}
                </span>
              </div>
              <div className="flex justify-between items-center text-sm">
                <span className="text-slate-400">MongoDB Readiness</span>
                <span className="px-2 py-0.5 bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 rounded-full font-semibold uppercase text-xs">
                  {status.database}
                </span>
              </div>
              <div className="flex justify-between items-center text-sm">
                <span className="text-slate-400">Deploy Environment</span>
                <span className="font-mono text-slate-300">{status.environment}</span>
              </div>
              <div className="flex justify-between items-center text-sm">
                <span className="text-slate-400">Operation Mode</span>
                <span className="font-mono text-slate-300">{status.mode}</span>
              </div>
            </div>
          ) : (
            <p className="text-rose-500 text-sm">Backend connection offline.</p>
          )}
        </div>
      </div>
    </div>
  );
}
