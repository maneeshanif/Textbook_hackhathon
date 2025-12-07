import React, { useState } from 'react';
import { useAuth } from '@site/src/contexts/AuthContext';
import AuthModal from '@site/src/components/AuthModal';
import UserMenu from '@site/src/components/UserMenu';

export default function NavbarContent(): JSX.Element {
  const { isAuthenticated, isLoading } = useAuth();
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authMode, setAuthMode] = useState<'login' | 'signup'>('login');

  if (isLoading) {
    return (
      <div style={{ padding: '0 1rem' }}>
        <span style={{ opacity: 0.6 }}>⏳</span>
      </div>
    );
  }

  return (
    <>
      {isAuthenticated ? (
        <UserMenu />
      ) : (
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <button
            onClick={() => {
              setAuthMode('login');
              setShowAuthModal(true);
            }}
            style={{
              padding: '0.5rem 1rem',
              background: 'transparent',
              border: `2px solid var(--ifm-color-primary)`,
              borderRadius: '8px',
              color: 'var(--ifm-color-primary)',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'all 0.2s',
            }}
            onMouseOver={(e) => {
              e.currentTarget.style.background = 'var(--ifm-color-primary)';
              e.currentTarget.style.color = 'white';
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.background = 'transparent';
              e.currentTarget.style.color = 'var(--ifm-color-primary)';
            }}
          >
            🔐 Login
          </button>
          <button
            onClick={() => {
              setAuthMode('signup');
              setShowAuthModal(true);
            }}
            style={{
              padding: '0.5rem 1rem',
              background: 'var(--ifm-color-primary)',
              border: 'none',
              borderRadius: '8px',
              color: 'white',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'all 0.2s',
            }}
            onMouseOver={(e) => {
              e.currentTarget.style.background = 'var(--ifm-color-primary-dark)';
              e.currentTarget.style.transform = 'translateY(-1px)';
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.background = 'var(--ifm-color-primary)';
              e.currentTarget.style.transform = 'translateY(0)';
            }}
          >
            ✨ Sign Up
          </button>
        </div>
      )}

      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        initialMode={authMode}
      />
    </>
  );
}
