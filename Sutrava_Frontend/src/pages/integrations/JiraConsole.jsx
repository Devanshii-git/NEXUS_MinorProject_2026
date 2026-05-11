import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Loader2, RefreshCw, FolderOpen, Globe, ChevronDown, ChevronRight,
  Lock, MessageSquare, ArrowLeft, FileText, LogIn, AlertCircle, Sparkles, CheckSquare, Square,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useResults } from '../../context/ResultsContext';
import {
  getAtlassianResources, getAtlassianProjects, getAtlassianIssues,
  getAtlassianComments, processIssuesWithAI, processCommentsWithAI,
} from '../../services/api';
import ConsoleLayout from '../../components/console/ConsoleLayout';
import EmptyState from '../../components/ui/EmptyState';
import { ListSkeleton } from '../../components/ui/LoadingSkeleton';
import AIResponseModal from '../../components/ui/AIResponseModal';

function JiraIcon({ size = 20 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      <path d="M11.53 2c0 4.97 4.03 9 9 9h1.47v1.47c0 4.97-4.03 9-9 9H2V11.53C2 6.56 6.56 2 11.53 2z" fill="#2684FF"/>
      <path d="M11.53 2C11.53 6.97 7.5 11 2.53 11H2v.53c0 4.97 4.03 9 9 9h.53c4.97 0 9-4.03 9-9V11h-.53c-4.97 0-9-4.03-9-9z" fill="url(#jg)"/>
      <defs><linearGradient id="jg" x1="2" y1="11" x2="20.53" y2="11"><stop stopColor="#0052CC"/><stop offset="1" stopColor="#2684FF"/></linearGradient></defs>
    </svg>
  );
}

