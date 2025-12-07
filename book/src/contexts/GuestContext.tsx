import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

export const GUEST_INTERACTION_LIMIT = 10;
const STORAGE_KEY = 'guest_interaction_count';

interface GuestContextType {
  interactionCount: number;
  isLimitReached: boolean;
  incrementCount: () => void;
  resetCount: () => void;
}

const GuestContext = createContext<GuestContextType | undefined>(undefined);

export function GuestProvider({ children }: { children: ReactNode }) {
  const [interactionCount, setInteractionCount] = useState<number>(() => {
    // Load count from sessionStorage on mount
    try {
      const stored = sessionStorage.getItem(STORAGE_KEY);
      return stored ? parseInt(stored, 10) : 0;
    } catch {
      return 0;
    }
  });

  const isLimitReached = interactionCount >= GUEST_INTERACTION_LIMIT;

  // Persist count to sessionStorage whenever it changes
  useEffect(() => {
    try {
      sessionStorage.setItem(STORAGE_KEY, interactionCount.toString());
    } catch (error) {
      console.error('Failed to save guest count:', error);
    }
  }, [interactionCount]);

  // Listen for storage events from other tabs
  useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === STORAGE_KEY && e.newValue) {
        setInteractionCount(parseInt(e.newValue, 10));
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  const incrementCount = () => {
    setInteractionCount((prev) => Math.min(prev + 1, GUEST_INTERACTION_LIMIT));
  };

  const resetCount = () => {
    setInteractionCount(0);
    try {
      sessionStorage.removeItem(STORAGE_KEY);
    } catch (error) {
      console.error('Failed to clear guest count:', error);
    }
  };

  return (
    <GuestContext.Provider
      value={{
        interactionCount,
        isLimitReached,
        incrementCount,
        resetCount,
      }}
    >
      {children}
    </GuestContext.Provider>
  );
}

export function useGuest(): GuestContextType {
  const context = useContext(GuestContext);
  if (!context) {
    throw new Error('useGuest must be used within a GuestProvider');
  }
  return context;
}
