// ============================================================
// Nexus API Service — aligned with Spring Boot backend
// Backend: https://localhost:8443 (Spring Boot 4 + OAuth2)
// Auth: Session-based OAuth2 — all requests use credentials: 'include'
// Dev: Vite proxy forwards API paths to backend automatically
// ============================================================

// In dev mode, Vite proxy handles routing to https://localhost:8443
// In production, set this to your deployed backend URL
const API_BASE = '';

/**
 * Core request helper.
 * Always sends credentials (cookies) for session-based OAuth2 auth.
 * Returns { data, error } pattern for consistent handling.
 */
async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const config = {
    credentials: 'include', // required for session-based OAuth2
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  };

  try {
    const response = await fetch(url, config);

    // If unauthorized, return null so callers can handle gracefully
    if (response.status === 401 || response.status === 403) {
      return null;
    }

    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } catch (error) {
    // Don't log auth-check failures as errors — they're expected when not logged in
    if (!endpoint.includes('/logged/')) {
      console.error(`API Error [${endpoint}]:`, error);
    }
    throw error;
  }
}

// ============================================================
// AUTH — OAuth2 Login URLs
// ============================================================

/** Returns the URL to redirect to for Atlassian OAuth login */
export const getAtlassianLoginUrl = () => `${API_BASE}/oauth2/authorization/atlassian`;

/** Alias for backward compatibility */
export const getLoginUrl = getAtlassianLoginUrl;

/** Returns the URL to redirect to for Slack OAuth login */
export const getSlackLoginUrl = () => `${API_BASE}/oauth2/authorization/slack`;

/** Fetch the currently logged-in user (session-based, from /logged/user) */
export const getLoggedUser = () => request('/user/logged');

/** Logout — Spring Security default logout endpoint */
export const logout = () =>
  request('/logout', { method: 'POST', headers: {} });

// ============================================================
// USER DATA — /user endpoints
// ============================================================

/** Fetch the logged-in user's Atlassian profile */
export const getAtlassianUserData = () => request('/user/atlassian');

/** Fetch the logged-in user's Slack profile */
export const getSlackUserData = () => request('/user/slack');

// ============================================================
// ATLASSIAN / JIRA — /atlassian endpoints
// ============================================================

/** Fetch accessible Atlassian resources (sites) for the logged-in user */
export const getAtlassianResources = () => request('/atlassian/resources');

/**
 * Fetch Jira projects for a given Atlassian cloud site
 * @param {string} cloudId - The Atlassian cloud ID
 */
export const getAtlassianProjects = (cloudId) =>
  request(`/atlassian/projects?cloudId=${encodeURIComponent(cloudId)}`);

/**
 * Fetch Jira issues from a specific project with pagination
 * @param {string} cloudId - The Atlassian cloud ID
 * @param {string} projectKey - The Jira project key (e.g., "PROJ")
 * @param {number} [startAt=0] - Starting index for pagination
 * @param {number} [maxResult=50] - Maximum number of results
 */
export const getAtlassianIssues = (cloudId, projectKey, startAt = 0, maxResult = 50) =>
  request(
    `/atlassian/issues?cloudId=${encodeURIComponent(cloudId)}&projectKey=${encodeURIComponent(projectKey)}&startAt=${startAt}&maxResult=${maxResult}`
  );

/**
 * Fetch comments for a specific Jira issue with pagination
 * @param {string} cloudId - The Atlassian cloud ID
 * @param {string} issueKey - The Jira issue key (e.g., "PROJ-123")
 * @param {number} [startAt=0] - Starting index for pagination
 * @param {number} [maxResult=50] - Maximum number of results
 */
export const getAtlassianComments = (cloudId, issueKey, startAt = 0, maxResult = 50) =>
  request(
    `/atlassian/comments?cloudId=${encodeURIComponent(cloudId)}&issueKey=${encodeURIComponent(issueKey)}&startAt=${startAt}&maxResult=${maxResult}`
  );

/**
 * Submit selected comment IDs (POST /atlassian/selected-commemts)
 * @param {object} selectedCommentsIds - Object with the selected comment IDs
 */
export const postSelectedComments = (selectedCommentsIds) =>
  request('/atlassian/selected-commemts', {
    method: 'POST',
    body: JSON.stringify(selectedCommentsIds),
  });

// ============================================================
// SLACK — /slack endpoints
// ============================================================

/** Fetch all Slack channels accessible to the authenticated user */
export const getSlackChannels = () => request('/slack/channels');

/**
 * Fetch messages from a specific Slack channel
 * @param {string} channelId - The Slack channel ID
 */
export const getSlackMessages = (channelId) =>
  request(`/slack/channels/${encodeURIComponent(channelId)}/messages`);

// ============================================================
// TEST — Backend connectivity check
// ============================================================

/** Test if the backend is reachable (no auth required) */
export const testBackendConnection = () =>
  request('/tests/1', { method: 'POST' });

// ============================================================
// AI PROCESSING — /ai endpoints (NLP pipeline)
// ============================================================

/**
 * Send selected Jira issues to AI/NLP for requirements analysis
 * @param {string} cloudID - The Atlassian cloud ID
 * @param {string[]} issueKeys - Array of Jira issue keys (e.g., ["PROJ-1", "PROJ-2"])
 */
export const processIssuesWithAI = (cloudID, issueKeys) =>
  request('/ai/issue-process', {
    method: 'POST',
    body: JSON.stringify({ cloudID, issueKeys }),
  });

/**
 * Send selected Jira comments to AI/NLP for requirements analysis
 * @param {string} cloudID - The Atlassian cloud ID
 * @param {string} issueKey - The Jira issue key (e.g., "PROJ-123")
 * @param {string[]} commentIds - Array of comment IDs
 */
export const processCommentsWithAI = (cloudID, issueKey, commentIds) =>
  request('/ai/comment-process', {
    method: 'POST',
    body: JSON.stringify({ cloudID, issueKey, commentIds }),
  });

// ============================================================
// UTILITY — API base getter for Settings page
// ============================================================

export const getApiBase = () => API_BASE || 'https://localhost:8443 (via Vite proxy)';
