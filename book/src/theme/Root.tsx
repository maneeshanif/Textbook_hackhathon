/**
 * Docusaurus Root wrapper - integrates ChatWidget and AuthProvider into every page
 */

import React from 'react';
import { ChatWidget } from '../components/ChatWidget';
import { AuthProvider } from '../contexts/AuthContext';

// Default implementation - this component wraps the entire app
export default function Root({ children }: { children: React.ReactNode }): JSX.Element {
  return (
    <AuthProvider>
      {children}
      <ChatWidget />
    </AuthProvider>
  );
}
