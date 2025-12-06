import React from 'react';
import DifficultyBadge, { DifficultyLevel } from '../DifficultyBadge';
import styles from './styles.module.css';

export interface ChapterHeaderProps {
  number: string | number;
  sectionNumber?: string;
  title: string;
  difficulty: DifficultyLevel;
  estimatedTime: string;
  description?: string;
  tags?: string[];
  showTocLink?: boolean;
  className?: string;
}

export default function ChapterHeader({
  number,
  sectionNumber,
  title,
  difficulty,
  estimatedTime,
  description,
  tags = [],
  showTocLink = true,
  className = '',
}: ChapterHeaderProps): JSX.Element {
  const displayNumber = sectionNumber || number;
  
  return (
    <header className={`${styles.chapterHeader} ${className}`}>
      <div className={styles.metadata}>
        <span className={styles.chapterNumber} aria-label={`Chapter ${displayNumber}`}>
          {displayNumber}
        </span>
        <DifficultyBadge level={difficulty} />
        <span className={styles.time} aria-label={`Estimated time: ${estimatedTime}`}>
          <span aria-hidden="true">⏱</span> {estimatedTime}
        </span>
      </div>
      
      <h1 className={styles.title}>{title}</h1>
      
      {description && (
        <p className={styles.description}>{description}</p>
      )}
      
      {tags.length > 0 && (
        <div className={styles.tags} role="list" aria-label="Chapter tags">
          {tags.map((tag) => (
            <span key={tag} className={styles.tag} role="listitem">
              {tag}
            </span>
          ))}
        </div>
      )}
      
      {showTocLink && (
        <nav className={styles.tocLink} aria-label="Table of contents navigation">
          <a href="#" className={styles.link}>
            📋 Table of Contents
          </a>
        </nav>
      )}
    </header>
  );
}
