import { useMemo } from 'react';
import { motion } from 'framer-motion';
import { CheckCircle2, TrendingUp, HelpCircle, Tag, Sparkles } from 'lucide-react';
import { useResults } from '../context/ResultsContext';
import { ListSkeleton } from '../components/ui/LoadingSkeleton';
import EmptyState from '../components/ui/EmptyState';

const categoryConfig = {
  Functional: {
    color: '#3b82f6',
    bgLight: '#eff6ff',
    borderLight: '#dbeafe',
    icon: CheckCircle2,
  },
  'Non-Functional': {
    color: '#8b5cf6',
    bgLight: '#f5f3ff',
    borderLight: '#ede9fe',
    icon: TrendingUp,
  },
  Ambiguous: {
    color: '#f59e0b',
    bgLight: '#fffbeb',
    borderLight: '#fef3c7',
    icon: HelpCircle,
  },
};

export default function ClassificationPage() {
  const { classificationGroups, hasResults, isLoading, error, allRequirements } = useResults();

  const classificationData = useMemo(() => {
    const data = {};
    Object.entries(classificationGroups).forEach(([type, reqs]) => {
      if (reqs.length > 0) {
        data[type] = {
          ...categoryConfig[type],
          items: reqs.map((r) => ({
            id: r.id,
            text: r.text,
            confidence: r.confidence,
          })),
        };
      }
    });
    return data;
  }, [classificationGroups]);

  const totalCount = allRequirements.length;

  // Loading state
  if (isLoading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="heading-lg">Classification Results</h1>
          <p className="text-sm mt-2" style={{ color: 'var(--text-secondary)' }}>Loading classification data…</p>
        </div>
        <div className="grid grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="card"><ListSkeleton count={3} /></div>
          ))}
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="space-y-6">
        <div><h1 className="heading-lg">Classification Results</h1></div>
        <EmptyState icon={Tag} title="Classification Failed" description={error} iconBg="#fef2f2" iconColor="#ef4444" />
      </div>
    );
  }

  // Empty state
  if (!hasResults) {
    return (
      <div className="space-y-6">
        <div><h1 className="heading-lg">Classification Results</h1></div>
        <EmptyState
          icon={Sparkles}
          title="No classification data yet"
          description="Run AI analysis on Jira issues or comments to see requirement classification."
          iconBg="linear-gradient(135deg, #c8b4ff, #f5c8d8)"
          iconColor="#ffffff"
        />
      </div>
    );
  }

  if (totalCount === 0 || Object.keys(classificationData).length === 0) {
    return (
      <div className="space-y-6">
        <div><h1 className="heading-lg">Classification Results</h1></div>
        <EmptyState
          icon={Tag}
          title="Classification data unavailable"
          description="AI response was parsed, but no classifiable requirements were found."
          iconBg="#fff7ed"
          iconColor="#f97316"
        />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="heading-lg">Classification Results</h1>
        <p className="text-sm mt-2" style={{ color: 'var(--text-secondary)' }}>
          {totalCount} requirements classified into {Object.keys(classificationData).length} categories
        </p>
      </motion.div>

      {/* Summary cards */}
      <div className="grid grid-cols-3 gap-4">
        {Object.entries(classificationData).map(([label, data], i) => {
          const Icon = data.icon;
          const pct = totalCount > 0 ? ((data.items.length / totalCount) * 100).toFixed(0) : 0;
          return (
            <motion.div
              key={label}
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              className="card"
              style={{ borderLeft: `3px solid ${data.color}` }}
            >
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <Icon size={18} style={{ color: data.color }} />
                  <span className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>{label}</span>
                </div>
                <span className="text-2xl font-bold" style={{ color: data.color }}>{data.items.length}</span>
              </div>
              <div className="h-1.5 rounded-full overflow-hidden" style={{ background: 'var(--bg-tertiary)' }}>
                <motion.div
                  className="h-full rounded-full"
                  style={{ background: data.color }}
                  initial={{ width: 0 }}
                  animate={{ width: `${pct}%` }}
                  transition={{ delay: 0.3 + i * 0.1, duration: 0.8 }}
                />
              </div>
              <p className="text-xs mt-2 font-medium" style={{ color: 'var(--text-muted)' }}>{pct}% of total</p>
            </motion.div>
          );
        })}
      </div>

      {/* Detailed sections */}
      {Object.entries(classificationData).map(([label, data], i) => {
        const Icon = data.icon;
        return (
          <motion.div
            key={label}
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 + i * 0.1 }}
            className="card !p-0 overflow-hidden"
          >
            <div className="px-5 py-3 flex items-center gap-2 border-b" style={{ borderColor: 'var(--border-light)' }}>
              <Icon size={16} style={{ color: data.color }} />
              <h3 className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>{label} Requirements</h3>
              <span
                className="ml-auto text-xs px-2 py-0.5 rounded-full font-semibold"
                style={{ background: data.bgLight, color: data.color }}
              >
                {data.items.length}
              </span>
            </div>
            <div className="divide-y" style={{ borderColor: 'var(--border-light)' }}>
              {data.items.map((item, idx) => (
                <div key={`${item.id}-${idx}`} className="px-5 py-3 flex items-center gap-4 hover:bg-gray-50 transition-colors">
                  <span className="font-mono text-xs font-semibold w-20 shrink-0" style={{ color: 'var(--text-primary)' }}>{item.id}</span>
                  <p className="text-sm flex-1" style={{ color: 'var(--text-primary)' }}>{item.text}</p>
                  <div className="flex items-center gap-2 shrink-0">
                    <div className="w-14 h-1.5 rounded-full overflow-hidden" style={{ background: 'var(--bg-tertiary)' }}>
                      <div className="h-full rounded-full" style={{ width: `${item.confidence * 100}%`, background: data.color }} />
                    </div>
                    <span className="text-xs font-mono font-semibold w-10 text-right" style={{ color: 'var(--text-secondary)' }}>
                      {(item.confidence * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        );
      })}
    </div>
  );
}
