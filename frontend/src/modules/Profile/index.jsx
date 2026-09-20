import React from 'react';

export default function Profile() {
  const username = localStorage.getItem('username') || 'Researcher';
  
  return (
    <div className="space-y-8 p-6">
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight text-white font-outfit">User Profile</h1>
        <p className="text-slate-400">Authenticated researcher profile details</p>
      </div>

      <div className="max-w-xl glass-panel p-6 space-y-6">
        <div className="flex items-center gap-4">
          <div className="h-16 w-16 rounded-full bg-gradient-to-tr from-violet-600 to-cyan-500 flex items-center justify-center text-white font-bold text-2xl font-outfit">
            {username.substring(0, 2).toUpperCase()}
          </div>
          <div>
            <h2 className="text-xl font-bold text-white">{username}</h2>
            <p className="text-slate-400 text-sm">Quantum Computing Engineer</p>
          </div>
        </div>

        <div className="border-t border-slate-800 pt-6 space-y-4">
          <div className="flex justify-between items-center text-sm">
            <span className="text-slate-400">Authorized Role</span>
            <span className="font-mono text-cyan-400 bg-cyan-950/20 px-2 py-0.5 border border-cyan-800/30 rounded">
              Administrator
            </span>
          </div>

          <div className="flex justify-between items-center text-sm">
            <span className="text-slate-400">System Permissions</span>
            <span className="text-slate-200">Full CRUD, Predictor Training, Job Scheduler</span>
          </div>
        </div>
      </div>
    </div>
  );
}
