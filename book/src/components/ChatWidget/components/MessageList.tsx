/**
 * MessageList component - displays all chat messages
 */

import React, { useEffect, useRef } from 'react';
import type { ChatMessage } from '../types';
import { Message } from './Message';
import styles from './MessageList.module.css';

interface MessageListProps {
  messages: ChatMessage[];
  currentMessage?: string;
  isLoading: boolean;
  onCitationClick?: (url: string) => void;
}

export function MessageList({ 
  messages, 
  currentMessage, 
  isLoading,
  onCitationClick 
}: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, currentMessage]);

  return (
    <div className={styles.messageList}>
      {messages.length === 0 && !currentMessage && (
        <div className={styles.emptyState}>
          <div className={styles.emptyStateIcon}>💬</div>
          <h3>Ask me anything about the textbook!</h3>
          <p>I can help you understand concepts, explain topics, and answer your questions.</p>
        </div>
      )}

      {messages.map((message) => (
        <Message 
          key={message.id} 
          message={message}
          onCitationClick={onCitationClick}
        />
      ))}

      {currentMessage && (
        <div className={styles.streamingMessage}>
          <div className={styles.messageContent}>
            <div className={styles.messageText}>
              {currentMessage}
              <span className={styles.cursor}>▋</span>
            </div>
          </div>
        </div>
      )}

      {isLoading && !currentMessage && (
        <div className={styles.loadingIndicator}>
          <div className={styles.loadingDot}></div>
          <div className={styles.loadingDot}></div>
          <div className={styles.loadingDot}></div>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}
