/**
 * Main ChatWidget component - floating chat interface
 */

import React, { useState, useCallback, useEffect } from 'react';
import { useStreamingQuery } from './hooks/useStreamingQuery';
import { MessageList } from './components/MessageList';
import { InputBox } from './components/InputBox';
import { 
  getSessionToken, 
  setSessionToken, 
  clearSessionToken,
  getSessionLanguage,
  setSessionLanguage 
} from './utils/session';
import type { ChatMessage } from './types';
import { useAuth } from '@/contexts/AuthContext';
import { useGuest } from '@/contexts/GuestContext';
import { GuestLimitBadge } from './GuestLimitBadge';
import { AuthDialog } from '../Auth/AuthDialog';
import styles from './ChatWidget.module.css';

export function ChatWidget() {
  const [isMounted, setIsMounted] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [sessionToken, setSessionTokenState] = useState<string | null>(null);
  const [language, setLanguageState] = useState<string>('en');
  const [authDialogOpen, setAuthDialogOpen] = useState(false);

  const { user } = useAuth();
  const { incrementCount, isLimitReached } = useGuest();

  const handleMessageComplete = useCallback((message: ChatMessage) => {
    setMessages((prev) => [...prev, message]);
    
    // Increment guest counter after bot response (only for non-authenticated users)
    if (!user) {
      incrementCount();
      
      // Open auth dialog if limit reached
      if (isLimitReached) {
        setAuthDialogOpen(true);
      }
    }
  }, [user, incrementCount, isLimitReached]);

  const { sendQuery, isLoading, error, currentMessage, citations } = useStreamingQuery(
    language,
    handleMessageComplete
  );

  // Only render on client side to avoid SSR issues
  useEffect(() => {
    setIsMounted(true);
    setLanguageState(getSessionLanguage());
  }, []);

  const handleSendMessage = useCallback(
    async (content: string) => {
      // Check guest limit before sending (block if limit reached and not authenticated)
      if (!user && isLimitReached) {
        setAuthDialogOpen(true);
        return;
      }

      // Add user message immediately
      const userMessage: ChatMessage = {
        id: `user-${Date.now()}`,
        role: 'user',
        content,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, userMessage]);

      // Get or create session token
      let token = sessionToken || getSessionToken();
      if (!token) {
        token = `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        setSessionToken(token);
        setSessionTokenState(token);
      }

      // Send query to backend
      await sendQuery(content, token);
    },
    [user, isLimitReached, sessionToken, sendQuery]
  );

  const handleCitationClick = useCallback((url: string) => {
    // Navigate to the chapter section
    if (typeof window !== 'undefined') {
      window.location.href = url;
    }
  }, []);

  const handleClearHistory = useCallback(() => {
    setMessages([]);
    clearSessionToken();
    setSessionTokenState(null);
  }, []);

  const handleLanguageChange = useCallback((newLanguage: string) => {
    setLanguageState(newLanguage);
    setSessionLanguage(newLanguage);
    // Clear session when language changes
    handleClearHistory();
  }, [handleClearHistory]);

  const toggleOpen = () => setIsOpen(!isOpen);

  // Don't render anything during SSR
  if (!isMounted) {
    return null;
  }

  return (
    <>
      {/* Floating button */}
      <button
        className={`${styles.floatingButton} ${isOpen ? styles.hidden : ''}`}
        onClick={toggleOpen}
        aria-label="Open chat"
      >
        <svg
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
        </svg>
      </button>

      {/* Chat panel */}
      {isOpen && (
        <div className={styles.chatPanel}>
          {/* Header */}
          <div className={styles.header}>
            <div className={styles.headerContent}>
              <h3 className={styles.title}>Textbook Assistant</h3>
              <GuestLimitBadge />
              <div className={styles.languageSelector}>
                <button
                  className={`${styles.langButton} ${language === 'en' ? styles.active : ''}`}
                  onClick={() => handleLanguageChange('en')}
                >
                  EN
                </button>
                <button
                  className={`${styles.langButton} ${language === 'ur' ? styles.active : ''}`}
                  onClick={() => handleLanguageChange('ur')}
                >
                  UR
                </button>
              </div>
            </div>
            <div className={styles.headerActions}>
              <button
                className={styles.iconButton}
                onClick={handleClearHistory}
                aria-label="Clear history"
                title="Clear history"
              >
                <svg
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <polyline points="1 4 1 10 7 10" />
                  <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10" />
                </svg>
              </button>
              <button
                className={styles.iconButton}
                onClick={toggleOpen}
                aria-label="Close chat"
              >
                <svg
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <line x1="18" y1="6" x2="6" y2="18" />
                  <line x1="6" y1="6" x2="18" y2="18" />
                </svg>
              </button>
            </div>
          </div>

          {/* Error banner */}
          {error && (
            <div className={styles.errorBanner}>
              <span>⚠️ {error}</span>
            </div>
          )}

          {/* Messages */}
          <MessageList
            messages={messages}
            currentMessage={currentMessage}
            isLoading={isLoading}
            onCitationClick={handleCitationClick}
          />

          {/* Input */}
          <InputBox
            onSend={handleSendMessage}
            disabled={isLoading}
            placeholder={
              language === 'ur' 
                ? 'کتاب کے بارے میں سوال پوچھیں...'
                : 'Ask a question about the textbook...'
            }
          />
        </div>
      )}

      {/* Auth Dialog */}
      <AuthDialog
        open={authDialogOpen}
        onOpenChange={setAuthDialogOpen}
      />
    </>
  );
}
