import { motion } from 'framer-motion';
import { GitBranch, GitPullRequest, GitCommit, Lock } from 'lucide-react';
import ConsoleLayout from '../../components/console/ConsoleLayout';

function GitHubIcon({ size = 20 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
    </svg>
  );
}

const features = [
  {
    icon: GitBranch,
    title: 'Repositories',
    description: 'Browse and manage your GitHub repositories',
    color: '#6366f1',
    bg: '#eef2ff',
  },
  {
    icon: GitPullRequest,
    title: 'Pull Requests',
    description: 'Track open and merged pull requests',
    color: '#10b981',
    bg: '#f0fdf4',
  },
  {
    icon: GitCommit,
    title: 'Commits',
    description: 'View commit history and changes',
    color: '#f59e0b',
    bg: '#fffbeb',
  },
];

export default function GitHubConsole() {
  return (
    <ConsoleLayout
      icon={GitHubIcon}
      iconBg="#f3f4f6"
      title="GitHub"
      subtitle="Repositories, pull requests & commits"
      status="pending"
      statusLabel="Coming Soon"
    >
      <div className="card-static space-y-8">
        {/* Coming soon header */}
        <div className="text-center py-8">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="w-20 h-20 rounded-3xl mx-auto flex items-center justify-center mb-4"
            style={{ background: '#f3f4f6' }}
          >
            <GitHubIcon size={40} />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <span
              className="inline-block text-[10px] font-bold px-3 py-1 rounded-full mb-4"
              style={{ background: '#fef3c7', color: '#d97706' }}
            >
              COMING SOON
            </span>
            <h2 className="text-xl font-semibold mb-2">GitHub Integration</h2>
            <p className="text-sm max-w-md mx-auto" style={{ color: 'var(--text-muted)' }}>
              GitHub integration is on our roadmap. Connect your repositories to track code changes alongside your requirements.
            </p>
          </motion.div>
        </div>

        {/* Feature preview cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {features.map((feature, i) => {
            const Icon = feature.icon;
            return (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 + i * 0.08 }}
                className="p-5 rounded-xl opacity-60"
                style={{ background: 'var(--bg-secondary)' }}
              >
                <div
                  className="w-10 h-10 rounded-xl flex items-center justify-center mb-3"
                  style={{ background: feature.bg }}
                >
                  <Icon size={20} style={{ color: feature.color }} />
                </div>
                <h3 className="text-sm font-semibold mb-1">{feature.title}</h3>
                <p className="text-xs" style={{ color: 'var(--text-muted)' }}>{feature.description}</p>
              </motion.div>
            );
          })}
        </div>

        {/* Disabled connect button */}
        <div className="text-center pb-4">
          <button
            disabled
            className="btn-outlined opacity-40 cursor-not-allowed inline-flex items-center gap-2"
            title="GitHub OAuth integration is not yet available"
          >
            <Lock size={14} /> Connect GitHub
          </button>
          <p className="text-[10px] mt-2" style={{ color: 'var(--text-muted)' }}>
            Backend integration required — GitHub OAuth not yet configured
          </p>
        </div>
      </div>
    </ConsoleLayout>
  );
}
