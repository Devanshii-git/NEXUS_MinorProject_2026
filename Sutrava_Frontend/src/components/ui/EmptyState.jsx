import { motion } from 'framer-motion';

export default function EmptyState({
  icon: Icon,
  title = 'Nothing here yet',
  description = '',
  actionLabel,
  onAction,
  iconBg = 'var(--bg-secondary)',
  iconColor = 'var(--text-muted)',
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex flex-col items-center justify-center py-12 px-6 text-center"
    >
      {Icon && (
        <div
          className="w-16 h-16 rounded-2xl flex items-center justify-center mb-4"
          style={{ background: iconBg }}
        >
          <Icon size={28} style={{ color: iconColor }} />
        </div>
      )}
      <h3
        className="text-base font-semibold mb-1"
        style={{ color: 'var(--text-primary)' }}
      >
        {title}
      </h3>
      {description && (
        <p
          className="text-sm max-w-sm"
          style={{ color: 'var(--text-muted)' }}
        >
          {description}
        </p>
      )}
      {actionLabel && onAction && (
        <button onClick={onAction} className="btn-dark mt-4 text-xs !py-2 !px-5">
          {actionLabel}
        </button>
      )}
    </motion.div>
  );
}
