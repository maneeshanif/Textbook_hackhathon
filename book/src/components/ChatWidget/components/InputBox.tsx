/**
 * InputBox component - text input for user queries
 */

import React, { useState, KeyboardEvent } from 'react';
import styles from './InputBox.module.css';

interface InputBoxProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export function InputBox({ onSend, disabled, placeholder }: InputBoxProps) {
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (input.trim() && !disabled) {
      onSend(input.trim());
      setInput('');
    }
  };

  const handleKeyPress = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className={styles.inputBox}>
      <textarea
        className={styles.textarea}
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyPress={handleKeyPress}
        placeholder={placeholder || 'Ask a question about the textbook...'}
        disabled={disabled}
        rows={1}
        maxLength={2000}
      />
      <button
        className={styles.sendButton}
        onClick={handleSend}
        disabled={disabled || !input.trim()}
        aria-label="Send message"
      >
        <svg
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <line x1="22" y1="2" x2="11" y2="13" />
          <polygon points="22 2 15 22 11 13 2 9 22 2" />
        </svg>
      </button>
    </div>
  );
}
