/**
 * ChatbotPlaceholder Component Contract
 * 
 * Displays a placeholder widget for the upcoming RAG chatbot (Phase 2).
 * Provides visual indication of the feature and handles clicks gracefully.
 * 
 * @accessibility
 * - Keyboard accessible (focusable, Enter/Space to activate)
 * - Includes aria-label describing the feature
 * - Visible focus indicator
 */

export type ChatbotPosition = 'bottom-right' | 'bottom-left' | 'inline';

export interface ChatbotPlaceholderProps {
  /**
   * Position of the chatbot widget on the page.
   * @default 'bottom-right'
   */
  position?: ChatbotPosition;

  /**
   * Callback when user clicks on the placeholder.
   * If not provided, shows a default "Coming soon" message.
   */
  onExpand?: () => void;

  /**
   * Custom message to display when expanded.
   * @default 'AI Assistant coming soon!'
   */
  comingSoonMessage?: string;

  /**
   * Whether to show the placeholder.
   * Useful for conditionally hiding during development.
   * @default true
   */
  visible?: boolean;

  /**
   * Optional CSS class for custom styling.
   */
  className?: string;

  /**
   * Icon to display (React node or emoji).
   * @default '🤖'
   */
  icon?: React.ReactNode;
}

/**
 * State interface for the component.
 */
export interface ChatbotPlaceholderState {
  isExpanded: boolean;
  showTooltip: boolean;
}

/**
 * CSS Custom Properties for theming.
 * Should be defined in :root or theme CSS.
 */
export const CHATBOT_CSS_VARS = {
  '--chatbot-bg': 'var(--ifm-color-primary)',
  '--chatbot-text': '#ffffff',
  '--chatbot-shadow': '0 4px 12px rgba(0, 0, 0, 0.15)',
  '--chatbot-size': '56px',
  '--chatbot-border-radius': '50%',
};

/**
 * Usage Example:
 * 
 * ```mdx
 * <!-- Basic usage (fixed position) -->
 * <ChatbotPlaceholder />
 * 
 * <!-- Custom position and message -->
 * <ChatbotPlaceholder 
 *   position="bottom-left" 
 *   comingSoonMessage="AI tutor launching in Phase 2!"
 * />
 * 
 * <!-- Inline placement -->
 * <ChatbotPlaceholder position="inline" icon="💬" />
 * ```
 */
