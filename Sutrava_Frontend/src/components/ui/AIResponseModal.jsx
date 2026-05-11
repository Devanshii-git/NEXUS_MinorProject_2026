import { motion, AnimatePresence } from 'framer-motion';
import { X, Sparkles, FileText, ArrowRight, CheckCircle2, AlertTriangle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { parseAndNormalizeResponse } from '../../utils/resultsParser';

/**
 * Modal panel for displaying AI/NLP analysis results inline.
 * Shows a summary of the analysis and a "View Full Results" button.
 */
export default function AIResponseModal({ isOpen, onClose, response, title = 'AI Analysis Complete' }) {
  const navigate = useNavigate();

  if (!response) return null;

  const parsedResult = parseAndNormalizeResponse(response);
  const parsed = parsedResult?.payload;
  const totalReqs = parsedResult?.metadata?.totalRequirements || 0;
  const totalClusters = parsedResult?.metadata?.totalClusters || 0;
  const groups = parsedResult?.groups || [];

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 flex items-center justify-center p-4"
          style={{ background: 'rgba(0,0,0,0.4)', backdropFilter: 'blur(4px)' }}
          onClick={onClose}
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ duration: 0.2 }}
            className="w-full max-w-lg max-h-[80vh] overflow-hidden rounded-2xl shadow-2xl"
            style={{ background: 'var(--bg-card)' }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="flex items-center justify-between px-6 py-4" style={{ borderBottom: '1px solid var(--border-light)' }}>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: 'linear-gradient(135deg, #c8b4ff, #f5c8d8)' }}>
                  <Sparkles size={20} className="text-white" />
                </div>
                <div>
                  <h3 className="text-sm font-bold" style={{ color: 'var(--text-primary)' }}>{title}</h3>
                  <p className="text-[10px]" style={{ color: 'var(--text-muted)' }}>NLP pipeline analysis complete</p>
                </div>
              </div>
              <button onClick={onClose} className="btn-ghost !p-1.5 rounded-lg">
                <X size={16} />
              </button>
            </div>

            {/* Stats */}
            <div className="px-6 py-4 grid grid-cols-2 gap-3">
              <div className="p-3 rounded-xl" style={{ background: 'var(--bg-secondary)' }}>
                <div className="flex items-center gap-2 mb-1">
                  <FileText size={14} style={{ color: '#6366f1' }} />
                  <span className="text-xs font-medium" style={{ color: 'var(--text-secondary)' }}>Requirements</span>
                </div>
                <p className="text-xl font-bold" style={{ color: '#6366f1' }}>{totalReqs}</p>
              </div>
              <div className="p-3 rounded-xl" style={{ background: 'var(--bg-secondary)' }}>
                <div className="flex items-center gap-2 mb-1">
                  <CheckCircle2 size={14} style={{ color: '#10b981' }} />
                  <span className="text-xs font-medium" style={{ color: 'var(--text-secondary)' }}>Clusters</span>
                </div>
                <p className="text-xl font-bold" style={{ color: '#10b981' }}>{totalClusters}</p>
              </div>
            </div>

            {/* Requirement groups preview */}
            <div className="px-6 pb-2 max-h-[300px] overflow-y-auto">
              <p className="text-xs font-semibold mb-2" style={{ color: 'var(--text-secondary)' }}>Requirement Groups</p>
              {parsed && groups.length > 0 ? (
                <div className="space-y-2">
                  {groups.slice(0, 5).map((group, idx) => (
                    <motion.div
                      key={group.group_id || idx}
                      initial={{ opacity: 0, y: 6 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: idx * 0.05 }}
                      className="p-3 rounded-xl"
                      style={{ background: 'var(--bg-secondary)' }}
                    >
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded" style={{ background: '#eff6ff', color: '#2684FF' }}>
                          {group.group_id || group.cluster_id || `G-${idx + 1}`}
                        </span>
                        <span className={`text-[10px] px-1.5 py-0.5 rounded font-semibold ${
                          (group.priority || group.cluster_priority) === 'HIGH' ? 'text-red-600 bg-red-50' :
                          (group.priority || group.cluster_priority) === 'MEDIUM' ? 'text-amber-600 bg-amber-50' :
                          'text-emerald-600 bg-emerald-50'
                        }`}>
                          {group.priority || group.cluster_priority || 'LOW'}
                        </span>
                      </div>
                      <p className="text-xs font-semibold mt-1" style={{ color: 'var(--text-primary)' }}>
                        {group.group_name || group.cluster_name || `Cluster ${idx + 1}`}
                      </p>
                      <p className="text-[11px] mt-0.5 line-clamp-2" style={{ color: 'var(--text-muted)' }}>
                        {group.summary || group.cluster_summary || parsedResult.message}
                      </p>
                      <p className="text-[10px] mt-1" style={{ color: 'var(--text-muted)' }}>
                        {group.requirements?.length || 0} requirement{(group.requirements?.length || 0) !== 1 ? 's' : ''}
                      </p>
                    </motion.div>
                  ))}
                  {groups.length > 5 && (
                    <p className="text-[10px] text-center py-1" style={{ color: 'var(--text-muted)' }}>
                      +{groups.length - 5} more groups
                    </p>
                  )}
                </div>
              ) : (
                <div className="flex items-center gap-2 p-3 rounded-xl" style={{ background: '#fef2f2' }}>
                  <AlertTriangle size={14} className="text-red-400" />
                  <p className="text-xs text-red-500">
                    {parsed ? 'No requirement groups found in AI response' : 'Failed to parse AI response'}
                  </p>
                </div>
              )}
            </div>

            {/* Footer actions */}
            <div className="px-6 py-4 flex items-center gap-3" style={{ borderTop: '1px solid var(--border-light)' }}>
              <button onClick={onClose} className="btn-ghost text-xs flex-1">
                Close
              </button>
              <button
                onClick={() => {
                  onClose();
                  navigate('/results');
                }}
                className="btn-dark text-xs flex-1 flex items-center justify-center gap-2"
              >
                View Full Results <ArrowRight size={14} />
              </button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
