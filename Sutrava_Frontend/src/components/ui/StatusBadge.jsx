import { CheckCircle2, XCircle, Loader2, Clock } from 'lucide-react';

const variants = {
  connected: {
    icon: CheckCircle2,
    color: '#10b981',
    bg: '#f0fdf4',
    label: 'Connected',
  },
  disconnected: {
    icon: XCircle,
    color: '#9ca3af',
    bg: '#f9fafb',
    label: 'Not connected',
  },
  pending: {
    icon: Clock,
    color: '#d97706',
    bg: '#fef3c7',
    label: 'Pending',
  },
  loading: {
    icon: Loader2,
    color: '#3b82f6',
    bg: '#eff6ff',
    label: 'Loading…',
  },
  error: {
    icon: XCircle,
    color: '#ef4444',
    bg: '#fef2f2',
    label: 'Error',
  },
};

export default function StatusBadge({ status = 'disconnected', label, size = 'sm' }) {
  const config = variants[status] || variants.disconnected;
  const Icon = config.icon;
  const displayLabel = label || config.label;

  const sizeClasses = size === 'lg'
    ? 'text-xs px-3 py-1.5 gap-1.5'
    : 'text-[10px] px-2 py-1 gap-1';

  return (
    <span
      className={`inline-flex items-center font-semibold rounded-full ${sizeClasses}`}
      style={{ background: config.bg, color: config.color }}
    >
      <Icon
        size={size === 'lg' ? 14 : 12}
        className={status === 'loading' ? 'animate-spin' : ''}
      />
      {displayLabel}
    </span>
  );
}
