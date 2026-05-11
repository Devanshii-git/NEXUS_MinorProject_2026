import { useState } from 'react';
import { motion } from 'framer-motion';
import { LayoutGrid, List, Hash, Layers, Sparkles } from 'lucide-react';
import { useResults } from '../context/ResultsContext';
import { ListSkeleton } from '../components/ui/LoadingSkeleton';
import EmptyState from '../components/ui/EmptyState';

export default function ClusteringPage() {
  const { clusters, hasResults, isLoading, error } = useResults();
  const [viewMode, setViewMode] = useState('grid');

  // Loading state
  if (isLoading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="heading-lg">Requirement Clusters</h1>
          <p className="text-sm mt-2" style={{ color: 'var(--text-secondary)' }}>Loading cluster data…</p>
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
        <div><h1 className="heading-lg">Requirement Clusters</h1></div>
        <EmptyState icon={Layers} title="Clustering Failed" description={error} iconBg="#fef2f2" iconColor="#ef4444" />
      </div>
    );
  }

  // Empty state
  if (!hasResults) {
    return (
      <div className="space-y-6">
        <div><h1 className="heading-lg">Requirement Clusters</h1></div>
        <EmptyState
          icon={Sparkles}
          title="No cluster data yet"
          description="Run AI analysis on Jira issues or comments to see requirement clusters."
          iconBg="linear-gradient(135deg, #c8b4ff, #f5c8d8)"
          iconColor="#ffffff"
        />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="flex items-start justify-between">
        <div>
          <h1 className="heading-lg">Requirement Clusters</h1>
          <p className="text-sm mt-2" style={{ color: 'var(--text-secondary)' }}>
            {clusters.length} clusters identified from requirement analysis
          </p>
        </div>
        <div className="flex items-center gap-1 p-1 rounded-xl" style={{ background: 'var(--bg-secondary)' }}>
          <button
            onClick={() => setViewMode('grid')}
            className={`p-2 rounded-lg transition-all duration-200 ${viewMode === 'grid' ? 'bg-black text-white' : 'btn-ghost'}`}
          >
            <LayoutGrid size={16} />
          </button>
          <button
            onClick={() => setViewMode('list')}
            className={`p-2 rounded-lg transition-all duration-200 ${viewMode === 'list' ? 'bg-black text-white' : 'btn-ghost'}`}
          >
            <List size={16} />
          </button>
        </div>
      </motion.div>

      {viewMode === 'grid' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {clusters.map((cluster, i) => (
            <motion.div
              key={cluster.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.06 }}
              className="card group"
              style={{ borderLeft: `3px solid ${cluster.color}` }}
            >
              <div className="flex items-center gap-2 mb-3">
                <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ background: `${cluster.color}15` }}>
                  <Layers size={16} style={{ color: cluster.color }} />
                </div>
                <h3 className="text-sm font-bold flex-1" style={{ color: 'var(--text-primary)' }}>
                  {cluster.name}
                </h3>
              </div>

              {cluster.keywords.length > 0 && (
                <div className="flex flex-wrap gap-1.5 mb-4">
                  {cluster.keywords.map((kw) => (
                    <span key={kw} className="px-2 py-0.5 rounded-full text-[10px] font-semibold" style={{ background: `${cluster.color}10`, color: cluster.color }}>
                      {kw}
                    </span>
                  ))}
                </div>
              )}

              <div className="space-y-2">
                {cluster.requirements.map((req, idx) => (
                  <div key={`${req.id}-${idx}`} className="flex items-start gap-2 p-2 rounded-lg transition-colors" style={{ background: 'var(--bg-secondary)' }}>
                    <span className="font-mono text-[10px] font-bold shrink-0 mt-0.5" style={{ color: 'var(--text-primary)' }}>{req.id}</span>
                    <p className="text-xs leading-relaxed" style={{ color: 'var(--text-secondary)' }}>{req.text}</p>
                  </div>
                ))}
              </div>

              <div className="mt-4 pt-3 flex items-center justify-between" style={{ borderTop: '1px solid var(--border-light)' }}>
                <span className="text-xs font-medium" style={{ color: 'var(--text-muted)' }}>
                  {cluster.requirements.length} requirements
                </span>
                <div className="flex items-center gap-1">
                  <Hash size={12} style={{ color: cluster.color }} />
                  <span className="text-xs font-bold" style={{ color: cluster.color }}>{cluster.id}</span>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      ) : (
        <div className="space-y-3">
          {clusters.map((cluster, i) => (
            <motion.div
              key={cluster.id}
              initial={{ opacity: 0, x: -16 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.05 }}
              className="card !p-0 overflow-hidden"
            >
              <div className="px-5 py-3 flex items-center gap-3" style={{ borderLeft: `3px solid ${cluster.color}` }}>
                <Layers size={16} style={{ color: cluster.color }} />
                <h3 className="text-sm font-bold flex-1" style={{ color: 'var(--text-primary)' }}>{cluster.name}</h3>
                <div className="flex flex-wrap gap-1.5">
                  {cluster.keywords.slice(0, 3).map((kw) => (
                    <span key={kw} className="px-2 py-0.5 rounded-full text-[10px] font-semibold" style={{ background: `${cluster.color}10`, color: cluster.color }}>
                      {kw}
                    </span>
                  ))}
                </div>
                <span className="text-xs font-semibold px-2 py-0.5 rounded-full" style={{ background: `${cluster.color}15`, color: cluster.color }}>
                  {cluster.requirements.length}
                </span>
              </div>
              <div className="px-5 py-2 divide-y" style={{ borderColor: 'var(--border-light)' }}>
                {cluster.requirements.map((req, idx) => (
                  <div key={`${req.id}-${idx}`} className="flex items-center gap-3 py-2">
                    <span className="font-mono text-xs font-semibold" style={{ color: 'var(--text-primary)' }}>{req.id}</span>
                    <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>{req.text}</p>
                  </div>
                ))}
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}
