import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate, useLocation } from 'react-router-dom';
import { LogIn, LogOut, User, ChevronDown, Plug, FileText, Settings, Home } from 'lucide-react';
import SutravaLogo from './SutravaLogo';
import { useAuth } from '../context/AuthContext';

function JiraIconSmall() {
  return (
    <svg width={16} height={16} viewBox="0 0 24 24" fill="none">
      <path d="M11.53 2c0 4.97 4.03 9 9 9h1.47v1.47c0 4.97-4.03 9-9 9H2V11.53C2 6.56 6.56 2 11.53 2z" fill="#2684FF"/>
      <path d="M11.53 2C11.53 6.97 7.5 11 2.53 11H2v.53c0 4.97 4.03 9 9 9h.53c4.97 0 9-4.03 9-9V11h-.53c-4.97 0-9-4.03-9-9z" fill="url(#jgn)"/>
      <defs><linearGradient id="jgn" x1="2" y1="11" x2="20.53" y2="11"><stop stopColor="#0052CC"/><stop offset="1" stopColor="#2684FF"/></linearGradient></defs>
    </svg>
  );
}

function SlackIconSmall() {
  return (
    <svg width={16} height={16} viewBox="0 0 24 24" fill="none">
      <path d="M5.042 15.165a2.528 2.528 0 0 1-2.52 2.523A2.528 2.528 0 0 1 0 15.165a2.527 2.527 0 0 1 2.522-2.52h2.52v2.52z" fill="#E01E5A"/>
      <path d="M8.834 5.042a2.528 2.528 0 0 1-2.521-2.52A2.528 2.528 0 0 1 8.834 0a2.528 2.528 0 0 1 2.521 2.522v2.52H8.834z" fill="#36C5F0"/>
      <path d="M18.956 8.834a2.528 2.528 0 0 1 2.522-2.521A2.528 2.528 0 0 1 24 8.834a2.528 2.528 0 0 1-2.522 2.521h-2.522V8.834z" fill="#2EB67D"/>
      <path d="M15.165 18.956a2.528 2.528 0 0 1 2.523 2.522A2.528 2.528 0 0 1 15.165 24a2.527 2.527 0 0 1-2.52-2.522v-2.522h2.52z" fill="#ECB22E"/>
    </svg>
  );
}

function GitHubIconSmall() {
  return (
    <svg width={16} height={16} viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
    </svg>
  );
}

// Navigation structure
const navItems = [
  { path: '/', label: 'Home', id: 'home' },
  { path: '/upload', label: 'Upload', id: 'upload' },
  { path: '/results', label: 'Results', id: 'results' },
  {
    label: 'Integrations',
    id: 'integrations',
    hasDropdown: true,
    children: [
      { path: '/integrations', label: 'All Integrations', sublabel: 'Overview of connected tools', icon: Plug },
      { path: '/integrations/jira', label: 'Jira', sublabel: 'Projects & issues', icon: JiraIconSmall, iconBg: '#eff6ff' },
      { path: '/integrations/slack', label: 'Slack', sublabel: 'Channels & messages', icon: SlackIconSmall, iconBg: '#f0fdf4' },
      { path: '/integrations/github', label: 'GitHub', sublabel: 'Repos & pull requests', icon: GitHubIconSmall, iconBg: '#f3f4f6' },
    ],
  },
  { path: '/settings', label: 'Settings', id: 'settings' },
];

