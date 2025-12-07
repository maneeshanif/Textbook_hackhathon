/**
 * Custom hook for streaming chat responses using Server-Sent Events (SSE)
 */

import { useState, useCallback } from 'react';
import type { ChatMessage, Citation } from '../types';

interface UseStreamingQueryResult {
  sendQuery: (query: string, sessionToken?: string, selectedText?: string) => Promise<void>;
  isLoading: boolean;
  error: string | null;
  currentMessage: string;
  citations: Citation[];
}

// API URL - update this for production deployment
const API_BASE_URL = 'http://localhost:8000';

export function useStreamingQuery(
  language: string,
  onMessageComplete: (message: ChatMessage) => void
): UseStreamingQueryResult {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentMessage, setCurrentMessage] = useState('');
  const [citations, setCitations] = useState<Citation[]>([]);

  const sendQuery = useCallback(
    async (query: string, sessionToken?: string, selectedText?: string) => {
      setIsLoading(true);
      setError(null);
      setCurrentMessage('');
      setCitations([]);

      try {
        // Get auth token from localStorage
        const authToken = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null;
        
        const headers: Record<string, string> = {
          'Content-Type': 'application/json',
        };
        
        // Add auth token if available
        if (authToken) {
          headers['Authorization'] = `Bearer ${authToken}`;
        }

        const response = await fetch(`${API_BASE_URL}/api/chat/query`, {
          method: 'POST',
          headers,
          body: JSON.stringify({
            query,
            session_token: sessionToken,
            language,
            selected_text: selectedText,
          }),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body?.getReader();
        const decoder = new TextDecoder();
        let fullResponse = '';

        if (!reader) {
          throw new Error('Response body is not readable');
        }

        while (true) {
          const { done, value } = await reader.read();
          
          if (done) break;

          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6);
              
              try {
                const parsed = JSON.parse(data);

                if (parsed.chunk) {
                  // Accumulate streaming chunks
                  fullResponse += parsed.chunk;
                  setCurrentMessage(fullResponse);
                } else if (parsed.done) {
                  // Stream complete
                  const message: ChatMessage = {
                    id: parsed.message_id,
                    role: 'assistant',
                    content: fullResponse,
                    timestamp: new Date(),
                    citations: parsed.citations?.map((c: any) => ({
                      chapterId: c.chapter_id,
                      chapterTitle: c.title,
                      url: c.url,
                    })) || [],
                  };

                  setCitations(message.citations || []);
                  onMessageComplete(message);
                  setIsLoading(false);
                } else if (parsed.error) {
                  throw new Error(parsed.message || 'Unknown error');
                }
              } catch (e) {
                console.error('Failed to parse SSE data:', data, e);
              }
            }
          }
        }
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to send query';
        setError(errorMessage);
        setIsLoading(false);
      }
    },
    [language, onMessageComplete]
  );

  return {
    sendQuery,
    isLoading,
    error,
    currentMessage,
    citations,
  };
}
