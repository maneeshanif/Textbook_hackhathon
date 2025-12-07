import React, { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useGuest, GUEST_INTERACTION_LIMIT } from '@/contexts/GuestContext';
import { SignUpForm } from './SignUpForm';
import { LoginForm } from './LoginForm';
import styles from './AuthDialog.module.css';

interface AuthDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  defaultTab?: 'login' | 'signup';
}

export function AuthDialog({ open, onOpenChange, defaultTab = 'signup' }: AuthDialogProps) {
  const { error, clearError } = useAuth();
  const { isLimitReached, interactionCount } = useGuest();
  const [activeTab, setActiveTab] = useState<string>(defaultTab);

  // Prevent body scroll when dialog is open
  useEffect(() => {
    if (open) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [open]);

  const handleOpenChange = (newOpen: boolean) => {
    if (!newOpen) {
      clearError();
    }
    onOpenChange(newOpen);
  };

  const handleSuccess = () => {
    onOpenChange(false);
  };

  const handleOverlayClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      handleOpenChange(false);
    }
  };

  if (!open) return null;

  return (
    <>
      {/* Overlay */}
      <div
        className={styles.dialogOverlay}
        onClick={handleOverlayClick}
        role="presentation"
      />

      {/* Dialog Content */}
      <div className={styles.dialogContent} role="dialog" aria-modal="true">
        {/* Close Button */}
        <button
          className={styles.closeButton}
          onClick={() => handleOpenChange(false)}
          aria-label="Close"
        >
          <svg
            width="16"
            height="16"
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

        {/* Header */}
        <div className={styles.dialogHeader}>
          <h2 className={styles.dialogTitle}>
            {isLimitReached ? 'Unlock Unlimited Questions' : 'Welcome to Physical AI Textbook'}
          </h2>
          <p className={styles.dialogDescription}>
            {isLimitReached ? (
              <>
                You've explored {interactionCount} questions as a guest. Create an account to continue your AI learning journey!
              </>
            ) : (
              'Sign up or log in to save your progress and access personalized features.'
            )}
          </p>
        </div>

        {/* Tabs */}
        <div className={styles.tabsList}>
          <button
            className={styles.tabTrigger}
            data-state={activeTab === 'signup' ? 'active' : 'inactive'}
            onClick={() => setActiveTab('signup')}
          >
            Sign Up
          </button>
          <button
            className={styles.tabTrigger}
            data-state={activeTab === 'login' ? 'active' : 'inactive'}
            onClick={() => setActiveTab('login')}
          >
            Log In
          </button>
        </div>

        {/* Tab Content */}
        <div className={styles.tabContent}>
          {activeTab === 'signup' && (
            <SignUpForm onSuccess={handleSuccess} onSwitchToLogin={() => setActiveTab('login')} />
          )}
          {activeTab === 'login' && (
            <LoginForm onSuccess={handleSuccess} onSwitchToSignup={() => setActiveTab('signup')} />
          )}
        </div>

        {/* Error Message */}
        {error && (
          <div className={styles.errorMessage}>
            {error}
          </div>
        )}
      </div>
    </>
  );
}
