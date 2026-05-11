import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import {
  getLoggedUser,
  getAtlassianLoginUrl,
  getSlackLoginUrl,
  logout as apiLogout,
  getAtlassianUserData,
  getSlackUserData,
} from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [atlassianUser, setAtlassianUser] = useState(null);
  const [slackUser, setSlackUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check if user is already logged in (session-based)
  const checkAuth = useCallback(async () => {
    setIsLoading(true);
    try {
      const userData = await getLoggedUser();
      setUser(userData); // null if 401, object if authenticated

      // If logged in, also fetch platform-specific user data
      if (userData) {
        const [atlassian, slack] = await Promise.all([
          getAtlassianUserData().catch(() => null),
          getSlackUserData().catch(() => null),
        ]);
        setAtlassianUser(atlassian);
        setSlackUser(slack);
      }
    } catch {
      setUser(null);
      setAtlassianUser(null);
      setSlackUser(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  // Redirect to Atlassian OAuth login
  const loginWithAtlassian = useCallback(() => {
    window.location.href = getAtlassianLoginUrl();
  }, []);

  // Redirect to Slack OAuth login
  const loginWithSlack = useCallback(() => {
    window.location.href = getSlackLoginUrl();
  }, []);

  // Backward-compatible alias — defaults to Atlassian
  const login = loginWithAtlassian;

  // Logout
  const logout = useCallback(async () => {
    try {
      await apiLogout();
    } catch {
      // ignore logout errors
    }
    setUser(null);
    setAtlassianUser(null);
    setSlackUser(null);
  }, []);

  const value = {
    user,
    atlassianUser,
    slackUser,
    isAuthenticated: !!user,
    isAtlassianConnected: !!atlassianUser,
    isSlackConnected: !!slackUser,
    isLoading,
    login,
    loginWithAtlassian,
    loginWithSlack,
    logout,
    refreshAuth: checkAuth,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export default AuthContext;
