import { motion } from 'framer-motion';
import { BarChart3, Trophy, Star, Clock, AlertTriangle, Sparkles } from 'lucide-react';
import { useResults } from '../context/ResultsContext';
import { ListSkeleton } from '../components/ui/LoadingSkeleton';
import EmptyState from '../components/ui/EmptyState';

const getScoreColor = (s) => s >= 9 ? '#ef4444' : s >= 6 ? '#f59e0b' : s >= 3 ? '#3b82f6' : '#94a3b8';
const getRankIcon = (r) => r <= 3 ? <Trophy size={16} className={r === 1 ? 'text-amber-400' : r === 2 ? 'text-gray-400' : 'text-amber-700'} /> : <span className="text-xs font-bold" style={{ color: 'var(--text-muted)' }}>{r}</span>;

export default function PrioritizationPage() {
  const { prioritizedRequirements, hasResults, isLoading, error } = useResults();

  // Loading state
  if (isLoading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="heading-lg">Prioritization</h1>
          <p className="text-sm mt-2" style={{ color: 'var(--text-secondary)' }}>Loading prioritization data…</p>
        </div>
        <div className="card"><ListSkeleton count={6} /></div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="space-y-6">
        <div><h1 className="heading-lg">Prioritization</h1></div>
        <EmptyState icon={BarChart3} title="Prioritization Failed" description={error} iconBg="#fef2f2" iconColor="#ef4444" />
      </div>
    );
  }

  // Empty state
  if (!hasResults) {
    return (
      <div className="space-y-6">
        <div><h1 className="heading-lg">Prioritization</h1></div>
        <EmptyState
          icon={Sparkles}
          title="No prioritization data yet"
          description="Run AI analysis on Jira issues or comments to see requirement prioritization."
          iconBg="linear-gradient(135deg, #c8b4ff, #f5c8d8)"
          iconColor="#ffffff"
        />
      </div>
    );
  }

  const maxScore = Math.max(...prioritizedRequirements.map((p) => p.priorityScore), 1);
  const stats = [
    { label: 'Critical', count: prioritizedRequirements.filter((p) => p.priorityScore >= 9).length, icon: AlertTriangle, color: '#ef4444' },
    { label: 'High', count: prioritizedRequirements.filter((p) => p.priorityScore >= 6 && p.priorityScore < 9).length, icon: Star, color: '#f59e0b' },
    { label: 'Medium', count: prioritizedRequirements.filter((p) => p.priorityScore >= 3 && p.priorityScore < 6).length, icon: Clock, color: '#3b82f6' },
    { label: 'Low', count: prioritizedRequirements.filter((p) => p.priorityScore < 3).length, icon: BarChart3, color: '#94a3b8' },
  ];

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="heading-lg">Prioritization</h1>
        <p className="text-sm mt-2" style={{ color: 'var(--text-secondary)' }}>AI-powered priority scoring using multi-signal analysis</p>
      </motion.div>

      <div className="grid grid-cols-4 gap-4">
        {stats.map((stat, i) => {
          const Icon = stat.icon;
          return (
            <motion.div key={stat.label} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.08 }} className="card !p-4">
              <div className="flex items-center gap-2 mb-1">
                <Icon size={16} style={{ color: stat.color }} />
                <span className="text-xs font-semibold" style={{ color: 'var(--text-secondary)' }}>{stat.label}</span>
              </div>
              <p className="text-2xl font-bold" style={{ color: stat.color }}>{stat.count}</p>
            </motion.div>
          );
        })}
      </div>

      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="card">
        <h3 className="text-sm font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>Priority Score Distribution</h3>
        <div className="space-y-3">
          {prioritizedRequirements.map((item, idx) => (
            <div key={`${item.id}-${idx}`} className="flex items-center gap-3">
              <div className="w-5 flex justify-center shrink-0">{getRankIcon(idx + 1)}</div>
              <span className="font-mono text-xs font-semibold w-16 shrink-0">{item.id}</span>
              <div className="flex-1 relative h-7 rounded-lg overflow-hidden" style={{ background: 'var(--bg-tertiary)' }}>
                <motion.div className="absolute inset-y-0 left-0 rounded-lg flex items-center justify-end pr-3" style={{ background: getScoreColor(item.priorityScore) }} initial={{ width: 0 }} animate={{ width: `${(item.priorityScore / maxScore) * 100}%` }} transition={{ delay: 0.4 + idx * 0.04, duration: 0.6 }}>
                  <span className="text-[11px] font-bold text-white">{item.priorityScore}</span>
                </motion.div>
              </div>
            </div>
          ))}
        </div>
      </motion.div>

      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }} className="card !p-0 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="data-table">
            <thead><tr><th>Rank</th><th>ID</th><th>Requirement</th><th>Score</th><th>Type</th><th>Reason</th></tr></thead>
            <tbody>
              {prioritizedRequirements.map((item, idx) => (
                <tr key={`${item.id}-${idx}`}>
                  <td>{getRankIcon(idx + 1)}</td>
                  <td className="font-mono text-xs font-semibold">{item.id}</td>
                  <td className="max-w-xs text-sm">{item.text}</td>
                  <td><span className="text-sm font-bold" style={{ color: getScoreColor(item.priorityScore) }}>{item.priorityScore}</span></td>
                  <td className="text-xs" style={{ color: 'var(--text-secondary)' }}>{item.type}</td>
                  <td><span className="text-xs px-2 py-0.5 rounded-full" style={{ background: 'var(--bg-secondary)' }}>{item.priorityReasons[0] || '—'}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </motion.div>
    </div>
  );
}
