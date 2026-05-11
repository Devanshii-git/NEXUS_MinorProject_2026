import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Palette,
  Server,
  Info,
  Save,
  RotateCcw,
  Type,
  Monitor,
  Globe,
  CheckCircle2,
  XCircle,
  Loader2,
  Zap,
} from 'lucide-react';
import SutravaLogo from '../components/SutravaLogo';
import { getApiBase, testBackendConnection } from '../services/api';

export default function SettingsPage() {
  const [apiEndpoint, setApiEndpoint] = useState(getApiBase());
  const [fontSize, setFontSize] = useState('14');
  const [language, setLanguage] = useState('en');
  const [saved, setSaved] = useState(false);

  // Connection test state
  const [connectionStatus, setConnectionStatus] = useState('idle'); // idle | testing | success | error
  const [connectionMessage, setConnectionMessage] = useState('');

  const handleSave = () => { setSaved(true); setTimeout(() => setSaved(false), 2000); };

  const handleTestConnection = async () => {
    setConnectionStatus('testing');
    setConnectionMessage('');
    try {
      const result = await testBackendConnection();
      if (result && result.body) {
        setConnectionStatus('success');
        setConnectionMessage(`Backend responded: ${result.body}`);
      } else {
        setConnectionStatus('error');
        setConnectionMessage('Backend returned empty response');
      }
    } catch (err) {
      setConnectionStatus('error');
      setConnectionMessage(`Connection failed: ${err.message}`);
    }
  };

  return (
    <div className="max-w-3xl space-y-6">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="heading-lg">Settings</h1>
        <p className="text-sm mt-2" style={{ color: 'var(--text-secondary)' }}>Customize your application preferences</p>
      </motion.div>

      {/* Appearance */}
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="card space-y-4">
        <div className="flex items-center gap-2 mb-2">
          <Palette size={18} style={{ color: 'var(--text-primary)' }} />
          <h2 className="text-sm font-bold">Appearance</h2>
        </div>

        <div className="flex items-center justify-between p-3 rounded-xl" style={{ background: 'var(--bg-secondary)' }}>
          <div className="flex items-center gap-3">
            <Type size={18} style={{ color: 'var(--text-primary)' }} />
            <div>
              <p className="text-sm font-semibold">Font Size</p>
              <p className="text-[10px]" style={{ color: 'var(--text-muted)' }}>Adjust base font size</p>
            </div>
          </div>
          <select value={fontSize} onChange={(e) => setFontSize(e.target.value)} className="input-field !w-24 text-center">
            <option value="12">12px</option>
            <option value="13">13px</option>
            <option value="14">14px</option>
            <option value="15">15px</option>
            <option value="16">16px</option>
          </select>
        </div>

        <div className="flex items-center justify-between p-3 rounded-xl" style={{ background: 'var(--bg-secondary)' }}>
          <div className="flex items-center gap-3">
            <Globe size={18} style={{ color: 'var(--text-primary)' }} />
            <div>
              <p className="text-sm font-semibold">Language</p>
              <p className="text-[10px]" style={{ color: 'var(--text-muted)' }}>Interface language</p>
            </div>
          </div>
          <select value={language} onChange={(e) => setLanguage(e.target.value)} className="input-field !w-32">
            <option value="en">English</option>
            <option value="hi">Hindi</option>
            <option value="fr">French</option>
          </select>
        </div>
      </motion.div>

      {/* API Configuration */}
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="card space-y-4">
        <div className="flex items-center gap-2 mb-2">
          <Server size={18} style={{ color: 'var(--text-primary)' }} />
          <h2 className="text-sm font-bold">API Configuration</h2>
        </div>
        <div>
          <label className="text-xs font-semibold block mb-1.5" style={{ color: 'var(--text-secondary)' }}>Backend Endpoint</label>
          <input className="input-field font-mono text-xs" value={apiEndpoint} onChange={(e) => setApiEndpoint(e.target.value)} placeholder="http://localhost:8080" />
        </div>

        {/* Connection status */}
        <div className="flex items-center gap-3 p-3 rounded-xl" style={{ background: 'var(--bg-secondary)' }}>
          {connectionStatus === 'testing' && <Loader2 size={16} className="text-blue-500 animate-spin" />}
          {connectionStatus === 'success' && <CheckCircle2 size={16} className="text-emerald-500" />}
          {connectionStatus === 'error' && <XCircle size={16} className="text-red-500" />}
          {connectionStatus === 'idle' && <Monitor size={16} className="text-gray-400" />}
          <div className="flex-1">
            <p className="text-xs font-semibold">
              {connectionStatus === 'testing' && 'Testing connection…'}
              {connectionStatus === 'success' && 'Connection successful'}
              {connectionStatus === 'error' && 'Connection failed'}
              {connectionStatus === 'idle' && 'Connection Status'}
            </p>
            <p className="text-[10px]" style={{ color: 'var(--text-muted)' }}>
              {connectionMessage || (connectionStatus === 'idle' ? 'Click "Test Connection" to verify backend availability' : '')}
            </p>
          </div>
          {connectionStatus === 'success' && <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />}
          {connectionStatus === 'error' && <div className="w-2 h-2 bg-red-500 rounded-full" />}
        </div>

        <button
          onClick={handleTestConnection}
          disabled={connectionStatus === 'testing'}
          className="btn-outlined w-full flex items-center justify-center gap-2 text-xs disabled:opacity-50"
        >
          <Zap size={14} />
          {connectionStatus === 'testing' ? 'Testing…' : 'Test Connection'}
        </button>
      </motion.div>

      {/* About */}
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="card">
        <div className="flex items-center gap-2 mb-3">
          <Info size={18} style={{ color: 'var(--text-primary)' }} />
          <h2 className="text-sm font-bold">About</h2>
        </div>
        <div className="flex items-center gap-4 p-4 rounded-xl" style={{ background: 'var(--bg-secondary)' }}>
          <div className="w-12 h-12 rounded-xl flex items-center justify-center shrink-0" style={{ background: 'linear-gradient(135deg, #c8b4ff, #f5c8d8)' }}>
            <SutravaLogo size={28} />
          </div>
          <div>
            <h3 className="text-base font-bold">Sutrava</h3>
            <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>AI-Driven Automated Requirements Engineering System</p>
            <p className="text-[10px] mt-1" style={{ color: 'var(--text-muted)' }}>Version 1.0.0 • Built with React + Vite • Backend: Spring Boot 4</p>
          </div>
        </div>
      </motion.div>

      {/* Save bar */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex items-center gap-3">
        <button onClick={handleSave} className="btn-dark flex items-center gap-2">
          <Save size={16} /> {saved ? 'Saved!' : 'Save Settings'}
        </button>
        <button className="btn-ghost flex items-center gap-2">
          <RotateCcw size={14} /> Reset to Defaults
        </button>
      </motion.div>
    </div>
  );
}
