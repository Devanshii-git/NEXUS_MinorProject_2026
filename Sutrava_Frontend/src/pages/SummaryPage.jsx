import { motion } from 'framer-motion';
import { FileText, BarChart3, Network, AlertTriangle, Download, FileJson, FileSpreadsheet, Printer, Sparkles } from 'lucide-react';
import { useResults } from '../context/ResultsContext';
import { ListSkeleton } from '../components/ui/LoadingSkeleton';
import EmptyState from '../components/ui/EmptyState';

const exportFormats = [
  { label: 'PDF Report', icon: Printer, desc: 'Formatted document with charts' },
  { label: 'CSV Spreadsheet', icon: FileSpreadsheet, desc: 'Raw data for analysis' },
  { label: 'JSON Export', icon: FileJson, desc: 'Structured data for APIs' },
];

export default function SummaryPage() {
  const { summaryStats, classificationGroups, hasResults, isLoading, error, rawResponse } = useResults();

  const handleExport = (format) => {
    if (format === 'JSON Export' && rawResponse) {
      const blob = new Blob([JSON.stringify(rawResponse, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'requirements_analysis.json';
      a.click();
      URL.revokeObjectURL(url);
    } else {
      alert(`Export as ${format} — coming soon`);
    }
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="heading-lg">Summary Report</h1>
          <p className="text-sm mt-2" style={{ color: 'var(--text-secondary)' }}>Loading summary…</p>
        </div>
        <div className="grid grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="card"><ListSkeleton count={2} /></div>
          ))}
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="space-y-6">
        <div><h1 className="heading-lg">Summary Report</h1></div>
        <EmptyState icon={FileText} title="Summary Failed" description={error} iconBg="#fef2f2" iconColor="#ef4444" />
      </div>
    );
  }

  // Empty state
  if (!hasResults || !summaryStats) {
    return (
      <div className="space-y-6">
        <div><h1 className="heading-lg">Summary Report</h1></div>
        <EmptyState
          icon={Sparkles}
          title="No analysis data yet"
          description="Run AI analysis on Jira issues or comments to see the summary report."
          iconBg="linear-gradient(135deg, #c8b4ff, #f5c8d8)"
          iconColor="#ffffff"
        />
      </div>
    );
  }

  const insights = [
    { label: 'Total Requirements', value: String(summaryStats.totalRequirements), icon: FileText, color: '#6366f1' },
    { label: 'Avg Priority Score', value: summaryStats.avgPriorityScore, icon: BarChart3, color: '#f59e0b' },
    { label: 'Clusters Identified', value: String(summaryStats.totalClusters), icon: Network, color: '#10b981' },
    { label: 'Ambiguity Rate', value: `${summaryStats.ambiguityRate}%`, icon: AlertTriangle, color: '#ef4444' },
  ];

  const breakdownData = [
    { label: 'Functional', count: summaryStats.functional, pct: summaryStats.totalRequirements > 0 ? Math.round((summaryStats.functional / summaryStats.totalRequirements) * 100) : 0, color: '#3b82f6' },
    { label: 'Non-Functional', count: summaryStats.nonFunctional, pct: summaryStats.totalRequirements > 0 ? Math.round((summaryStats.nonFunctional / summaryStats.totalRequirements) * 100) : 0, color: '#8b5cf6' },
    { label: 'Ambiguous', count: summaryStats.ambiguous, pct: summaryStats.totalRequirements > 0 ? Math.round((summaryStats.ambiguous / summaryStats.totalRequirements) * 100) : 0, color: '#f59e0b' },
  ];

  // Generate activity from actual data
  const generatedAt = rawResponse?.metadata?.generated_at;
  const timeline = [
    { text: `${summaryStats.totalRequirements} requirements analyzed`, icon: FileText, color: '#3b82f6' },
    { text: `${summaryStats.totalClusters} clusters identified`, icon: Network, color: '#6366f1' },
    { text: `${summaryStats.functional} functional, ${summaryStats.nonFunctional} non-functional classified`, icon: BarChart3, color: '#f59e0b' },
    ...(summaryStats.ambiguous > 0 ? [{ text: `${summaryStats.ambiguous} ambiguous requirement(s) flagged`, icon: AlertTriangle, color: '#ef4444' }] : []),
    ...(generatedAt ? [{ text: `Analysis generated at ${new Date(generatedAt).toLocaleString()}`, icon: FileText, color: '#8b5cf6' }] : []),
  ];

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="heading-lg">Summary Report</h1>
        <p className="text-sm mt-2" style={{ color: 'var(--text-secondary)' }}>Complete overview of your requirements analysis</p>
      </motion.div>

      <div className="grid grid-cols-4 gap-4">
        {insights.map((item, i) => {
          const Icon = item.icon;
          return (
            <motion.div key={item.label} initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.08 }} className="card">
              <div className="flex items-center justify-between mb-2">
                <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: `${item.color}12` }}>
                  <Icon size={20} style={{ color: item.color }} />
                </div>
              </div>
              <p className="text-2xl font-bold mt-2">{item.value}</p>
              <p className="text-xs mt-0.5" style={{ color: 'var(--text-muted)' }}>{item.label}</p>
            </motion.div>
          );
        })}
      </div>

      <div className="grid grid-cols-3 gap-4">
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="card">
          <h3 className="text-sm font-semibold mb-4">Type Breakdown</h3>
          <div className="space-y-3">
            {breakdownData.map((item, i) => (
              <div key={item.label}>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-medium" style={{ color: 'var(--text-secondary)' }}>{item.label}</span>
                  <span className="text-xs font-bold" style={{ color: item.color }}>{item.count} ({item.pct}%)</span>
                </div>
                <div className="h-2 rounded-full overflow-hidden" style={{ background: 'var(--bg-tertiary)' }}>
                  <motion.div className="h-full rounded-full" style={{ background: item.color }} initial={{ width: 0 }} animate={{ width: `${item.pct}%` }} transition={{ delay: 0.5 + i * 0.1, duration: 0.7 }} />
                </div>
              </div>
            ))}
          </div>
          <div className="mt-4 h-3 rounded-full overflow-hidden flex">
            {breakdownData.map((item) => (
              <motion.div key={item.label} className="h-full" style={{ background: item.color }} initial={{ width: 0 }} animate={{ width: `${item.pct}%` }} transition={{ delay: 0.8, duration: 0.6 }} />
            ))}
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }} className="card">
          <h3 className="text-sm font-semibold mb-4">Analysis Summary</h3>
          <div className="space-y-3">
            {timeline.map((item, i) => {
              const Icon = item.icon;
              return (
                <motion.div key={i} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.5 + i * 0.06 }} className="flex items-start gap-3">
                  <div className="w-7 h-7 rounded-lg flex items-center justify-center shrink-0" style={{ background: `${item.color}12` }}>
                    <Icon size={14} style={{ color: item.color }} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs leading-relaxed">{item.text}</p>
                  </div>
                </motion.div>
              );
            })}
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }} className="card">
          <h3 className="text-sm font-semibold mb-4">Export Report</h3>
          <div className="space-y-3">
            {exportFormats.map((fmt) => {
              const Icon = fmt.icon;
              return (
                <button key={fmt.label} onClick={() => handleExport(fmt.label)} className="w-full flex items-center gap-3 p-3 rounded-xl transition-all duration-200 group hover:bg-gray-50" style={{ background: 'var(--bg-secondary)' }}>
                  <div className="w-9 h-9 rounded-lg flex items-center justify-center" style={{ background: 'var(--bg-card)' }}>
                    <Icon size={18} style={{ color: 'var(--text-primary)' }} />
                  </div>
                  <div className="text-left flex-1">
                    <p className="text-sm font-semibold">{fmt.label}</p>
                    <p className="text-[10px]" style={{ color: 'var(--text-muted)' }}>{fmt.desc}</p>
                  </div>
                  <Download size={14} style={{ color: 'var(--text-muted)' }} />
                </button>
              );
            })}
          </div>
        </motion.div>
      </div>
    </div>
  );
}
