/**
 * Type definitions for RAG chatbot widget
 */

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  citations?: Citation[];
  selectedText?: string;
}

export interface Citation {
  chapterId: string;
  chapterTitle: string;
  section?: string;
  url: string;
}

export interface ChatSession {
  sessionToken: string;
  messages: ChatMessage[];
  language: 'en' | 'ur';
  createdAt: Date;
  lastActive: Date;
}

export interface QueryRequest {
  query: string;
  sessionToken?: string;
  language?: 'en' | 'ur';
  selectedText?: string;
}

export interface QueryResponse {
  answer: string;
  citations: Citation[];
  similarityScore?: number;
  requestId: string;
}

export interface StreamChunk {
  type: 'content' | 'citation' | 'done' | 'error';
  content?: string;
  citation?: Citation;
  error?: string;
}

export interface HistoryResponse {
  messages: ChatMessage[];
  hasMore: boolean;
  nextCursor?: string;
}

export interface FeedbackRequest {
  messageId: string;
  rating: 'positive' | 'negative';
  sessionToken: string;
}

export interface WidgetConfig {
  apiBaseUrl: string;
  language: 'en' | 'ur';
  maxMessages: number;
  enableAuth: boolean;
}

export interface AuthState {
  isAuthenticated: boolean;
  userId?: string;
  email?: string;
}
