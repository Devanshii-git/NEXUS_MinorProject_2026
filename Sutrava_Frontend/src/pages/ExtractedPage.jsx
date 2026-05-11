import { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import { Search, ArrowUpDown, ChevronDown, Tag, FileText, Sparkles } from 'lucide-react';
import { useResults } from '../context/ResultsContext';
import { ListSkeleton } from '../components/ui/LoadingSkeleton';
import EmptyState from '../components/ui/EmptyState';

const priorityColors = {
  Critical: 'bg-red-50 text-red-600 border-red-200',
  High: 'bg-orange-50 text-orange-600 border-orange-200',
  Medium: 'bg-amber-50 text-amber-600 border-amber-200',
  Low: 'bg-emerald-50 text-emerald-600 border-emerald-200',
};

const typeColors = {
  Functional: 'bg-blue-50 text-blue-600 border-blue-200',
  'Non-Functional': 'bg-purple-50 text-purple-600 border-purple-200',
  Ambiguous: 'bg-yellow-50 text-yellow-600 border-yellow-200',
};

export default function ExtractedPage() {
  const { allRequirements, hasResults, isLoading, error } = useResults();
  const [search, setSearch] = useState('');
  const [sortKey, setSortKey] = useState('id');
  const [sortDir, setSortDir] = useState('asc');
  const [filterType, setFilterType] = useState('All');
  const [filterPriority, setFilterPriority] = useState('All');

  const filtered = useMemo(() => {
    let list = [...allRequirements];

    if (search) {
      const lower = search.toLowerCase();
      list = list.filter(
        (r) =>
          r.id.toLowerCase().includes(lower) ||
          r.text.toLowerCase().includes(lower) ||
          r.source.toLowerCase().includes(lower)
      );
    }

    if (filterType !== 'All') list = list.filter((r) => r.type === filterType);
    if (filterPriority !== 'All') list = list.filter((r) => r.priority === filterPriority);

    list.sort((a, b) => {
      let cmp = 0;
      if (sortKey === 'confidence') cmp = a.confidence - b.confidence;
      else cmp = String(a[sortKey]).localeCompare(String(b[sortKey]));
      return sortDir === 'asc' ? cmp : -cmp;
    });

    return list;
  }, [allRequirements, search, sortKey, sortDir, filterType, filterPriority]);

  const handleSort = (key) => {
    if (sortKey === key) setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'));
    else {
      setSortKey(key);
      setSortDir('asc');
    }
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="heading-lg">Extracted Requirements</h1>
          <p className="text-sm mt-2" style={{ color: 'var(--text-secondary)' }}>Loading analysis results…</p>
        </div>
        <div className="card">
          <ListSkeleton count={8} />
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="heading-lg">Extracted Requirements</h1>
        </div>
        <EmptyState
          icon={FileText}
          title="Analysis Failed"
          description={error}
          iconBg="#fef2f2"
          iconColor="#ef4444"
        />
      </div>
    );
  }

  // Empty state — no results yet
  if (!hasResults) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="heading-lg">Extracted Requirements</h1>
        </div>
        <EmptyState
          icon={Sparkles}
          title="No analysis data yet"
          description="Navigate to Integrations → Jira, select issues or comments, and run AI analysis to see extracted requirements here."
          iconBg="linear-gradient(135deg, #c8b4ff, #f5c8d8)"
          iconColor="#ffffff"
        />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="heading-lg">Extracted Requirements</h1>
        <p className="text-sm mt-2" style={{ color: 'var(--text-secondary)' }}>
          {filtered.length} requirements extracted from AI analysis
        </p>
      </motion.div>

      {/* Toolbar */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="flex flex-wrap items-center gap-3"
      >
        <div className="relative flex-1 min-w-[240px]">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2" style={{ color: 'var(--text-muted)' }} />
          <input
            type="text"
            placeholder="Search requirements…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="input-field !pl-10"
          />
        </div>

        <div className="relative">
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="input-field !pr-8 appearance-none cursor-pointer !w-auto"
          >
            <option value="All">All Types</option>
            <option value="Functional">Functional</option>
            <option value="Non-Functional">Non-Functional</option>
            <option value="Ambiguous">Ambiguous</option>
          </select>
          <ChevronDown size={14} className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none" style={{ color: 'var(--text-muted)' }} />
        </div>

        <div className="relative">
          <select
            value={filterPriority}
            onChange={(e) => setFilterPriority(e.target.value)}
            className="input-field !pr-8 appearance-none cursor-pointer !w-auto"
          >
            <option value="All">All Priorities</option>
            <option value="Critical">Critical</option>
            <option value="High">High</option>
            <option value="Medium">Medium</option>
            <option value="Low">Low</option>
          </select>
          <ChevronDown size={14} className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none" style={{ color: 'var(--text-muted)' }} />
        </div>
      </motion.div>

      {/* Table */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="card !p-0 overflow-hidden"
      >
        <div className="overflow-x-auto max-h-[600px] overflow-y-auto">
          <table className="data-table">
            <thead>
              <tr>
                {[
                  { key: 'id', label: 'ID' },
                  { key: 'text', label: 'Requirement' },
                  { key: 'type', label: 'Type' },
                  { key: 'priority', label: 'Priority' },
                  { key: 'source', label: 'Source' },
                  { key: 'confidence', label: 'Confidence' },
                ].map((col) => (
                  <th
                    key={col.key}
                    onClick={() => handleSort(col.key)}
                    className="cursor-pointer select-none hover:text-black transition-colors"
                  >
                    <div className="flex items-center gap-1.5">
                      {col.label}
                      <ArrowUpDown size={12} className={sortKey === col.key ? 'text-black' : 'opacity-30'} />
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filtered.length > 0 ? filtered.map((req, idx) => (
                <motion.tr
                  key={`${req.id}-${idx}`}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: idx * 0.02 }}
                >
                  <td className="font-mono text-xs font-semibold" style={{ color: 'var(--text-primary)' }}>{req.id}</td>
                  <td className="max-w-xs">
                    <p className="text-sm leading-relaxed" style={{ color: 'var(--text-primary)' }}>
                      {req.text}
                    </p>
                  </td>
                  <td>
                    <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium border ${typeColors[req.type] || ''}`}>
                      <Tag size={11} /> {req.type}
                    </span>
                  </td>
                  <td>
                    <span className={`inline-block px-2.5 py-1 rounded-full text-xs font-medium border ${priorityColors[req.priority] || ''}`}>
                      {req.priority}
                    </span>
                  </td>
                  <td className="text-xs" style={{ color: 'var(--text-secondary)' }}>{req.source}</td>
                  <td>
                    <div className="flex items-center gap-2">
                      <div className="w-16 h-1.5 rounded-full overflow-hidden" style={{ background: 'var(--bg-tertiary)' }}>
                        <div
                          className="h-full rounded-full"
                          style={{
                            width: `${req.confidence * 100}%`,
                            background: req.confidence > 0.9 ? '#10b981' : req.confidence > 0.7 ? '#f59e0b' : '#ef4444',
                          }}
                        />
                      </div>
                      <span className="text-xs font-mono font-semibold" style={{ color: 'var(--text-secondary)' }}>
                        {(req.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                  </td>
                </motion.tr>
              )) : (
                <tr>
                  <td colSpan={6} className="text-center text-sm py-8" style={{ color: 'var(--text-muted)' }}>
                    No requirements match current filters. Try clearing search or filters.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </motion.div>
    </div>
  );
}
