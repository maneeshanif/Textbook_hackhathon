import React, { useState } from 'react';
import Translate from '@docusaurus/Translate';
import styles from './styles.module.css';

export type ChatbotPosition = 'bottom-right' | 'bottom-left' | 'inline';

export interface ChatbotPlaceholderProps {
  position?: ChatbotPosition;
  onExpand?: () => void;
  comingSoonMessage?: string;
  visible?: boolean;
  className?: string;
  icon?: React.ReactNode;
}

export default function ChatbotPlaceholder({
  position = 'bottom-right',
  onExpand,
  comingSoonMessage,
  visible = true,
  className = '',
  icon = '🤖',
}: ChatbotPlaceholderProps): JSX.Element | null {
  const [isExpanded, setIsExpanded] = useState(false);
  const [showTooltip, setShowTooltip] = useState(false);

  if (!visible) {
    return null;
  }

  const handleClick = () => {
    if (onExpand) {
      onExpand();
    } else {
      setIsExpanded(!isExpanded);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleClick();
    }
    if (e.key === 'Escape' && isExpanded) {
      setIsExpanded(false);
    }
  };

  const defaultMessage = (
    <Translate
      id="chatbot.comingSoon"
      description="Coming soon message for chatbot placeholder"
    >
      AI Assistant coming soon!
    </Translate>
  );

  const positionClass = position === 'inline' ? styles.inline : styles.fixed;
  const alignmentClass = position === 'bottom-left' ? styles.left : styles.right;

  return (
    <>
      <div
        className={`${styles.chatbotPlaceholder} ${positionClass} ${alignmentClass} ${className}`}
        onClick={handleClick}
        onKeyDown={handleKeyDown}
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
        role="button"
        tabIndex={0}
        aria-label="AI Assistant (Coming Soon)"
        aria-expanded={isExpanded}
      >
        <div className={styles.iconContainer}>
          {icon}
        </div>
        
        {showTooltip && !isExpanded && (
          <div className={styles.tooltip} role="tooltip">
            <Translate
              id="chatbot.clickToLearnMore"
              description="Tooltip for chatbot placeholder"
            >
              Click to learn more
            </Translate>
          </div>
        )}
      </div>

      {isExpanded && (
        <div className={styles.modal} onClick={() => setIsExpanded(false)}>
          <div 
            className={styles.modalContent} 
            onClick={(e) => e.stopPropagation()}
            role="dialog"
            aria-modal="true"
            aria-labelledby="chatbot-modal-title"
          >
            <button
              className={styles.closeButton}
              onClick={() => setIsExpanded(false)}
              aria-label="Close"
            >
              ✕
            </button>
            <div className={styles.modalIcon}>{icon}</div>
            <h3 id="chatbot-modal-title" className={styles.modalTitle}>
              {comingSoonMessage || defaultMessage}
            </h3>
            <p className={styles.modalDescription}>
              <Translate
                id="chatbot.phase2Feature"
                description="Description of chatbot as Phase 2 feature"
              >
                This feature will be available in Phase 2. The AI assistant will help you:
              </Translate>
            </p>
            <ul className={styles.featureList}>
              <li>
                <Translate id="chatbot.feature.questions">
                  Answer questions about course content
                </Translate>
              </li>
              <li>
                <Translate id="chatbot.feature.explanations">
                  Provide detailed explanations
                </Translate>
              </li>
              <li>
                <Translate id="chatbot.feature.examples">
                  Generate code examples
                </Translate>
              </li>
              <li>
                <Translate id="chatbot.feature.progress">
                  Track your learning progress
                </Translate>
              </li>
            </ul>
          </div>
        </div>
      )}
    </>
  );
}
