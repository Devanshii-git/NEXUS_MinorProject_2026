export default function LoadingSkeleton({ lines = 3, className = '' }) {
  return (
    <div className={`space-y-3 ${className}`}>
      {Array.from({ length: lines }).map((_, i) => (
        <div key={i} className="space-y-2">
          <div
            className="skeleton"
            style={{
              height: '14px',
              width: i === lines - 1 ? '60%' : `${85 + Math.random() * 15}%`,
            }}
          />
        </div>
      ))}
    </div>
  );
}

export function CardSkeleton({ count = 1, className = '' }) {
  return (
    <div className={`space-y-3 ${className}`}>
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          className="p-4 rounded-xl"
          style={{ background: 'var(--bg-secondary)' }}
        >
          <div className="flex items-center gap-3 mb-3">
            <div className="skeleton w-10 h-10 rounded-xl" />
            <div className="flex-1 space-y-2">
              <div className="skeleton h-3.5 w-3/4" />
              <div className="skeleton h-2.5 w-1/2" />
            </div>
          </div>
          <div className="space-y-2">
            <div className="skeleton h-2.5 w-full" />
            <div className="skeleton h-2.5 w-4/5" />
          </div>
        </div>
      ))}
    </div>
  );
}

export function ListSkeleton({ count = 5, className = '' }) {
  return (
    <div className={`space-y-2 ${className}`}>
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          className="flex items-center gap-3 p-3 rounded-xl"
          style={{ background: 'var(--bg-secondary)' }}
        >
          <div className="skeleton w-8 h-8 rounded-lg" />
          <div className="flex-1 space-y-1.5">
            <div className="skeleton h-3 w-2/3" />
            <div className="skeleton h-2 w-1/3" />
          </div>
          <div className="skeleton w-5 h-5 rounded" />
        </div>
      ))}
    </div>
  );
}
