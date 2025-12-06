/**
 * DifficultyBadge Component Contract
 * 
 * Displays a colored badge indicating content difficulty level.
 * Used in chapter sections to help readers identify appropriate content.
 * 
 * @accessibility
 * - Includes aria-label for screen readers
 * - Color contrast meets WCAG 2.1 AA standards
 * - Text is visible in both light and dark themes
 */

export type DifficultyLevel = 'beginner' | 'intermediate' | 'advanced';

export interface DifficultyBadgeProps {
  /**
   * The difficulty level to display.
   * Controls both the label text and background color.
   */
  level: DifficultyLevel;

  /**
   * Optional CSS class for additional styling.
   */
  className?: string;

  /**
   * Whether to show the badge inline or as a block element.
   * @default 'inline'
   */
  display?: 'inline' | 'block';
}

/**
 * Color mapping for each difficulty level.
 * These colors should be defined in CSS variables for theme consistency.
 */
export const DIFFICULTY_COLORS: Record<DifficultyLevel, string> = {
  beginner: 'var(--ifm-color-success)',      // Green
  intermediate: 'var(--ifm-color-primary)',  // Blue
  advanced: 'var(--ifm-color-danger)',       // Red
};

/**
 * Labels for each difficulty level (used for i18n).
 */
export const DIFFICULTY_LABELS: Record<DifficultyLevel, string> = {
  beginner: 'difficulty.beginner',
  intermediate: 'difficulty.intermediate',
  advanced: 'difficulty.advanced',
};

/**
 * Usage Example:
 * 
 * ```mdx
 * <DifficultyBadge level="beginner" />
 * 
 * <DifficultyBadge level="advanced" display="block" />
 * ```
 */