export default function JiraConsole() {
  const { isAuthenticated, isAtlassianConnected, atlassianUser, loginWithAtlassian } = useAuth();
  const { storeResults, setIsLoading: setResultsLoading, setError: setResultsError } = useResults();

  const [resources, setResources] = useState([]);
  const [selectedResource, setSelectedResource] = useState(null);
  const [projects, setProjects] = useState([]);
  const [loadingResources, setLoadingResources] = useState(false);
  const [loadingProjects, setLoadingProjects] = useState(false);
  const [resourceError, setResourceError] = useState(null);

  const [selectedProject, setSelectedProject] = useState(null);
  const [issues, setIssues] = useState(null);
  const [loadingIssues, setLoadingIssues] = useState(false);
  const [issuesPage, setIssuesPage] = useState(0);

  const [selectedIssue, setSelectedIssue] = useState(null);
  const [comments, setComments] = useState(null);
  const [loadingComments, setLoadingComments] = useState(false);

  // AI selection state
  const [selectedIssueKeys, setSelectedIssueKeys] = useState(new Set());
  const [selectedCommentIds, setSelectedCommentIds] = useState(new Set());
  const [aiProcessing, setAiProcessing] = useState(false);
  const [aiError, setAiError] = useState(null);
  const [aiModalOpen, setAiModalOpen] = useState(false);
  const [aiResponse, setAiResponse] = useState(null);

  useEffect(() => { if (isAuthenticated) fetchResources(); }, [isAuthenticated]);

  const fetchResources = async () => {
    setLoadingResources(true); setResourceError(null);
    try {
      const data = await getAtlassianResources();
      if (data) { setResources(data); if (data.length > 0) { setSelectedResource(data[0]); fetchProjects(data[0].id); } }
    } catch (err) { setResourceError('Failed to load Atlassian resources'); console.error(err); }
    finally { setLoadingResources(false); }
  };

  const fetchProjects = async (cloudId) => {
    setLoadingProjects(true); setSelectedProject(null); setIssues(null); setSelectedIssue(null); setComments(null);
    try { const data = await getAtlassianProjects(cloudId); if (data) setProjects(data); }
    catch (err) { console.error('Failed to fetch projects:', err); }
    finally { setLoadingProjects(false); }
  };

  const fetchIssues = async (projectKey, startAt = 0) => {
    if (!selectedResource) return;
    setLoadingIssues(true); setSelectedIssue(null); setComments(null); setIssuesPage(startAt); setSelectedIssueKeys(new Set());
    try { const data = await getAtlassianIssues(selectedResource.id, projectKey, startAt); if (data) setIssues(data); }
    catch (err) { console.error('Failed to fetch issues:', err); }
    finally { setLoadingIssues(false); }
  };

  const fetchComments = async (issueKey) => {
    if (!selectedResource) return;
    setLoadingComments(true); setSelectedCommentIds(new Set());
    try { const data = await getAtlassianComments(selectedResource.id, issueKey); if (data) setComments(data); }
    catch (err) { console.error('Failed to fetch comments:', err); }
    finally { setLoadingComments(false); }
  };

  const handleResourceChange = (e) => { const r = resources.find(r => r.id === e.target.value); setSelectedResource(r); if (r) fetchProjects(r.id); };
  const handleProjectClick = (proj) => { setSelectedProject(proj); fetchIssues(proj.key); };
  const handleIssueClick = (issue) => { setSelectedIssue(issue); fetchComments(issue.key); };
  const handleBackToProjects = () => { setSelectedProject(null); setIssues(null); setSelectedIssue(null); setComments(null); };
  const handleBackToIssues = () => { setSelectedIssue(null); setComments(null); };

  const extractText = (field) => {
    if (!field) return '';
    if (typeof field === 'string') return field;
    if (field.content) return field.content.map(block => (block.content || []).map(inline => inline.text || '').join('')).join('\n');
    return JSON.stringify(field);
  };

  // Issue selection
  const toggleIssueSelection = (key) => {
    setSelectedIssueKeys(prev => { const next = new Set(prev); next.has(key) ? next.delete(key) : next.add(key); return next; });
  };
  const toggleAllIssues = () => {
    if (!issues?.issues) return;
    if (selectedIssueKeys.size === issues.issues.length) setSelectedIssueKeys(new Set());
    else setSelectedIssueKeys(new Set(issues.issues.map(i => i.key)));
  };

  // Comment selection
  const toggleCommentSelection = (id) => {
    setSelectedCommentIds(prev => { const next = new Set(prev); next.has(id) ? next.delete(id) : next.add(id); return next; });
  };
  const toggleAllComments = () => {
    if (!comments?.comments) return;
    if (selectedCommentIds.size === comments.comments.length) setSelectedCommentIds(new Set());
    else setSelectedCommentIds(new Set(comments.comments.map(c => c.id)));
  };

  // AI processing
  const handleProcessIssues = async () => {
    if (selectedIssueKeys.size === 0 || !selectedResource) return;
    setAiProcessing(true); setAiError(null); setResultsLoading(true);
    try {
      const response = await processIssuesWithAI(selectedResource.id, [...selectedIssueKeys]);
      setAiResponse(response); storeResults(response, 'issues'); setAiModalOpen(true);
    } catch (err) { setAiError('AI processing failed. Please try again.'); setResultsError('AI processing failed'); console.error(err); }
    finally { setAiProcessing(false); setResultsLoading(false); }
  };

  const handleProcessComments = async () => {
    if (selectedCommentIds.size === 0 || !selectedResource || !selectedIssue) return;
    setAiProcessing(true); setAiError(null); setResultsLoading(true);
    try {
      const response = await processCommentsWithAI(selectedResource.id, selectedIssue.key, [...selectedCommentIds]);
      setAiResponse(response); storeResults(response, 'comments'); setAiModalOpen(true);
    } catch (err) { setAiError('AI processing failed. Please try again.'); setResultsError('AI processing failed'); console.error(err); }
    finally { setAiProcessing(false); setResultsLoading(false); }
  };

  const connectionStatus = isAtlassianConnected ? 'connected' : isAuthenticated ? 'pending' : 'disconnected';

  if (!isAuthenticated) {
    return (
      <ConsoleLayout icon={JiraIcon} iconBg="#eff6ff" title="Atlassian Jira" subtitle="Project management & issue tracking" status="disconnected">
        <div className="card-static text-center py-16">
          <div className="w-20 h-20 rounded-3xl mx-auto flex items-center justify-center mb-4" style={{ background: '#eff6ff' }}><JiraIcon size={40} /></div>
          <h3 className="text-lg font-semibold mb-2">Connect with Atlassian</h3>
          <p className="text-sm mb-6 max-w-md mx-auto" style={{ color: 'var(--text-muted)' }}>Sign in with your Atlassian account to access Jira projects, issues, and comments</p>
          <button onClick={loginWithAtlassian} className="btn-dark inline-flex items-center gap-2"><LogIn size={16} /> Login with Atlassian</button>
        </div>
      </ConsoleLayout>
    );
  }

  return (
    <ConsoleLayout icon={JiraIcon} iconBg="#eff6ff" title="Atlassian Jira" subtitle="Project management & issue tracking" status={connectionStatus} userName={atlassianUser?.name} userAvatar={atlassianUser?.avatarUrl}>
      <div className="space-y-5">
        {/* Resource selector */}
        {loadingResources ? <ListSkeleton count={2} /> : resourceError ? (
          <div className="card-static text-center py-8">
            <AlertCircle size={24} className="mx-auto mb-2 text-red-400" />
            <p className="text-sm text-red-500 mb-3">{resourceError}</p>
            <button onClick={fetchResources} className="btn-ghost text-xs inline-flex items-center gap-1"><RefreshCw size={12} /> Retry</button>
          </div>
        ) : resources.length > 0 && (
          <div className="card-static !p-4">
            <label className="text-xs font-semibold block mb-1.5" style={{ color: 'var(--text-secondary)' }}><Globe size={12} className="inline mr-1" />Atlassian Site</label>
            <div className="relative">
              <select className="input-field !pr-8 appearance-none cursor-pointer" value={selectedResource?.id || ''} onChange={handleResourceChange}>
                {resources.map((r) => <option key={r.id} value={r.id}>{r.name} — {r.url}</option>)}
              </select>
              <ChevronDown size={14} className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none" style={{ color: 'var(--text-muted)' }} />
            </div>
          </div>
        )}

        {/* Breadcrumb */}
        {(selectedProject || selectedIssue) && (
          <motion.div initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }} className="flex items-center gap-1 text-xs" style={{ color: 'var(--text-muted)' }}>
            <button onClick={handleBackToProjects} className="hover:underline font-medium" style={{ color: 'var(--text-secondary)' }}>Projects</button>
            {selectedProject && (<><ChevronRight size={12} /><button onClick={handleBackToIssues} className="hover:underline font-medium" style={{ color: selectedIssue ? 'var(--text-secondary)' : 'var(--text-primary)' }}>{selectedProject.key}</button></>)}
            {selectedIssue && (<><ChevronRight size={12} /><span className="font-semibold" style={{ color: 'var(--text-primary)' }}>{selectedIssue.key}</span></>)}
          </motion.div>
        )}

        {/* AI error banner */}
        {aiError && (
          <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} className="flex items-center gap-2 p-3 rounded-xl" style={{ background: '#fef2f2', border: '1px solid #fecaca' }}>
            <AlertCircle size={14} className="text-red-400 shrink-0" />
            <p className="text-xs text-red-600 flex-1">{aiError}</p>
            <button onClick={() => setAiError(null)} className="text-red-400 hover:text-red-600 text-xs">✕</button>
          </motion.div>
        )}

        {/* Content area */}
        <AnimatePresence mode="wait">
          {selectedIssue ? (
            /* Comments view */
            <motion.div key="comments" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} className="card-static space-y-4">
              <div className="flex items-center gap-2">
                <button onClick={handleBackToIssues} className="btn-ghost !p-1.5"><ArrowLeft size={14} /></button>
                <label className="text-xs font-semibold" style={{ color: 'var(--text-secondary)' }}><MessageSquare size={12} className="inline mr-1" />Comments on {selectedIssue.key}</label>
                {comments?.comments?.length > 0 && (
                  <div className="ml-auto flex items-center gap-2">
                    <button onClick={toggleAllComments} className="btn-ghost text-[10px] flex items-center gap-1">
                      {selectedCommentIds.size === comments.comments.length ? <CheckSquare size={12} /> : <Square size={12} />}
                      {selectedCommentIds.size === comments.comments.length ? 'Deselect All' : 'Select All'}
                    </button>
                    <button
                      onClick={handleProcessComments}
                      disabled={selectedCommentIds.size === 0 || aiProcessing}
                      className="btn-dark text-[10px] !py-1.5 !px-3 flex items-center gap-1.5 disabled:opacity-40 disabled:cursor-not-allowed"
                    >
                      {aiProcessing ? <Loader2 size={12} className="animate-spin" /> : <Sparkles size={12} />}
                      {aiProcessing ? 'Analyzing…' : `Analyze with AI${selectedCommentIds.size > 0 ? ` (${selectedCommentIds.size})` : ''}`}
                    </button>
                  </div>
                )}
              </div>
              {/* Issue summary */}
              <div className="p-4 rounded-xl" style={{ background: 'var(--bg-secondary)' }}>
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded" style={{ background: '#eff6ff', color: '#2684FF' }}>{selectedIssue.key}</span>
                  {selectedIssue.fields?.status?.name && <span className="text-[10px] px-1.5 py-0.5 rounded" style={{ background: '#f0fdf4', color: '#16a34a' }}>{selectedIssue.fields.status.name}</span>}
                </div>
                <p className="text-sm font-semibold mt-1">{selectedIssue.fields?.summary || selectedIssue.key}</p>
                {selectedIssue.fields?.description && <p className="text-xs mt-1.5" style={{ color: 'var(--text-muted)' }}>{extractText(selectedIssue.fields.description).slice(0, 300)}</p>}
              </div>
              {/* Comments list */}
              {loadingComments ? <ListSkeleton count={3} /> : comments?.comments?.length > 0 ? (
                <div className="space-y-2 max-h-[500px] overflow-y-auto">
                  {comments.comments.map((comment, idx) => (
                    <motion.div
                      key={comment.id || idx}
                      initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: idx * 0.03 }}
                      className={`p-4 rounded-xl cursor-pointer transition-all ${selectedCommentIds.has(comment.id) ? 'ring-2 ring-blue-400' : ''}`}
                      style={{ background: 'var(--bg-secondary)' }}
                      onClick={() => toggleCommentSelection(comment.id)}
                    >
                      <div className="flex items-center justify-between mb-1.5">
                        <div className="flex items-center gap-2">
                          {selectedCommentIds.has(comment.id) ? <CheckSquare size={14} className="text-blue-500" /> : <Square size={14} style={{ color: 'var(--text-muted)' }} />}
                          <span className="text-xs font-semibold">{comment.author?.displayName || comment.author || 'Unknown'}</span>
                        </div>
                        <span className="text-[10px]" style={{ color: 'var(--text-muted)' }}>{comment.created ? new Date(comment.created).toLocaleDateString() : ''}</span>
                      </div>
                      <p className="text-xs leading-relaxed ml-6" style={{ color: 'var(--text-secondary)' }}>{extractText(comment.body)}</p>
                    </motion.div>
                  ))}
                </div>
              ) : (
                <EmptyState icon={MessageSquare} title="No comments" description="This issue doesn't have any comments yet" iconBg="#eff6ff" iconColor="#2684FF" />
              )}
            </motion.div>
          ) : selectedProject ? (
            /* Issues view */
            <motion.div key="issues" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} className="card-static space-y-4">
              <div className="flex items-center gap-2 flex-wrap">
                <button onClick={handleBackToProjects} className="btn-ghost !p-1.5"><ArrowLeft size={14} /></button>
                <label className="text-xs font-semibold" style={{ color: 'var(--text-secondary)' }}><FileText size={12} className="inline mr-1" />Issues in {selectedProject.name}</label>
                {issues && <span className="text-[10px]" style={{ color: 'var(--text-muted)' }}>{issues.total} total</span>}
                {issues?.issues?.length > 0 && (
                  <div className="ml-auto flex items-center gap-2">
                    <button onClick={toggleAllIssues} className="btn-ghost text-[10px] flex items-center gap-1">
                      {selectedIssueKeys.size === issues.issues.length ? <CheckSquare size={12} /> : <Square size={12} />}
                      {selectedIssueKeys.size === issues.issues.length ? 'Deselect All' : 'Select All'}
                    </button>
                    <button
                      onClick={handleProcessIssues}
                      disabled={selectedIssueKeys.size === 0 || aiProcessing}
                      className="btn-dark text-[10px] !py-1.5 !px-3 flex items-center gap-1.5 disabled:opacity-40 disabled:cursor-not-allowed"
                    >
                      {aiProcessing ? <Loader2 size={12} className="animate-spin" /> : <Sparkles size={12} />}
                      {aiProcessing ? 'Computing…' : `Compute with AI${selectedIssueKeys.size > 0 ? ` (${selectedIssueKeys.size})` : ''}`}
                    </button>
                  </div>
                )}
              </div>
              {loadingIssues ? <ListSkeleton count={5} /> : issues?.issues?.length > 0 ? (
                <>
                  <div className="space-y-2 max-h-[500px] overflow-y-auto">
                    {issues.issues.map((issue, idx) => (
                      <motion.div
                        key={issue.id}
                        initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: idx * 0.02 }}
                        className={`flex items-center gap-3 p-4 rounded-xl transition-all hover:bg-gray-50 ${selectedIssueKeys.has(issue.key) ? 'ring-2 ring-blue-400' : ''}`}
                        style={{ background: 'var(--bg-secondary)' }}
                      >
                        <button
                          onClick={(e) => { e.stopPropagation(); toggleIssueSelection(issue.key); }}
                          className="shrink-0"
                        >
                          {selectedIssueKeys.has(issue.key) ? <CheckSquare size={16} className="text-blue-500" /> : <Square size={16} style={{ color: 'var(--text-muted)' }} />}
                        </button>
                        <div className="flex-1 min-w-0 cursor-pointer" onClick={() => handleIssueClick(issue)}>
                          <div className="flex items-center gap-2">
                            <span className="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded" style={{ background: '#eff6ff', color: '#2684FF' }}>{issue.key}</span>
                            {issue.fields?.status?.name && <span className="text-[10px] px-1.5 py-0.5 rounded" style={{ background: '#f0fdf4', color: '#16a34a' }}>{issue.fields.status.name}</span>}
                          </div>
                          <p className="text-sm font-medium truncate mt-1">{issue.fields?.summary || issue.key}</p>
                          {issue.fields?.assignee && <p className="text-[10px] mt-0.5" style={{ color: 'var(--text-muted)' }}>Assignee: {issue.fields.assignee.displayName || issue.fields.assignee}</p>}
                        </div>
                        <ChevronRight size={14} style={{ color: 'var(--text-muted)' }} className="cursor-pointer" onClick={() => handleIssueClick(issue)} />
                      </motion.div>
                    ))}
                  </div>
                  {issues.total > 50 && (
                    <div className="flex items-center justify-between pt-2">
                      <button onClick={() => fetchIssues(selectedProject.key, Math.max(0, issuesPage - 50))} disabled={issuesPage === 0} className="btn-ghost text-xs disabled:opacity-30">← Previous</button>
                      <span className="text-[10px]" style={{ color: 'var(--text-muted)' }}>{issuesPage + 1}–{Math.min(issuesPage + 50, issues.total)} of {issues.total}</span>
                      <button onClick={() => fetchIssues(selectedProject.key, issuesPage + 50)} disabled={issuesPage + 50 >= issues.total} className="btn-ghost text-xs disabled:opacity-30">Next →</button>
                    </div>
                  )}
                </>
              ) : (
                <EmptyState icon={FileText} title="No issues found" description={`No issues found in ${selectedProject.name}`} iconBg="#eff6ff" iconColor="#2684FF" />
              )}
            </motion.div>
          ) : (
            /* Projects list */
            <motion.div key="projects" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -12 }} className="card-static space-y-4">
              <div className="flex items-center justify-between">
                <label className="text-xs font-semibold" style={{ color: 'var(--text-secondary)' }}><FolderOpen size={12} className="inline mr-1" />Projects</label>
                <button onClick={fetchResources} className="btn-ghost text-[10px] flex items-center gap-1"><RefreshCw size={12} /> Refresh</button>
              </div>
              {loadingProjects ? <ListSkeleton count={4} /> : projects.length > 0 ? (
                <div className="space-y-2">
                  {projects.map((proj, idx) => (
                    <motion.div key={proj.id} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: idx * 0.03 }}
                      onClick={() => handleProjectClick(proj)} className="flex items-center gap-3 p-4 rounded-xl transition-colors hover:bg-gray-50 cursor-pointer" style={{ background: 'var(--bg-secondary)' }}>
                      {proj.avatarUrls && <img src={proj.avatarUrls['48x48'] || proj.avatarUrls['32x32'] || Object.values(proj.avatarUrls)[0]} alt={proj.name} className="w-10 h-10 rounded-xl" />}
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-semibold truncate">{proj.name}</p>
                        <div className="flex items-center gap-2 mt-0.5">
                          <span className="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded" style={{ background: '#eff6ff', color: '#2684FF' }}>{proj.key}</span>
                          <span className="text-[10px]" style={{ color: 'var(--text-muted)' }}>{proj.projectTypeKey}</span>
                          {proj.isPrivate && <Lock size={10} style={{ color: 'var(--text-muted)' }} />}
                        </div>
                      </div>
                      <ChevronRight size={14} style={{ color: 'var(--text-muted)' }} />
                    </motion.div>
                  ))}
                </div>
              ) : (
                <EmptyState icon={FolderOpen} title="No projects found" description="No Jira projects were found for this site" iconBg="#eff6ff" iconColor="#2684FF" actionLabel="Refresh" onAction={fetchResources} />
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* AI Response Modal */}
      <AIResponseModal isOpen={aiModalOpen} onClose={() => setAiModalOpen(false)} response={aiResponse} title="AI Analysis Complete" />
    </ConsoleLayout>
  );
}
