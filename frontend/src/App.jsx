import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { BrowserRouter, Routes, Route, NavLink, Navigate } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Binary, 
  Cpu, 
  Compass, 
  LineChart, 
  Activity, 
  Settings as SettingsIcon, 
  CloudLightning, 
  LogOut,
  FileText,
  User as UserIcon,
  Server,
  Sun,
  Moon
} from 'lucide-react';

import Authentication from './modules/Authentication';
import Dashboard from './modules/Dashboard';
import DigitalTwin from './modules/DigitalTwin';
import MathematicalSimulator from './modules/MathematicalSimulator';
import Scheduler from './modules/Scheduler';
import Prediction from './modules/Prediction';
import Training from './modules/Training';
import Execution from './modules/Execution';
import QuantumAPIs from './modules/QuantumAPIs';
import Analytics from './modules/Analytics';
import Settings from './modules/Settings';
import Reports from './modules/Reports';
import Profile from './modules/Profile';
import SystemStatus from './modules/SystemStatus';

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(!!localStorage.getItem('token'));
  const [theme, setTheme] = useState(localStorage.getItem('theme') || 'dark');

  useEffect(() => {
    if (theme === 'light') {
      document.body.classList.add('light');
    } else {
      document.body.classList.remove('light');
    }
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark');
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    setIsAuthenticated(false);
  };

  if (!isAuthenticated) {
    return <Authentication onLoginSuccess={() => setIsAuthenticated(true)} />;
  }

  return (
    <BrowserRouter>
      <div className="flex min-h-screen text-slate-100 bg-slate-950 font-sans">
        {/* Animated Sidebar Nav */}
        <motion.aside 
          initial={{ x: -80, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ type: 'spring', stiffness: 100, damping: 20 }}
          className="w-64 glass-panel m-4 mr-0 p-6 flex flex-col justify-between border-r border-slate-800 print:hidden"
        >
          <div className="space-y-8">
            <div className="flex justify-between items-start">
              <div>
                <h2 className="text-2xl font-black tracking-wider text-transparent bg-clip-text bg-gradient-to-r from-violet-400 to-cyan-400 font-outfit">
                  TwinQ-Map
                </h2>
                <span className="text-xs text-slate-500 font-medium">IEEE Digital Twin Console</span>
              </div>
            </div>

            <nav className="space-y-2">
              <NavLink to="/dashboard" className="sidebar-link">
                <LayoutDashboard className="h-5 w-5" /> Dashboard
              </NavLink>
              <NavLink to="/digital-twin" className="sidebar-link">
                <Binary className="h-5 w-5" /> Digital Twin
              </NavLink>
              <NavLink to="/simulator" className="sidebar-link">
                <Cpu className="h-5 w-5" /> Math Simulator
              </NavLink>
              <NavLink to="/scheduler" className="sidebar-link">
                <Compass className="h-5 w-5" /> Scheduler
              </NavLink>
              <NavLink to="/reports" className="sidebar-link">
                <FileText className="h-5 w-5" /> Reports
              </NavLink>
              <NavLink to="/forecast" className="sidebar-link">
                <LineChart className="h-5 w-5" /> Forecasts
              </NavLink>
              <NavLink to="/training" className="sidebar-link">
                <Activity className="h-5 w-5" /> Training
              </NavLink>
              <NavLink to="/execution" className="sidebar-link">
                <Cpu className="h-5 w-5" /> Execution
              </NavLink>
              <NavLink to="/analytics" className="sidebar-link">
                <LineChart className="h-5 w-5" /> Analytics
              </NavLink>
              <NavLink to="/quantum-apis" className="sidebar-link">
                <CloudLightning className="h-5 w-5" /> Quantum APIs
              </NavLink>
              <NavLink to="/status" className="sidebar-link">
                <Server className="h-5 w-5" /> System Status
              </NavLink>
              <NavLink to="/profile" className="sidebar-link">
                <UserIcon className="h-5 w-5" /> Profile
              </NavLink>
              <NavLink to="/settings" className="sidebar-link">
                <SettingsIcon className="h-5 w-5" /> Settings
              </NavLink>
            </nav>
          </div>

          <div>
            <button
              onClick={handleLogout}
              className="flex items-center gap-3 w-full p-3 text-slate-400 hover:text-rose-400 rounded-lg hover:bg-rose-500/5 transition duration-150 font-semibold"
            >
              <LogOut className="h-5 w-5" /> Log Out
            </button>
          </div>
        </motion.aside>

        {/* Main Content Area with Frosted Topbar */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Frosted Glass Navbar */}
          <motion.header
            initial={{ y: -30, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.5, ease: 'easeOut' }}
            className="glass-panel m-4 mb-0 p-4 flex items-center justify-between border-b border-slate-800 print:hidden"
          >
            {/* Breadcrumb trace */}
            <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-slate-400">
              <span className="hover:text-cyan-400 cursor-pointer">TwinQ-Map</span>
              <span className="text-slate-600">/</span>
              <span className="text-cyan-400">Quantum Ops Center</span>
            </div>

            {/* Topbar Right Actions */}
            <div className="flex items-center gap-4">
              {/* Notification Audit Popover */}
              <div className="relative group">
                <button className="p-2 hover:bg-slate-800/60 dark:hover:bg-slate-850 rounded-lg text-slate-400 hover:text-cyan-400 transition">
                  <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-cyan-400 rounded-full animate-ping"></span>
                  <Server className="h-4 w-4" />
                </button>
                <div className="absolute right-0 mt-2 w-72 glass-panel p-4 hidden group-hover:block z-50 text-xs space-y-2">
                  <div className="font-bold text-white uppercase border-b border-slate-800 pb-1">Telemetry Status Logs</div>
                  <div className="text-slate-400 font-mono">- Snapshot V101 validated successfully</div>
                  <div className="text-slate-400 font-mono">- Multi-Target regressor search complete</div>
                  <div className="text-slate-400 font-mono">- Layout scheduler routing: active</div>
                </div>
              </div>

              {/* Theme Selector Toggle */}
              <button
                onClick={toggleTheme}
                className="p-2 hover:bg-slate-800/60 dark:hover:bg-slate-850 rounded-lg text-slate-400 hover:text-cyan-400 transition"
                title="Toggle Theme"
              >
                {theme === 'dark' ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
              </button>

              {/* User Profile Badge */}
              <div className="flex items-center gap-3 pl-3 border-l border-slate-800">
                <div className="h-8 w-8 rounded-full bg-gradient-to-r from-violet-500 to-cyan-500 p-0.5 shadow-lg shadow-cyan-500/10 flex items-center justify-center font-bold text-sm text-white font-outfit">
                  U
                </div>
                <div className="hidden sm:block text-left">
                  <div className="text-xs font-bold text-slate-200">{localStorage.getItem('username') || 'Lead Researcher'}</div>
                  <div className="text-[10px] text-slate-500 uppercase tracking-wider font-semibold">Administrator</div>
                </div>
              </div>
            </div>
          </motion.header>

          {/* Render target content with frame-motion transitions */}
          <main className="flex-1 overflow-y-auto p-8 pt-4">
            <Routes>
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/digital-twin" element={<DigitalTwin />} />
              <Route path="/simulator" element={<MathematicalSimulator />} />
              <Route path="/scheduler" element={<Scheduler />} />
              <Route path="/forecast" element={<Prediction />} />
              <Route path="/training" element={<Training />} />
              <Route path="/execution" element={<Execution />} />
              <Route path="/analytics" element={<Analytics />} />
              <Route path="/quantum-apis" element={<QuantumAPIs />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="/reports" element={<Reports />} />
              <Route path="/status" element={<SystemStatus />} />
              <Route path="/profile" element={<Profile />} />
              <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
          </main>
        </div>
      </div>
    </BrowserRouter>
  );
}
