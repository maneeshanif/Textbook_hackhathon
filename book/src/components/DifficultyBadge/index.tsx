import React from 'react';
import Translate from '@docusaurus/Translate';
import styles from './styles.module.css';

export type DifficultyLevel = 'beginner' | 'intermediate' | 'advanced';

export interface DifficultyBadgeProps {
  level: DifficultyLevel;
  className?: string;
  display?: 'inline' | 'block';
}

const difficultyEmojis: Record<DifficultyLevel, string> = {
  beginner: '🟢',
  intermediate: '🟡',
  advanced: '🔴',
};

export default function DifficultyBadge({
  level,
  className = '',
  display = 'inline',
}: DifficultyBadgeProps): JSX.Element {
  const displayClass = display === 'block' ? styles.block : styles.inline;
  
  return (
    <span 
      className={`${styles.badge} ${styles[level]} ${displayClass} ${className}`}
      role="status"
      aria-label={`Difficulty: ${level}`}
    >
      <span className={styles.emoji} aria-hidden="true">
        {difficultyEmojis[level]}
      </span>
      <Translate
        id={`difficulty.${level}`}
        description={`Difficulty level: ${level}`}
      >
        {level.charAt(0).toUpperCase() + level.slice(1)}
      </Translate>
    </span>
  );
}
