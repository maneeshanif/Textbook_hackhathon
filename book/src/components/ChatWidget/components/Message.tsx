/**
 * Message component - displays a single chat message
 */

import React from 'react';
import type { ChatMessage } from '../types';
import styles from './Message.module.css';

interface MessageProps {
  message: ChatMessage;
  onCitationClick?: (url: string) => void;
}

export function Message({ message, onCitationClick }: MessageProps) {
  const isUser = message.role === 'user';

  return (
    <div className={`${styles.message} ${isUser ? styles.userMessage : styles.assistantMessage}`}>
      <div className={styles.messageContent}>
        <div className={styles.messageText}>
          {message.content}
        </div>
        
        {message.citations && message.citations.length > 0 && (
          <div className={styles.citations}>
            <div className={styles.citationsLabel}>📚 Related chapters:</div>
            <div className={styles.citationsList}>
              {message.citations.map((citation, index) => (
                <button
                  key={index}
                  className={styles.citationLink}
                  onClick={() => onCitationClick?.(citation.url)}
                >
                  {citation.chapterTitle}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
      
      <div className={styles.messageTime}>
        {message.timestamp.toLocaleTimeString([], { 
          hour: '2-digit', 
          minute: '2-digit' 
        })}
      </div>
    </div>
  );
}
