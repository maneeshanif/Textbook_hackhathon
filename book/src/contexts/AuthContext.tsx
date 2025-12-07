import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface User {
  id: string;
  email: string;
  name: string | null;
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
  preferences: UserPreferences | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, name?: string) => Promise<void>;
  logout: () => Promise<void>;
  updatePreferences: (prefs: UserPreferences) => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const API_BASE_URL = 'http://localhost:8000';

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [preferences, setPreferences] = useState<UserPreferences | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const getStoredToken = () => localStorage.getItem('auth_token');
  const setStoredToken = (token: string) => localStorage.setItem('auth_token', token);
  const removeStoredToken = () => localStorage.removeItem('auth_token');

  const fetchUser = async () => {
    const token = getStoredToken();
    if (!token) {
      setIsLoading(false);
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
        await fetchPreferences(token);
      } else {
        removeStoredToken();
        setUser(null);
      }
    } catch (error) {
      console.error('Failed to fetch user:', error);
      removeStoredToken();
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchPreferences = async (token: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/preferences`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const prefs = await response.json();
        setPreferences({
          difficulty: prefs.difficulty,
          focusTags: prefs.focus_tags,
          preferredLanguage: prefs.preferred_language,
          lastChapters: prefs.last_chapters,
        });
      }
    } catch (error) {
      console.error('Failed to fetch preferences:', error);
    }
  };

  useEffect(() => {
    fetchUser();
  }, []);

  const login = async (email: string, password: string) => {
    const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }

    const data = await response.json();
    setStoredToken(data.session_token);
    setUser(data.user);
    await fetchPreferences(data.session_token);
  };

  const signup = async (email: string, password: string, name?: string) => {
    const response = await fetch(`${API_BASE_URL}/api/auth/signup`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password, name }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Signup failed');
    }

    const data = await response.json();
    setStoredToken(data.session_token);
    setUser(data.user);
    await fetchPreferences(data.session_token);
  };

  const logout = async () => {
    const token = getStoredToken();
    if (token) {
      try {
        await fetch(`${API_BASE_URL}/api/auth/logout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });
      } catch (error) {
        console.error('Logout request failed:', error);
      }
    }

    removeStoredToken();
    setUser(null);
    setPreferences(null);
  };

  const updatePreferences = async (prefs: UserPreferences) => {
    const token = getStoredToken();
    if (!token) throw new Error('Not authenticated');

    const response = await fetch(`${API_BASE_URL}/api/auth/preferences`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({
        difficulty: prefs.difficulty,
        focus_tags: prefs.focusTags,
        preferred_language: prefs.preferredLanguage,
        last_chapters: prefs.lastChapters,
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to update preferences');
    }

    const updated = await response.json();
    setPreferences({
      difficulty: updated.difficulty,
      focusTags: updated.focus_tags,
      preferredLanguage: updated.preferred_language,
      lastChapters: updated.last_chapters,
    });
  };

  const refreshUser = async () => {
    await fetchUser();
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        preferences,
        isAuthenticated: !!user,
        isLoading,
        login,
        signup,
        logout,
        updatePreferences,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
