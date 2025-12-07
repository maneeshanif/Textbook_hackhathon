/**
 * Session management utilities for localStorage
 */

const SESSION_TOKEN_KEY = 'rag_chat_session_token';
const SESSION_LANGUAGE_KEY = 'rag_chat_language';

export function getSessionToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(SESSION_TOKEN_KEY);
}

export function setSessionToken(token: string): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem(SESSION_TOKEN_KEY, token);
}

export function clearSessionToken(): void {
  if (typeof window === 'undefined') return;
  localStorage.removeItem(SESSION_TOKEN_KEY);
}

export function getSessionLanguage(): string {
  if (typeof window === 'undefined') return 'en';
  return localStorage.getItem(SESSION_LANGUAGE_KEY) || 'en';
}

export function setSessionLanguage(language: string): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem(SESSION_LANGUAGE_KEY, language);
}

export function generateSessionToken(): string {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}
