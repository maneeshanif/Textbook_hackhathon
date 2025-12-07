import React, { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react';
import axios from 'axios';

interface User {
  id: string;
  email: string;
  fullName: string | null;
  role: string;
  emailVerified: boolean;
  createdAt: string;
}

interface UserPreferences {
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  focusTags: string[];
  preferredLanguage: 'en' | 'ur';
  lastChapters: string[];
}

interface AuthContextType {
  user: User | null;
  accessToken: string | null;
  preferences: UserPreferences | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (email: string, password: string, rememberMe?: boolean) => Promise<void>;
  signup: (email: string, password: string, fullName?: string) => Promise<void>;
  logout: () => Promise<void>;
  updatePreferences: (prefs: UserPreferences) => Promise<void>;
  refreshToken: () => Promise<void>;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Use window.location for API URL detection (works in browser)
const getApiBaseUrl = () => {
  if (typeof window === 'undefined') return 'http://localhost:8000';
  // In production, API is usually on same domain or can be configured via window
  return (window as any).__API_URL__ || 'http://localhost:8000';
};

const API_BASE_URL = getApiBaseUrl();

// Create axios instance with credentials
const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true, // Important for httpOnly cookies
});

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [preferences, setPreferences] = useState<UserPreferences | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const isAuthenticated = !!user && !!accessToken;

  // Decode JWT to get expiry time
  const getTokenExpiry = (token: string): number | null => {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return payload.exp * 1000; // Convert to milliseconds
    } catch {
      return null;
    }
  };

  // Refresh token function
  const refreshToken = useCallback(async () => {
    try {
      const response = await api.post('/api/auth/refresh');
      const { accessToken: newToken } = response.data;
      
      setAccessToken(newToken);

      // Fetch user data if we don't have it
      if (!user) {
        const userResponse = await api.get('/api/auth/me', {
          headers: { Authorization: `Bearer ${newToken}` },
        });
        setUser(userResponse.data);
      }

      setIsLoading(false);
      return newToken;
    } catch (err) {
      setAccessToken(null);
      setUser(null);
      setIsLoading(false);
      throw err;
    }
  }, [user]);

  // Auto-refresh token before expiry
  useEffect(() => {
    if (!accessToken) return;

    const expiry = getTokenExpiry(accessToken);
    if (!expiry) return;

    // Refresh 60 seconds before expiry
    const refreshTime = expiry - Date.now() - 60000;
    
    if (refreshTime <= 0) {
      refreshToken();
      return;
    }

    const timer = setTimeout(() => {
      refreshToken();
    }, refreshTime);

    return () => clearTimeout(timer);
  }, [accessToken, refreshToken]);

  // Initialize: Try to refresh token on mount
  useEffect(() => {
    const initAuth = async () => {
      try {
        await refreshToken();
      } catch {
        // No valid session
        setIsLoading(false);
      }
    };

    initAuth();
  }, []);

  // Fetch user preferences
  const fetchPreferences = async (token: string) => {
    try {
      const response = await api.get('/api/auth/preferences', {
        headers: { Authorization: `Bearer ${token}` },
      });

      const prefs = response.data;
      setPreferences({
        difficulty: prefs.difficulty,
        focusTags: prefs.focus_tags || [],
        preferredLanguage: prefs.preferred_language || 'en',
        lastChapters: prefs.last_chapters || [],
      });
    } catch (error) {
      console.error('Failed to fetch preferences:', error);
    }
  };

  const login = async (email: string, password: string, rememberMe = false) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await api.post('/api/auth/login', {
        email,
        password,
        rememberMe,
      });

      const { user: userData, accessToken: token } = response.data;
      setUser(userData);
      setAccessToken(token);
      setError(null);

      // Fetch preferences in background
      fetchPreferences(token);
    } catch (err: any) {
      const message = err.response?.data?.detail || 'Login failed. Please try again.';
      setError(message);
      throw new Error(message);
    } finally {
      setIsLoading(false);
    }
  };

  const signup = async (email: string, password: string, fullName?: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await api.post('/api/auth/signup', {
        email,
        password,
        fullName,
      });

      const { user: userData, accessToken: token } = response.data;
      setUser(userData);
      setAccessToken(token);
      setError(null);

      // Initialize default preferences
      setPreferences({
        difficulty: 'beginner',
        focusTags: [],
        preferredLanguage: 'en',
        lastChapters: [],
      });
    } catch (err: any) {
      const message = err.response?.data?.detail || 'Registration failed. Please try again.';
      setError(message);
      throw new Error(message);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    setIsLoading(true);
    setError(null);

    try {
      await api.post('/api/auth/logout', {}, {
        headers: accessToken ? { Authorization: `Bearer ${accessToken}` } : {},
      });
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      setUser(null);
      setAccessToken(null);
      setPreferences(null);
      setIsLoading(false);
    }
  };

  const updatePreferences = async (prefs: UserPreferences) => {
    if (!accessToken) {
      throw new Error('Not authenticated');
    }

    try {
      await api.put(
        '/api/auth/preferences',
        {
          difficulty: prefs.difficulty,
          focus_tags: prefs.focusTags,
          preferred_language: prefs.preferredLanguage,
          last_chapters: prefs.lastChapters,
        },
        {
          headers: { Authorization: `Bearer ${accessToken}` },
        }
      );

      setPreferences(prefs);
    } catch (error) {
      console.error('Failed to update preferences:', error);
      throw error;
    }
  };

  const clearError = () => setError(null);

  return (
    <AuthContext.Provider
      value={{
        user,
        accessToken,
        preferences,
        isAuthenticated,
        isLoading,
        error,
        login,
        signup,
        logout,
        updatePreferences,
        refreshToken,
        clearError,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
