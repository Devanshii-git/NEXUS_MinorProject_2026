import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { ChevronRight, CheckCircle2, XCircle, Clock } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

function JiraIcon({ size = 20 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      <path d="M11.53 2c0 4.97 4.03 9 9 9h1.47v1.47c0 4.97-4.03 9-9 9H2V11.53C2 6.56 6.56 2 11.53 2z" fill="#2684FF"/>
      <path d="M11.53 2C11.53 6.97 7.5 11 2.53 11H2v.53c0 4.97 4.03 9 9 9h.53c4.97 0 9-4.03 9-9V11h-.53c-4.97 0-9-4.03-9-9z" fill="url(#jg2)"/>
      <defs><linearGradient id="jg2" x1="2" y1="11" x2="20.53" y2="11"><stop stopColor="#0052CC"/><stop offset="1" stopColor="#2684FF"/></linearGradient></defs>
    </svg>
  );
}

function SlackIcon({ size = 20 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      <path d="M5.042 15.165a2.528 2.528 0 0 1-2.52 2.523A2.528 2.528 0 0 1 0 15.165a2.527 2.527 0 0 1 2.522-2.52h2.52v2.52zM6.313 15.165a2.527 2.527 0 0 1 2.521-2.52 2.527 2.527 0 0 1 2.521 2.52v6.313A2.528 2.528 0 0 1 8.834 24a2.528 2.528 0 0 1-2.521-2.522v-6.313z" fill="#E01E5A"/>
      <path d="M8.834 5.042a2.528 2.528 0 0 1-2.521-2.52A2.528 2.528 0 0 1 8.834 0a2.528 2.528 0 0 1 2.521 2.522v2.52H8.834zM8.834 6.313a2.528 2.528 0 0 1 2.521 2.521 2.528 2.528 0 0 1-2.521 2.521H2.522A2.528 2.528 0 0 1 0 8.834a2.528 2.528 0 0 1 2.522-2.521h6.312z" fill="#36C5F0"/>
      <path d="M18.956 8.834a2.528 2.528 0 0 1 2.522-2.521A2.528 2.528 0 0 1 24 8.834a2.528 2.528 0 0 1-2.522 2.521h-2.522V8.834zM17.688 8.834a2.528 2.528 0 0 1-2.523 2.521 2.527 2.527 0 0 1-2.52-2.521V2.522A2.527 2.527 0 0 1 15.165 0a2.528 2.528 0 0 1 2.523 2.522v6.312z" fill="#2EB67D"/>
      <path d="M15.165 18.956a2.528 2.528 0 0 1 2.523 2.522A2.528 2.528 0 0 1 15.165 24a2.527 2.527 0 0 1-2.52-2.522v-2.522h2.52zM15.165 17.688a2.527 2.527 0 0 1-2.52-2.523 2.526 2.526 0 0 1 2.52-2.52h6.313A2.527 2.527 0 0 1 24 15.165a2.528 2.528 0 0 1-2.522 2.523h-6.313z" fill="#ECB22E"/>
    </svg>
  );
}

function GitHubIcon({ size = 20 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
    </svg>
  );
}

const integrations = [
  {
    id: 'jira',
    name: 'Atlassian Jira',
    description: 'Project management & issue tracking via OAuth',
    icon: JiraIcon,
    iconBg: '#eff6ff',
    route: '/integrations/jira',
    features: ['Projects', 'Issues', 'Comments', 'Status tracking'],
  },
  {
    id: 'slack',
    name: 'Slack',
    description: 'Channels & team communication',
    icon: SlackIcon,
    iconBg: '#f0fdf4',
    route: '/integrations/slack',
    features: ['Channels', 'Messages', 'Reactions'],
  },
  {
    id: 'github',
    name: 'GitHub',
    description: 'Repositories, pull requests & commits',
    icon: GitHubIcon,
    iconBg: '#f3f4f6',
    route: '/integrations/github',
    features: ['Repositories', 'Pull Requests', 'Commits'],
    comingSoon: true,
  },
];

export default function IntegrationsPage() {
  const navigate = useNavigate();
  const { isAuthenticated, isAtlassianConnected, isSlackConnected } = useAuth();

  const getStatus = (id) => {
    if (id === 'github') return 'coming-soon';
    if (id === 'jira') return isAtlassianConnected ? 'connected' : isAuthenticated ? 'available' : 'disconnected';
    if (id === 'slack') return isSlackConnected ? 'connected' : isAuthenticated ? 'available' : 'disconnected';
    return 'disconnected';
  };

  const statusConfig = {
    connected: { icon: CheckCircle2, label: 'Connected', color: '#10b981', bg: '#f0fdf4' },
    available: { icon: Clock, label: 'Available', color: '#d97706', bg: '#fef3c7' },
    disconnected: { icon: XCircle, label: 'Not connected', color: '#9ca3af', bg: '#f9fafb' },
    'coming-soon': { icon: Clock, label: 'Coming Soon', color: '#d97706', bg: '#fef3c7' },
  };

  return (
    <div className="max-w-5xl mx-auto px-6 py-12">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="heading-lg">Integrations</h1>
        <p className="text-sm mt-2" style={{ color: 'var(--text-secondary)' }}>
          Connect your tools to streamline requirements engineering
        </p>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
        {integrations.map((integration, i) => {
          const Icon = integration.icon;
          const status = getStatus(integration.id);
          const statusInfo = statusConfig[status];
          const StatusIcon = statusInfo.icon;

          return (
            <motion.div
              key={integration.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.08 }}
              onClick={() => navigate(integration.route)}
              className={`card group cursor-pointer ${integration.comingSoon ? 'opacity-75' : ''}`}
            >
              {/* Header */}
              <div className="flex items-start justify-between mb-4">
                <div
                  className="w-12 h-12 rounded-2xl flex items-center justify-center"
                  style={{ background: integration.iconBg }}
                >
                  <Icon size={26} />
                </div>
                <span
                  className="inline-flex items-center gap-1 text-[10px] font-semibold px-2 py-1 rounded-full"
                  style={{ background: statusInfo.bg, color: statusInfo.color }}
                >
                  <StatusIcon size={12} />
                  {statusInfo.label}
                </span>
              </div>

              {/* Title */}
              <h3 className="text-base font-bold mb-1">{integration.name}</h3>
              <p className="text-xs mb-4" style={{ color: 'var(--text-muted)' }}>
                {integration.description}
              </p>

              {/* Features list */}
              <div className="flex flex-wrap gap-1.5 mb-4">
                {integration.features.map((f) => (
                  <span
                    key={f}
                    className="text-[10px] font-medium px-2 py-0.5 rounded-full"
                    style={{ background: 'var(--bg-secondary)', color: 'var(--text-secondary)' }}
                  >
                    {f}
                  </span>
                ))}
              </div>

              {/* Action */}
              <div
                className="flex items-center gap-1 text-xs font-medium pt-3 transition-colors group-hover:text-black"
                style={{ borderTop: '1px solid var(--border-light)', color: 'var(--text-muted)' }}
              >
                {integration.comingSoon ? 'View details' : 'Open console'}
                <ChevronRight size={14} className="transition-transform group-hover:translate-x-1" />
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
