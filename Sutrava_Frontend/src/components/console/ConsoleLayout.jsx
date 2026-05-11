import { motion } from 'framer-motion';
import { ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import StatusBadge from '../ui/StatusBadge';

export default function ConsoleLayout({
  icon: Icon,
  iconBg = '#eff6ff',
  title,
  subtitle,
  status = 'disconnected',
  statusLabel,
  userAvatar,
  userName,
  children,
  backTo = '/integrations',
  backLabel = 'Integrations',
}) {
  const navigate = useNavigate();

  return (
    <div className="max-w-6xl mx-auto px-6 py-8">
      {/* Back link */}
      <motion.button
        initial={{ opacity: 0, x: -8 }}
        animate={{ opacity: 1, x: 0 }}
        onClick={() => navigate(backTo)}
        className="flex items-center gap-1.5 text-xs font-medium mb-6 transition-colors"
        style={{ color: 'var(--text-muted)' }}
        onMouseEnter={(e) => (e.currentTarget.style.color = 'var(--text-primary)')}
        onMouseLeave={(e) => (e.currentTarget.style.color = 'var(--text-muted)')}
      >
        <ArrowLeft size={14} />
        {backLabel}
      </motion.button>

      {/* Console header */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center gap-4 mb-8"
      >
        {Icon && (
          <div
            className="w-12 h-12 rounded-2xl flex items-center justify-center"
            style={{ background: iconBg }}
          >
            <Icon size={26} />
          </div>
        )}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-3">
            <h1 className="heading-lg !text-2xl">{title}</h1>
            <StatusBadge status={status} label={statusLabel} size="lg" />
          </div>
          {subtitle && (
            <p className="text-sm mt-0.5" style={{ color: 'var(--text-muted)' }}>
              {subtitle}
            </p>
          )}
        </div>

        {/* User info */}
        {userName && (
          <div className="flex items-center gap-2 px-3 py-2 rounded-xl" style={{ background: 'var(--bg-secondary)' }}>
            {userAvatar ? (
              <img src={userAvatar} alt={userName} className="w-6 h-6 rounded-full object-cover" />
            ) : (
              <div className="w-6 h-6 rounded-full" style={{ background: 'var(--bg-tertiary)' }} />
            )}
            <span className="text-xs font-medium" style={{ color: 'var(--text-secondary)' }}>
              {userName}
            </span>
          </div>
        )}
      </motion.div>

      {/* Console content */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        {children}
      </motion.div>
    </div>
  );
}
