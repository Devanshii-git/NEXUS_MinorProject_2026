/**
 * Sutrava Logo — An abstract mark representing scattered information
 * converging into a structured central nexus (threads).
 */
export default function SutravaLogo({ size = 32, className = '' }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 48 48"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      <defs>
        <linearGradient id="sutrava-grad" x1="0" y1="0" x2="48" y2="48" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor="#6366f1" />
          <stop offset="50%" stopColor="#8b5cf6" />
          <stop offset="100%" stopColor="#ec4899" />
        </linearGradient>
        <linearGradient id="sutrava-grad2" x1="48" y1="0" x2="0" y2="48" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor="#818cf8" />
          <stop offset="100%" stopColor="#f472b6" />
        </linearGradient>
      </defs>

      {/* Central hub node */}
      <circle cx="24" cy="24" r="5" fill="url(#sutrava-grad)" />

      {/* Outer scattered nodes */}
      <circle cx="8" cy="8" r="2.5" fill="url(#sutrava-grad2)" opacity="0.7" />
      <circle cx="40" cy="8" r="2.5" fill="url(#sutrava-grad2)" opacity="0.7" />
      <circle cx="8" cy="40" r="2.5" fill="url(#sutrava-grad2)" opacity="0.7" />
      <circle cx="40" cy="40" r="2.5" fill="url(#sutrava-grad2)" opacity="0.7" />
      <circle cx="24" cy="4" r="2" fill="url(#sutrava-grad2)" opacity="0.5" />
      <circle cx="24" cy="44" r="2" fill="url(#sutrava-grad2)" opacity="0.5" />
      <circle cx="4" cy="24" r="2" fill="url(#sutrava-grad2)" opacity="0.5" />
      <circle cx="44" cy="24" r="2" fill="url(#sutrava-grad2)" opacity="0.5" />

      {/* Connecting threads — converging lines */}
      <line x1="8" y1="8" x2="20" y2="20" stroke="url(#sutrava-grad)" strokeWidth="1.2" opacity="0.6" />
      <line x1="40" y1="8" x2="28" y2="20" stroke="url(#sutrava-grad)" strokeWidth="1.2" opacity="0.6" />
      <line x1="8" y1="40" x2="20" y2="28" stroke="url(#sutrava-grad)" strokeWidth="1.2" opacity="0.6" />
      <line x1="40" y1="40" x2="28" y2="28" stroke="url(#sutrava-grad)" strokeWidth="1.2" opacity="0.6" />
      <line x1="24" y1="4" x2="24" y2="19" stroke="url(#sutrava-grad)" strokeWidth="1.2" opacity="0.5" />
      <line x1="24" y1="44" x2="24" y2="29" stroke="url(#sutrava-grad)" strokeWidth="1.2" opacity="0.5" />
      <line x1="4" y1="24" x2="19" y2="24" stroke="url(#sutrava-grad)" strokeWidth="1.2" opacity="0.5" />
      <line x1="44" y1="24" x2="29" y2="24" stroke="url(#sutrava-grad)" strokeWidth="1.2" opacity="0.5" />

      {/* Inner ring — structured thread orbit */}
      <circle cx="24" cy="24" r="12" stroke="url(#sutrava-grad)" strokeWidth="1" fill="none" opacity="0.25" />
      <circle cx="24" cy="24" r="18" stroke="url(#sutrava-grad2)" strokeWidth="0.7" fill="none" opacity="0.15" strokeDasharray="3 4" />
    </svg>
  );
}
