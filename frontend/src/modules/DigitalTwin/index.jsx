import React, { useState, useEffect } from 'react';
import api from '../../services/api';

import { Download } from 'lucide-react';

export default function DigitalTwin() {
  const [twinInfo, setTwinInfo] = useState(null);
  const [qubitId, setQubitId] = useState('Q0');
  const [calibrations, setCalibrations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [syncStatus, setSyncStatus] = useState('');
  const [rollbackVersion, setRollbackVersion] = useState(1);

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

  async function fetchTwinDetails() {
    try {
      // Fetch digital twin status for selected qubit
      const res = await api.get(`/digital-twin/${qubitId}`);
      setTwinInfo(res.data);
    } catch (err) {
      console.error(err);
      setTwinInfo(null);
    }
  }

  async function fetchCalibrations() {
    try {
      const res = await api.get('/calibrations/history', {
        params: { qubit_id: qubitId, limit: 150 }
      });
      setCalibrations(res.data);
    } catch (err) {
      console.error(err);
    }
  }

  useEffect(() => {
    fetchTwinDetails();
    fetchCalibrations();
  }, [qubitId]);

  const handleSync = async () => {
    setLoading(true);
    setSyncStatus('');
    try {
      const res = await api.post(`/digital-twin/${qubitId}/sync?is_full_sync=false`);
      setSyncStatus(`Successfully synchronized qubit to version ${res.data.current_version}`);
      fetchTwinDetails();
      fetchCalibrations();
    } catch (err) {
      console.error(err);
      setSyncStatus('Synchronization failed: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleRollback = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await api.post(`/digital-twin/${qubitId}/rollback?target_version=${rollbackVersion}`);
      setSyncStatus(`Rollback successful. Restored version ${rollbackVersion}`);
      fetchTwinDetails();
      fetchCalibrations();
    } catch (err) {
      console.error(err);
      setSyncStatus('Rollback failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8 p-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-white font-outfit">Digital Twin Engine</h1>
          <p className="text-slate-400">Manage real-time hardware calibration state snapshots and synchronization lineage</p>
        </div>
        <div className="flex gap-2 print:hidden">
          <button
            onClick={() => downloadReport('digital_twin', 'json')}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold rounded-lg border border-slate-700 text-sm flex items-center gap-2 transition"
          >
            <Download className="h-4 w-4" /> JSON Report
          </button>
          <button
            onClick={() => downloadReport('digital_twin', 'csv')}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold rounded-lg border border-slate-700 text-sm flex items-center gap-2 transition"
          >
            <Download className="h-4 w-4" /> CSV Report
          </button>
          <button
            onClick={() => window.print()}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-lg text-sm flex items-center gap-2 transition shadow-lg shadow-indigo-600/20"
          >
            Print PDF
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Left Column containing select and Glossary */}
        <div className="space-y-6">
          <div className="glass-panel p-6 space-y-6">
            <h3 className="text-lg font-bold text-white">Qubit Target Select</h3>
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Qubit ID</label>
              <select
                value={qubitId}
                onChange={(e) => setQubitId(e.target.value)}
                className="form-input"
              >
                {['Q0', 'Q1', 'Q2', 'Q3', 'Q4'].map((q) => (
                  <option key={q} value={q}>{q}</option>
                ))}
              </select>
            </div>

            <div className="border-t border-slate-800 pt-6">
              <button
                onClick={handleSync}
                disabled={loading}
                className="glow-btn w-full"
              >
                {loading ? 'Synchronizing...' : 'Trigger Sync'}
              </button>
            </div>

            {syncStatus && (
              <div className="p-3 bg-violet-500/10 border border-violet-500/30 text-violet-300 rounded-lg text-sm text-center">
                {syncStatus}
              </div>
            )}
          </div>

          {/* Digital Twin Glossary */}
          <div className="glass-panel p-6 space-y-4 text-xs">
            <h3 className="text-lg font-bold text-white font-outfit">Digital Twin Glossary</h3>
            <div className="space-y-3 text-slate-400 text-left">
              <div>
                <strong className="text-slate-200">Digital Twin:</strong> A virtual software replica of a physical qubit, logging history calibrations, forecasting drift patterns, and compiling schedules.
              </div>
              <div>
                <strong className="text-slate-200">State Version:</strong> An incremental version tag (V1, V2, etc.) cataloging a distinct, immutable state of a qubit's physical parameters.
              </div>
              <div>
                <strong className="text-slate-200">Trigger Sync:</strong> Updates the digital twin to synchronize with the active simulator calibrations, adding a new document version to the audit trail database.
              </div>
              <div>
                <strong className="text-slate-200">Perform Rollback:</strong> Restores a digital twin's calibrations back to a target historic version, reverting active parameters to those state values.
              </div>
            </div>
          </div>
        </div>

        {/* Center Twin Info Card */}
        <div className="glass-panel p-6 md:col-span-2 space-y-6">
          <h3 className="text-lg font-bold text-white">Qubit {qubitId} Twin Info</h3>
          {twinInfo ? (
            <div className="grid grid-cols-2 gap-4">
              <div className="p-4 bg-slate-900/40 rounded-lg border border-slate-800">
                <span className="text-slate-400 text-xs uppercase font-semibold">Current State Version</span>
                <p className="text-2xl font-bold mt-1 text-cyan-400">V{twinInfo.current_version}</p>
              </div>
              <div className="p-4 bg-slate-900/40 rounded-lg border border-slate-800">
                <span className="text-slate-400 text-xs uppercase font-semibold">Lifecycle State</span>
                <p className="text-2xl font-bold mt-1 text-purple-400">{twinInfo.status}</p>
              </div>
              <div className="p-4 bg-slate-900/40 rounded-lg border border-slate-800 col-span-2">
                <span className="text-slate-400 text-xs uppercase font-semibold">Last Audit Action</span>
                <p className="text-slate-200 mt-1 font-mono text-sm">
                  {twinInfo.audit_trail?.[twinInfo.audit_trail.length - 1]?.action || 'None'}
                </p>
              </div>
            </div>
          ) : (
            <div className="text-center py-10 text-slate-500">No active Digital Twin loaded in database for {qubitId}. Click Trigger Sync to initialize.</div>
          )}

          {twinInfo && (
            <form onSubmit={handleRollback} className="flex gap-4 items-end border-t border-slate-800 pt-6">
              <div className="flex-1">
                <label className="block text-sm font-medium text-slate-300 mb-2">Rollback Version</label>
                <input
                  type="number"
                  min="1"
                  max={twinInfo.current_version}
                  value={rollbackVersion}
                  onChange={(e) => setRollbackVersion(Number(e.target.value))}
                  className="form-input"
                  required
                />
              </div>
              <button
                type="submit"
                disabled={loading || twinInfo.current_version <= 1}
                className="bg-rose-600 hover:bg-rose-500 text-white font-semibold py-3 px-6 rounded-lg shadow-lg transition duration-200"
              >
                Perform Rollback
              </button>
            </form>
          )}
        </div>
      </div>

      {/* History table */}
      <div className="glass-panel p-6">
        <h3 className="text-xl font-bold text-white mb-4">Historical Calibration Records: {qubitId}</h3>
        <div className="overflow-x-auto max-h-96 overflow-y-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 text-sm">
                <th className="py-3 px-4">Epoch</th>
                <th className="py-3 px-4">T1 (µs)</th>
                <th className="py-3 px-4">T2 (µs)</th>
                <th className="py-3 px-4">Readout Error</th>
                <th className="py-3 px-4">Frequency</th>
                <th className="py-3 px-4">Temp (K)</th>
              </tr>
            </thead>
            <tbody>
              {calibrations.map((cal) => (
                <tr key={cal.epoch_number} className="border-b border-slate-800/50 hover:bg-slate-900/30">
                  <td className="py-4 px-4 font-mono">{cal.epoch_number}</td>
                  <td className="py-4 px-4 font-mono">{cal.t1.toFixed(2)}</td>
                  <td className="py-4 px-4 font-mono">{cal.t2.toFixed(2)}</td>
                  <td className="py-4 px-4 font-mono">{(cal.readout_error * 100).toFixed(3)}%</td>
                  <td className="py-4 px-4 font-mono">{cal.frequency.toFixed(3)} GHz</td>
                  <td className="py-4 px-4 font-mono">{cal.temperature.toFixed(4)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
