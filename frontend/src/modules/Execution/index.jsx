import React, { useState } from 'react';
import api from '../../services/api';
import { Download } from 'lucide-react';

export default function Execution() {
  const [circuit, setCircuit] = useState('OpenQASM 2.0;\ninclude "qelib1.inc";\nqreg q[2];\ncreg c[2];\nh q[0];\ncx q[0],q[1];\nmeasure q -> c;');
  const [mapping, setMapping] = useState('0, 1');
  const [shots, setShots] = useState(1024);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [provider, setProvider] = useState('simulator');
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

  const handleExecute = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);

    const parsedMapping = mapping.split(',').map(x => parseInt(x.trim(), 10)).filter(x => !isNaN(x));

    try {
      const response = await api.post('/quantum/execute', {
        circuit_representation: circuit,
        physical_mapping: parsedMapping,
        shots: shots,
        provider: provider
      });
      setResult(response.data);
    } catch (err) {
      console.error(err);
      alert('Circuit execution failed: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8 p-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-white font-outfit">Circuit Execution Console</h1>
          <p className="text-slate-400">Run quantum circuits mathematically on the simulated backend and verify execution fidelity</p>
        </div>
        <div className="flex gap-2 print:hidden">
          <button
            onClick={() => downloadReport('execution', 'json')}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold rounded-lg border border-slate-700 text-sm flex items-center gap-2 transition"
          >
            <Download className="h-4 w-4" /> JSON Report
          </button>
          <button
            onClick={() => downloadReport('execution', 'csv')}
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
        <div className="space-y-6 md:col-span-1">
          <div className="glass-panel p-6 space-y-6">
            <h3 className="text-lg font-bold text-white font-outfit">Execution Config</h3>
            <form onSubmit={handleExecute} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">QASM Circuit</label>
                <textarea
                  rows="6"
                  value={circuit}
                  onChange={(e) => setCircuit(e.target.value)}
                  className="form-input font-mono text-xs"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Quantum Provider Target</label>
                <select
                  value={provider}
                  onChange={(e) => setProvider(e.target.value)}
                  className="form-input"
                >
                  <option value="simulator">Mathematical Simulator</option>
                  <option value="ibm">IBM Quantum Runtime (Cloud API)</option>
                  <option value="ionq">IonQ Trapped-Ion (Cloud API)</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Physical Mapping Allocation</label>
                <input
                  type="text"
                  value={mapping}
                  onChange={(e) => setMapping(e.target.value)}
                  className="form-input font-mono"
                  required
                />
                <span className="text-xs text-slate-500 mt-1 block">Comma-separated physical indices.</span>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Shots</label>
                <input
                  type="number"
                  value={shots}
                  onChange={(e) => setShots(Number(e.target.value))}
                  className="form-input"
                  required
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="glow-btn w-full"
              >
                {loading ? 'Executing Circuit...' : 'Execute Circuit'}
              </button>
            </form>
          </div>

          <div className="glass-panel p-6 space-y-4">
            <h3 className="text-lg font-bold text-white font-outfit">Execution Glossary</h3>
            <div className="space-y-3 text-xs text-slate-400 leading-relaxed">
              <div>
                <strong className="text-slate-200 block">QASM (Quantum Assembly)</strong>
                A standard intermediate representation describing quantum circuits via gate instructions (e.g. Hadamard, CNOT) and register mapping commands.
              </div>
              <div>
                <strong className="text-slate-200 block">Physical Mapping</strong>
                Specifies which physical qubits on the backend hardware layout will execute the corresponding logical qubits of the QASM register.
              </div>
              <div>
                <strong className="text-slate-200 block">Shots Count</strong>
                The number of times the circuit is executed. Because quantum measurements collapse the superposition, many shots are required to compile the output probabilities.
              </div>
              <div>
                <strong className="text-slate-200 block">Fidelity & Success Rate</strong>
                A mathematically modeled performance indicator showing the probability that the circuit executes without error, based on physical dephasing and gate decay rates.
              </div>
            </div>
          </div>
        </div>

        <div className="glass-panel p-6 md:col-span-2 space-y-6">
          <div className="flex justify-between items-center border-b border-slate-800 pb-4">
            <h3 className="text-lg font-bold text-white font-outfit">Execution Outputs</h3>
            {result && (
              <button
                onClick={() => setShowExplanation(!showExplanation)}
                className="px-2 py-0.5 bg-slate-800 hover:bg-slate-700 text-xxs text-slate-300 font-semibold rounded border border-slate-700 transition"
              >
                {showExplanation ? 'Hide Interpretation' : 'Explain Execution Dynamics'}
              </button>
            )}
          </div>

          {result ? (
            <div className="space-y-6">
              {showExplanation && (
                <div className="p-4 bg-slate-900/50 border border-slate-800 rounded-lg text-xs text-slate-400 space-y-2">
                  <p>
                    <strong>What is happening:</strong> The quantum circuit has been transpiled and run on the target hardware backend (<code>{result.provider}</code>). The measurement shots counts show the collapsed eigenstates observed after <code>{shots}</code> repetitions.
                  </p>
                  <p>
                    <strong>Purpose:</strong> Compiling the statistical outcomes validates circuit gate accuracy. When running entangled states (like Bell states), we expect to observe highly correlated states (like |00&rang; and |11&rang;), while the presence of error states (like |01&rang; and |10&rang;) tracks active device noise levels.
                  </p>
                  <p>
                    <strong>Conclusion:</strong> With an execution success rate of <strong>{(result.success_rate * 100).toFixed(2)}%</strong>, the measurement outcomes confirm that the selected backend successfully preserved quantum coherence within noise thresholds.
                  </p>
                </div>
              )}

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="p-4 bg-slate-900/40 border border-slate-800 rounded-lg">
                  <span className="text-slate-400 text-xs uppercase font-semibold">Fidelity</span>
                  <p className="text-2xl font-bold mt-1 text-emerald-400">{(result.fidelity * 100).toFixed(2)}%</p>
                </div>
                <div className="p-4 bg-slate-900/40 border border-slate-800 rounded-lg">
                  <span className="text-slate-400 text-xs uppercase font-semibold">Success Rate</span>
                  <p className="text-2xl font-bold mt-1 text-cyan-400">{(result.success_rate * 100).toFixed(2)}%</p>
                </div>
              </div>

              <div>
                <h4 className="text-sm font-semibold text-slate-300 mb-2">Measurement Shots Counts Output</h4>
                <div className="grid grid-cols-2 gap-4">
                  {Object.entries(result.counts).map(([state, count]) => (
                    <div key={state} className="p-4 bg-slate-900/20 border border-slate-800 rounded-lg text-center font-mono">
                      <span className="text-slate-400 text-xs block">State |{state}&rang;</span>
                      <span className="text-xl font-bold text-cyan-400 block mt-1">{count} shots</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="p-4 bg-slate-900/40 border border-slate-800 rounded-lg col-span-2">
                <span className="text-slate-400 text-xs uppercase font-semibold">Job Reference Token</span>
                <p className="text-slate-200 mt-1 font-mono text-sm">{result.job_id}</p>
              </div>
            </div>
          ) : (
            <div className="text-center py-20 text-slate-500">Configure parameters and click Execute to compile mathematical runs.</div>
          )}
        </div>
      </div>
    </div>
  );
}
