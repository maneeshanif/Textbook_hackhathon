/**
 * ChapterHeader Component Contract
 * 
 * Displays chapter metadata at the top of each chapter page.
 * Shows chapter number, title, difficulty, and estimated reading time.
 * 
 * @accessibility
 * - Uses semantic heading elements
 * - Time estimate is human-readable
 * - Difficulty badge follows DifficultyBadge accessibility
 */

import type { DifficultyLevel } from './DifficultyBadge';

export interface ChapterHeaderProps {
  /**
   * Chapter number in X format (e.g., "1", "2").
   */
  number: string | number;

  /**
   * Chapter or section number in X.Y format (e.g., "1.1", "2.3").
   */
  sectionNumber?: string;

  /**
   * Title of the chapter/section.
   */
  title: string;

  /**
   * Difficulty level of the content.
   */
  difficulty: DifficultyLevel;

  /**
   * Estimated reading/completion time.
   * Format: "XX minutes" or "X hours"
   */
  estimatedTime: string;

  /**
   * Optional description/subtitle.
   */
  description?: string;

  /**
   * Tags for the chapter (displayed as chips).
   */
  tags?: string[];

  /**
   * Whether to show the table of contents link.
   * @default true
   */
  showTocLink?: boolean;

  /**
   * Optional CSS class for custom styling.
   */
  className?: string;
}

/**
 * Frontmatter type that maps to ChapterHeader props.
 * This is what's defined in MDX files.
 */
export interface ChapterFrontmatter {
  title: string;
  sidebar_position: number;
  tags?: string[];
  difficulty: DifficultyLevel;
  estimated_time: string;
  description?: string;
}

/**
 * Helper to extract chapter number from frontmatter title.
 * e.g., "1.2 What is Physical AI?" -> { chapter: "1", section: "2" }
 */
export interface ParsedChapterNumber {
  chapter: string;
  section?: string;
  fullNumber: string; // "1.2"
}

/**
 * Usage Example:
 * 
 * ```mdx
 * <!-- Auto-populated from frontmatter -->
 * <ChapterHeader 
 *   number="1"
 *   sectionNumber="1.2"
 *   title="What is Physical AI?"
 *   difficulty="beginner"
 *   estimatedTime="15 minutes"
 *   tags={['physical-ai', 'introduction']}
 * />
 * 
 * <!-- Or use the wrapper that reads frontmatter automatically -->
 * <AutoChapterHeader />
 * ```
 */
