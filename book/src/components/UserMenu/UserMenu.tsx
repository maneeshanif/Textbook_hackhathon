import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import styles from './UserMenu.module.css';

export default function UserMenu() {
  const { user, preferences, isAuthenticated, logout } = useAuth();
  const [isOpen, setIsOpen] = useState(false);

  if (!isAuthenticated || !user) return null;

  const handleLogout = async () => {
    await logout();
    setIsOpen(false);
  };

  return (
    <div className={styles.container}>
      <button
        className={styles.avatar}
        onClick={() => setIsOpen(!isOpen)}
        aria-label="User menu"
      >
        {user.name ? user.name[0].toUpperCase() : user.email[0].toUpperCase()}
      </button>

      {isOpen && (
        <>
          <div className={styles.backdrop} onClick={() => setIsOpen(false)} />
          <div className={styles.dropdown}>
            <div className={styles.header}>
              <div className={styles.name}>{user.name || 'User'}</div>
              <div className={styles.email}>{user.email}</div>
            </div>

            {preferences && (
              <div className={styles.preferences}>
                <div className={styles.prefItem}>
                  <span className={styles.prefLabel}>📚 Level:</span>
                  <span className={styles.prefValue}>
                    {preferences.difficulty === 'beginner' && '🟢 Beginner'}
                    {preferences.difficulty === 'intermediate' && '🟡 Intermediate'}
                    {preferences.difficulty === 'advanced' && '🔴 Advanced'}
                  </span>
                </div>
                <div className={styles.prefItem}>
                  <span className={styles.prefLabel}>🌐 Language:</span>
                  <span className={styles.prefValue}>
                    {preferences.preferredLanguage === 'en' ? '🇬🇧 English' : '🇵🇰 اردو'}
                  </span>
                </div>
              </div>
            )}

            <div className={styles.divider} />

            <button className={styles.menuItem} onClick={handleLogout}>
              🚪 Logout
            </button>
          </div>
        </>
      )}
    </div>
  );
}
