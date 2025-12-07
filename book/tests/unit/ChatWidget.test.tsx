/**
 * ChatWidget component tests
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { ChatWidget } from '../../src/components/ChatWidget';

// Mock fetch for SSE
global.fetch = jest.fn();

describe('ChatWidget', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
  });

  it('renders floating button when closed', () => {
    render(<ChatWidget />);
    const button = screen.getByLabelText('Open chat');
    expect(button).toBeInTheDocument();
  });

  it('opens chat panel when button clicked', () => {
    render(<ChatWidget />);
    const button = screen.getByLabelText('Open chat');
    fireEvent.click(button);
    
    expect(screen.getByText('Textbook Assistant')).toBeInTheDocument();
  });

  it('closes chat panel when close button clicked', () => {
    render(<ChatWidget />);
    
    // Open
    fireEvent.click(screen.getByLabelText('Open chat'));
    expect(screen.getByText('Textbook Assistant')).toBeInTheDocument();
    
    // Close
    fireEvent.click(screen.getByLabelText('Close chat'));
    expect(screen.queryByText('Textbook Assistant')).not.toBeInTheDocument();
  });

  it('displays empty state initially', () => {
    render(<ChatWidget />);
    fireEvent.click(screen.getByLabelText('Open chat'));
    
    expect(screen.getByText('Ask me anything about the textbook!')).toBeInTheDocument();
  });

  it('switches language when language button clicked', () => {
    render(<ChatWidget />);
    fireEvent.click(screen.getByLabelText('Open chat'));
    
    const urButton = screen.getByText('UR');
    fireEvent.click(urButton);
    
    // Should see Urdu placeholder
    const input = screen.getByPlaceholderText('کتاب کے بارے میں سوال پوچھیں...');
    expect(input).toBeInTheDocument();
  });

  it('clears history when clear button clicked', async () => {
    render(<ChatWidget />);
    fireEvent.click(screen.getByLabelText('Open chat'));
    
    // Send a message (will be added to state)
    const input = screen.getByPlaceholderText('Ask a question about the textbook...');
    fireEvent.change(input, { target: { value: 'Test message' } });
    
    // Clear history
    fireEvent.click(screen.getByLabelText('Clear history'));
    
    // Session token should be cleared
    expect(localStorage.getItem('rag_chat_session_token')).toBeNull();
  });

  it('enables send button only when input has text', () => {
    render(<ChatWidget />);
    fireEvent.click(screen.getByLabelText('Open chat'));
    
    const sendButton = screen.getByLabelText('Send message');
    expect(sendButton).toBeDisabled();
    
    const input = screen.getByPlaceholderText('Ask a question about the textbook...');
    fireEvent.change(input, { target: { value: 'Test' } });
    
    expect(sendButton).not.toBeDisabled();
  });

  it('adds user message when send clicked', () => {
    render(<ChatWidget />);
    fireEvent.click(screen.getByLabelText('Open chat'));
    
    const input = screen.getByPlaceholderText('Ask a question about the textbook...');
    fireEvent.change(input, { target: { value: 'What is kinematics?' } });
    
    const sendButton = screen.getByLabelText('Send message');
    fireEvent.click(sendButton);
    
    // User message should appear
    expect(screen.getByText('What is kinematics?')).toBeInTheDocument();
  });

  it('stores session token in localStorage', () => {
    render(<ChatWidget />);
    fireEvent.click(screen.getByLabelText('Open chat'));
    
    const input = screen.getByPlaceholderText('Ask a question about the textbook...');
    fireEvent.change(input, { target: { value: 'Test' } });
    fireEvent.click(screen.getByLabelText('Send message'));
    
    // Should have created session token
    const token = localStorage.getItem('rag_chat_session_token');
    expect(token).toBeTruthy();
  });
});
