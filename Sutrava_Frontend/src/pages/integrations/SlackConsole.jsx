import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Hash,
  ArrowLeft,
  LogIn,
  RefreshCw,
  Search,
  Users,
  Lock,
  Globe,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { getSlackChannels, getSlackMessages } from '../../services/api';
import ConsoleLayout from '../../components/console/ConsoleLayout';
import EmptyState from '../../components/ui/EmptyState';
import { ListSkeleton } from '../../components/ui/LoadingSkeleton';

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

export default function SlackConsole() {
  const { isAuthenticated, isSlackConnected, slackUser, loginWithSlack } = useAuth();

  const [channels, setChannels] = useState([]);
  const [loadingChannels, setLoadingChannels] = useState(false);
  const [channelError, setChannelError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');

  const [selectedChannel, setSelectedChannel] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loadingMessages, setLoadingMessages] = useState(false);

  useEffect(() => {
    if (isAuthenticated) fetchChannels();
  }, [isAuthenticated]);

  const fetchChannels = async () => {
    setLoadingChannels(true);
    setChannelError(null);
    try {
      const data = await getSlackChannels();
      if (data) {
        setChannels(data);
      }
    } catch (err) {
      setChannelError('Slack integration not yet configured');
      console.error(err);
    } finally {
      setLoadingChannels(false);
    }
  };

  const handleChannelClick = async (channel) => {
    setSelectedChannel(channel);
    setLoadingMessages(true);
    try {
      const data = await getSlackMessages(channel.id);
      if (data) setMessages(data);
      else setMessages([]);
    } catch (err) {
      console.error('Failed to fetch messages:', err);
      setMessages([]);
    } finally {
      setLoadingMessages(false);
    }
  };

  const handleBack = () => {
    setSelectedChannel(null);
    setMessages([]);
  };

  const filteredChannels = channels.filter(ch =>
    ch.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const formatTimestamp = (ts) => {
    if (!ts) return '';
    try {
      return new Date(parseFloat(ts) * 1000).toLocaleString(undefined, {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return '';
    }
  };

  const connectionStatus = isSlackConnected ? 'connected' : channels.length > 0 ? 'connected' : 'disconnected';

  // Not authenticated
  if (!isAuthenticated) {
    return (
      <ConsoleLayout
        icon={SlackIcon}
        iconBg="#f0fdf4"
        title="Slack"
        subtitle="Channels & team communication"
        status="disconnected"
      >
        <div className="card-static text-center py-16">
          <div className="w-20 h-20 rounded-3xl mx-auto flex items-center justify-center mb-4" style={{ background: '#f0fdf4' }}>
            <SlackIcon size={40} />
          </div>
          <h3 className="text-lg font-semibold mb-2">Connect with Slack</h3>
          <p className="text-sm mb-6 max-w-md mx-auto" style={{ color: 'var(--text-muted)' }}>
            Sign in with your Slack workspace to access channels and messages
          </p>
          <button onClick={loginWithSlack} className="btn-dark inline-flex items-center gap-2">
            <LogIn size={16} /> Login with Slack
          </button>
        </div>
      </ConsoleLayout>
    );
  }

  return (
    <ConsoleLayout
      icon={SlackIcon}
      iconBg="#f0fdf4"
      title="Slack"
      subtitle="Channels & team communication"
      status={connectionStatus}
      userName={slackUser?.name}
      userAvatar={slackUser?.avatarUrl}
    >
      {loadingChannels ? (
        <div className="card-static">
          <ListSkeleton count={6} />
        </div>
      ) : channelError || channels.length === 0 ? (
        <div className="card-static text-center py-12">
          <div className="w-16 h-16 rounded-2xl mx-auto flex items-center justify-center mb-4 opacity-60" style={{ background: '#f0fdf4' }}>
            <SlackIcon size={28} />
          </div>
          <h3 className="text-base font-semibold mb-1">Slack Integration</h3>
          <p className="text-sm max-w-sm mx-auto" style={{ color: 'var(--text-muted)' }}>
            {channelError || 'Slack OAuth not yet configured. Configure Slack credentials in the backend to enable this integration.'}
          </p>
          <button onClick={fetchChannels} className="btn-ghost text-xs mt-4 inline-flex items-center gap-1">
            <RefreshCw size={12} /> Retry
          </button>
        </div>
      ) : (
        <div className="console-container">
          {/* Channel sidebar */}
          <div className="console-sidebar">
            <div className="console-sidebar-header">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-xs font-semibold" style={{ color: 'var(--text-secondary)' }}>
                  <Hash size={12} className="inline mr-1" />Channels ({channels.length})
                </h3>
                <button onClick={fetchChannels} className="btn-ghost !p-1" title="Refresh">
                  <RefreshCw size={12} />
                </button>
              </div>
              <div className="relative">
                <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2" style={{ color: 'var(--text-muted)' }} />
                <input
                  type="text"
                  placeholder="Search channels…"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="input-field !pl-9 !py-2 text-xs"
                />
              </div>
            </div>
            <div className="flex-1 overflow-y-auto">
              {filteredChannels.map((ch) => (
                <div
                  key={ch.id}
                  onClick={() => handleChannelClick(ch)}
                  className={`console-sidebar-item ${selectedChannel?.id === ch.id ? 'active' : ''}`}
                >
                  <div className="flex items-center gap-2 flex-1 min-w-0">
                    {ch.isPublic ? (
                      <Hash size={14} style={{ color: 'var(--text-muted)' }} />
                    ) : (
                      <Lock size={14} style={{ color: 'var(--text-muted)' }} />
                    )}
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">{ch.name}</p>
                      {ch.topic && (
                        <p className="text-[10px] truncate" style={{ color: 'var(--text-muted)' }}>{ch.topic}</p>
                      )}
                    </div>
                  </div>
                  {ch.isMember && (
                    <Users size={10} className="shrink-0" style={{ color: 'var(--text-muted)' }} />
                  )}
                </div>
              ))}
              {filteredChannels.length === 0 && (
                <div className="p-6 text-center">
                  <p className="text-xs" style={{ color: 'var(--text-muted)' }}>No channels match your search</p>
                </div>
              )}
            </div>
          </div>

          {/* Messages panel */}
          <div className="console-main">
            {selectedChannel ? (
              <>
                <div className="console-main-header">
                  <button onClick={handleBack} className="btn-ghost !p-1 lg:hidden"><ArrowLeft size={14} /></button>
                  <Hash size={16} style={{ color: 'var(--text-muted)' }} />
                  <div className="flex-1 min-w-0">
                    <h3 className="text-sm font-semibold truncate">{selectedChannel.name}</h3>
                    {selectedChannel.purpose && (
                      <p className="text-[10px] truncate" style={{ color: 'var(--text-muted)' }}>{selectedChannel.purpose}</p>
                    )}
                  </div>
                </div>
                <div className="console-main-content">
                  {loadingMessages ? (
                    <ListSkeleton count={6} />
                  ) : messages.length > 0 ? (
                    <div className="space-y-3">
                      {messages.map((msg, idx) => (
                        <motion.div
                          key={idx}
                          initial={{ opacity: 0, y: 8 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: idx * 0.02 }}
                          className="flex gap-3"
                        >
                          <div className="w-8 h-8 rounded-lg shrink-0 flex items-center justify-center text-[10px] font-bold" style={{ background: 'var(--bg-secondary)', color: 'var(--text-muted)' }}>
                            {(msg.user || '?')[0].toUpperCase()}
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-0.5">
                              <span className="text-xs font-semibold">{msg.user || 'Unknown'}</span>
                              <span className="text-[10px]" style={{ color: 'var(--text-muted)' }}>{formatTimestamp(msg.timestamp)}</span>
                            </div>
                            <p className="text-sm leading-relaxed" style={{ color: 'var(--text-secondary)' }}>{msg.text}</p>
                            {msg.reactions && msg.reactions.length > 0 && (
                              <div className="flex items-center gap-1.5 mt-1.5">
                                {msg.reactions.map((reaction, ri) => (
                                  <span
                                    key={ri}
                                    className="text-[10px] px-2 py-0.5 rounded-full font-medium"
                                    style={{ background: 'var(--bg-secondary)', color: 'var(--text-secondary)' }}
                                  >
                                    :{reaction.name}: {reaction.count}
                                  </span>
                                ))}
                              </div>
                            )}
                          </div>
                        </motion.div>
                      ))}
                    </div>
                  ) : (
                    <EmptyState
                      icon={Hash}
                      title="No messages"
                      description="This channel doesn't have any messages yet"
                      iconBg="#f0fdf4"
                      iconColor="#2EB67D"
                    />
                  )}
                </div>
              </>
            ) : (
              <div className="flex items-center justify-center h-full">
                <EmptyState
                  icon={Hash}
                  title="Select a channel"
                  description="Choose a channel from the sidebar to view messages"
                  iconBg="#f0fdf4"
                  iconColor="#2EB67D"
                />
              </div>
            )}
          </div>
        </div>
      )}
    </ConsoleLayout>
  );
}