export default function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, atlassianUser, isAuthenticated, isLoading, login, loginWithAtlassian, loginWithSlack, logout } = useAuth();
  const [openDropdown, setOpenDropdown] = useState(null);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [loginDropdownOpen, setLoginDropdownOpen] = useState(false);
  const dropdownTimeout = useRef(null);
  const loginDropdownRef = useRef(null);
  const dropdownRef = useRef(null);

  const displayName = atlassianUser?.name || user?.name || user?.display_name || user?.email || 'User';
  const avatarUrl = atlassianUser?.avatarUrl || user?.picture || user?.avatar_url || null;

  const isActive = (item) => {
    if (item.path) return location.pathname === item.path;
    if (item.children) return item.children.some(c => location.pathname.startsWith(c.path));
    return false;
  };

  const handleMouseEnter = (id) => {
    if (dropdownTimeout.current) clearTimeout(dropdownTimeout.current);
    setOpenDropdown(id);
  };

  const handleMouseLeave = () => {
    dropdownTimeout.current = setTimeout(() => setOpenDropdown(null), 150);
  };

  // Close dropdowns on outside click
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setOpenDropdown(null);
      }
      if (loginDropdownRef.current && !loginDropdownRef.current.contains(e.target)) {
        setLoginDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Close mobile menu on navigation
  useEffect(() => {
    setMobileMenuOpen(false);
    setOpenDropdown(null);
  }, [location.pathname]);

  return (
    <>
      <motion.nav
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-8 py-4"
        style={{
          background: 'rgba(250, 248, 245, 0.85)',
          backdropFilter: 'blur(20px)',
          WebkitBackdropFilter: 'blur(20px)',
          borderBottom: '1px solid var(--border-light)',
        }}
      >
        {/* Logo */}
        <button
          onClick={() => navigate('/')}
          className="flex items-center gap-2 cursor-pointer"
          style={{ background: 'none', border: 'none' }}
        >
          <SutravaLogo size={32} />
          <span className="font-display font-semibold text-lg" style={{ color: 'var(--text-primary)' }}>
            Sutrava
          </span>
        </button>

        {/* Desktop Nav Links */}
        <div className="hidden md:flex items-center gap-1" ref={dropdownRef}>
          {navItems.map((item) => (
            <div
              key={item.id}
              className="relative"
              onMouseEnter={() => item.hasDropdown && handleMouseEnter(item.id)}
              onMouseLeave={() => item.hasDropdown && handleMouseLeave()}
            >
              <button
                onClick={() => {
                  if (item.path) {
                    navigate(item.path);
                  } else if (item.hasDropdown) {
                    setOpenDropdown(openDropdown === item.id ? null : item.id);
                  }
                }}
                className={`px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 flex items-center gap-1 ${
                  isActive(item)
                    ? 'bg-black text-white'
                    : 'text-gray-600 hover:text-black hover:bg-gray-100'
                }`}
              >
                {item.label}
                {item.hasDropdown && (
                  <ChevronDown
                    size={13}
                    className={`transition-transform duration-200 ${openDropdown === item.id ? 'rotate-180' : ''}`}
                  />
                )}
              </button>

              {/* Dropdown panel */}
              <AnimatePresence>
                {item.hasDropdown && openDropdown === item.id && (
                  <motion.div
                    initial={{ opacity: 0, y: 8, scale: 0.96 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: 8, scale: 0.96 }}
                    transition={{ duration: 0.15, ease: 'easeOut' }}
                    className="nav-dropdown"
                    onMouseEnter={() => handleMouseEnter(item.id)}
                    onMouseLeave={handleMouseLeave}
                  >
                    {item.children.map((child) => {
                      const ChildIcon = child.icon;
                      const isChildFunc = typeof ChildIcon === 'function';
                      return (
                        <button
                          key={child.path}
                          onClick={() => {
                            navigate(child.path);
                            setOpenDropdown(null);
                          }}
                          className="nav-dropdown-item"
                        >
                          <div
                            className="dropdown-icon"
                            style={{ background: child.iconBg || 'var(--bg-secondary)' }}
                          >
                            {isChildFunc ? <ChildIcon /> : <ChildIcon size={16} style={{ color: 'var(--text-secondary)' }} />}
                          </div>
                          <div className="dropdown-label">
                            <span>{child.label}</span>
                            <span>{child.sublabel}</span>
                          </div>
                        </button>
                      );
                    })}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          ))}
        </div>

        {/* Auth CTA */}
        <div className="flex items-center gap-3">
          {/* Mobile menu toggle */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-2 rounded-lg btn-ghost"
          >
            <div className="space-y-1.5">
              <div className={`w-5 h-0.5 bg-current transition-all duration-200 ${mobileMenuOpen ? 'rotate-45 translate-y-2' : ''}`} />
              <div className={`w-5 h-0.5 bg-current transition-opacity duration-200 ${mobileMenuOpen ? 'opacity-0' : ''}`} />
              <div className={`w-5 h-0.5 bg-current transition-all duration-200 ${mobileMenuOpen ? '-rotate-45 -translate-y-2' : ''}`} />
            </div>
          </button>

          {isLoading ? (
            <div className="w-24 h-9 rounded-full animate-pulse" style={{ background: 'var(--bg-secondary)' }} />
          ) : isAuthenticated ? (
            <div className="hidden md:flex items-center gap-3">
              <div className="flex items-center gap-2">
                {avatarUrl ? (
                  <img src={avatarUrl} alt={displayName} className="w-7 h-7 rounded-full object-cover" />
                ) : (
                  <div className="w-7 h-7 rounded-full flex items-center justify-center" style={{ background: 'linear-gradient(135deg, #c8b4ff, #f5c8d8)' }}>
                    <User size={14} className="text-white" />
                  </div>
                )}
                <span className="text-xs font-medium" style={{ color: 'var(--text-secondary)' }}>
                  {displayName}
                </span>
              </div>
              <button
                onClick={logout}
                className="btn-ghost text-xs !py-1.5 !px-3 flex items-center gap-1"
                title="Logout"
              >
                <LogOut size={14} />
              </button>
            </div>
          ) : (
            <div className="hidden md:block relative" ref={loginDropdownRef}>
              <button
                onClick={() => setLoginDropdownOpen(!loginDropdownOpen)}
                className="btn-outlined text-xs !py-2 !px-4 flex items-center gap-2"
              >
                <LogIn size={14} />
                Login
                <ChevronDown
                  size={12}
                  className={`transition-transform duration-200 ${loginDropdownOpen ? 'rotate-180' : ''}`}
                />
              </button>
              <AnimatePresence>
                {loginDropdownOpen && (
                  <motion.div
                    initial={{ opacity: 0, y: 8, scale: 0.96 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: 8, scale: 0.96 }}
                    transition={{ duration: 0.15, ease: 'easeOut' }}
                    className="nav-dropdown"
                    style={{ right: 0, left: 'auto', transform: 'none', minWidth: '240px' }}
                  >
                    <button
                      onClick={() => { loginWithAtlassian(); setLoginDropdownOpen(false); }}
                      className="nav-dropdown-item"
                    >
                      <div className="dropdown-icon" style={{ background: '#eff6ff' }}>
                        <JiraIconSmall />
                      </div>
                      <div className="dropdown-label">
                        <span>Login with Atlassian</span>
                        <span>Jira projects & issues</span>
                      </div>
                    </button>
                    <button
                      onClick={() => { loginWithSlack(); setLoginDropdownOpen(false); }}
                      className="nav-dropdown-item"
                    >
                      <div className="dropdown-icon" style={{ background: '#f0fdf4' }}>
                        <SlackIconSmall />
                      </div>
                      <div className="dropdown-label">
                        <span>Login with Slack</span>
                        <span>Channels & messages</span>
                      </div>
                    </button>
                    <button
                      disabled
                      className="nav-dropdown-item opacity-40 cursor-not-allowed"
                    >
                      <div className="dropdown-icon" style={{ background: '#f3f4f6' }}>
                        <GitHubIconSmall />
                      </div>
                      <div className="dropdown-label">
                        <span>Login with GitHub</span>
                        <span>Coming soon</span>
                      </div>
                    </button>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          )}
        </div>
      </motion.nav>

      {/* Mobile Menu Overlay */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-40 md:hidden"
            style={{ background: 'rgba(0,0,0,0.3)', backdropFilter: 'blur(4px)' }}
            onClick={() => setMobileMenuOpen(false)}
          >
            <motion.div
              initial={{ x: '100%' }}
              animate={{ x: 0 }}
              exit={{ x: '100%' }}
              transition={{ type: 'spring', damping: 25, stiffness: 300 }}
              className="absolute right-0 top-0 bottom-0 w-72 p-6 pt-20"
              style={{ background: 'var(--bg-card)' }}
              onClick={(e) => e.stopPropagation()}
            >
              <div className="space-y-2">
                {navItems.map((item) => (
                  <div key={item.id}>
                    {item.path ? (
                      <button
                        onClick={() => navigate(item.path)}
                        className={`w-full text-left px-4 py-3 rounded-xl text-sm font-medium transition-all ${
                          isActive(item) ? 'bg-black text-white' : 'text-gray-600 hover:bg-gray-100'
                        }`}
                      >
                        {item.label}
                      </button>
                    ) : (
                      <>
                        <p className="px-4 py-2 text-xs font-semibold tracking-wider uppercase" style={{ color: 'var(--text-muted)' }}>
                          {item.label}
                        </p>
                        {item.children?.map((child) => (
                          <button
                            key={child.path}
                            onClick={() => navigate(child.path)}
                            className="w-full text-left px-6 py-2.5 rounded-xl text-sm font-medium text-gray-600 hover:bg-gray-100 transition-all"
                          >
                            {child.label}
                          </button>
                        ))}
                      </>
                    )}
                  </div>
                ))}
              </div>

              {/* Mobile auth */}
              <div className="mt-8 pt-6" style={{ borderTop: '1px solid var(--border-light)' }}>
                {isAuthenticated ? (
                  <div className="space-y-3">
                    <div className="flex items-center gap-2 px-4">
                      {avatarUrl ? (
                        <img src={avatarUrl} alt={displayName} className="w-8 h-8 rounded-full" />
                      ) : (
                        <div className="w-8 h-8 rounded-full" style={{ background: 'linear-gradient(135deg, #c8b4ff, #f5c8d8)' }} />
                      )}
                      <span className="text-sm font-medium">{displayName}</span>
                    </div>
                    <button onClick={logout} className="btn-ghost w-full text-left flex items-center gap-2">
                      <LogOut size={14} /> Logout
                    </button>
                  </div>
                ) : (
                  <div className="space-y-2">
                    <button onClick={loginWithAtlassian} className="btn-dark w-full flex items-center justify-center gap-2">
                      <JiraIconSmall /> Login with Atlassian
                    </button>
                    <button onClick={loginWithSlack} className="btn-outlined w-full flex items-center justify-center gap-2 !text-xs">
                      <SlackIconSmall /> Login with Slack
                    </button>
                    <button disabled className="btn-outlined w-full flex items-center justify-center gap-2 !text-xs opacity-40 cursor-not-allowed">
                      <GitHubIconSmall /> Login with GitHub
                    </button>
                  </div>
                )}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
