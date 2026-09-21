import React, { useState, useEffect } from 'react';
import api from '../../services/api';

export default function QuantumAPIs() {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [ibmToken, setIbmToken] = useState('');
  const [ionqKey, setIonqKey] = useState('');
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState(null);

  const fetchStatus = async () => {
    try {
      const res = await api.get('/quantum/status');
      setStatus(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  const handleSaveKeys = async (e) => {
    e.preventDefault();
    setSaving(true);
    setMsg(null);
    try {
      const res = await api.post('/quantum/config', {
        ibm_quantum_token: ibmToken,
        ionq_api_key: ionqKey
      });
      setMsg({ type: 'success', text: res.data.message || 'API Keys updated and verified successfully!' });
      setIbmToken('');
      setIonqKey('');
      await fetchStatus();
    } catch (err) {
      setMsg({ type: 'error', text: 'Failed to update API keys. Please check endpoint status.' });
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-8 p-6">
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight text-white font-outfit">Quantum Provider Status</h1>
        <p className="text-slate-400">View active backend provider integrations and configure live cloud API credentials</p>
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

        <div className={`glass-panel p-6 space-y-4 transition ${(!status || (status.ibm && !status.ibm.configured)) ? 'border-amber-500/30' : 'border-emerald-500/30'}`}>
          <h3 className="text-lg font-bold text-white font-outfit">IBM Quantum Runtime (Cloud API)</h3>
          
          {loading ? (
            <p className="text-slate-500">Querying status...</p>
          ) : status && status.ibm ? (
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-slate-400 text-sm">Status Indicator</span>
                <span className={`px-3 py-1 font-semibold rounded-full text-xs uppercase border ${status.ibm.configured ? 'bg-emerald-500/15 text-emerald-400 border-emerald-500/20' : 'bg-amber-500/15 text-amber-400 border-amber-500/20'}`}>
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

        <div className={`glass-panel p-6 space-y-4 transition ${(!status || (status.ionq && !status.ionq.configured)) ? 'border-amber-500/30' : 'border-emerald-500/30'}`}>
          <h3 className="text-lg font-bold text-white font-outfit">IonQ Trapped-Ion (Cloud API)</h3>
          
          {loading ? (
            <p className="text-slate-500">Querying status...</p>
          ) : status && status.ionq ? (
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-slate-400 text-sm">Status Indicator</span>
                <span className={`px-3 py-1 font-semibold rounded-full text-xs uppercase border ${status.ionq.configured ? 'bg-emerald-500/15 text-emerald-400 border-emerald-500/20' : 'bg-amber-500/15 text-amber-400 border-amber-500/20'}`}>
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

      {/* Interactive API Key Manager Panel */}
      <div className="glass-panel p-8 max-w-3xl space-y-6 border border-violet-500/20">
        <div>
          <h2 className="text-xl font-bold text-white font-outfit">Configure Cloud API Tokens</h2>
          <p className="text-slate-400 text-sm mt-1">
            Enter your active IBM Quantum API Token and IonQ API Key to activate live hardware status.
          </p>
        </div>

        {msg && (
          <div className={`p-4 rounded-lg text-sm font-medium ${msg.type === 'success' ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30' : 'bg-rose-500/15 text-rose-400 border border-rose-500/30'}`}>
            {msg.text}
          </div>
        )}

        <form onSubmit={handleSaveKeys} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              IBM Quantum API Token
            </label>
            <input
              type="password"
              placeholder="Paste 44-character IBM Quantum Token (e.g. e4UV8XMFASmSG...)"
              value={ibmToken}
              onChange={(e) => setIbmToken(e.target.value)}
              className="form-input font-mono text-sm w-full"
            />
            <p className="text-xs text-slate-500 mt-1">Get your free token from quantum.ibm.com -&gt; Account Settings</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              IonQ API Key
            </label>
            <input
              type="password"
              placeholder="Paste IonQ API Key (e.g. boaQ5UxRaS0g...)"
              value={ionqKey}
              onChange={(e) => setIonqKey(e.target.value)}
              className="form-input font-mono text-sm w-full"
            />
            <p className="text-xs text-slate-500 mt-1">Get your API key from console.ionq.com</p>
          </div>

          <button
            type="submit"
            disabled={saving}
            className="glow-btn px-6 py-3 text-sm font-bold"
          >
            {saving ? 'Updating API Keys...' : 'Save & Activate Cloud API Keys'}
          </button>
        </form>
      </div>
    </div>
  );
}
