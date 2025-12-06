import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import ChatbotPlaceholder from '../../src/components/ChatbotPlaceholder';

describe('ChatbotPlaceholder', () => {
  it('renders with default props', () => {
    render(<ChatbotPlaceholder />);
    expect(screen.getByRole('button')).toBeInTheDocument();
    expect(screen.getByLabelText('AI Assistant (Coming Soon)')).toBeInTheDocument();
  });

  it('does not render when visible is false', () => {
    render(<ChatbotPlaceholder visible={false} />);
    expect(screen.queryByRole('button')).not.toBeInTheDocument();
  });

  it('shows modal when clicked', () => {
    render(<ChatbotPlaceholder />);
    const button = screen.getByRole('button');
    fireEvent.click(button);
    expect(screen.getByRole('dialog')).toBeInTheDocument();
    expect(screen.getByText(/AI Assistant coming soon/i)).toBeInTheDocument();
  });

  it('closes modal when close button is clicked', () => {
    render(<ChatbotPlaceholder />);
    fireEvent.click(screen.getByRole('button'));
    const closeButton = screen.getByLabelText('Close');
    fireEvent.click(closeButton);
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  });

  it('supports custom message', () => {
    render(<ChatbotPlaceholder comingSoonMessage="Custom message!" />);
    fireEvent.click(screen.getByRole('button'));
    expect(screen.getByText('Custom message!')).toBeInTheDocument();
  });

  it('handles keyboard navigation', () => {
    render(<ChatbotPlaceholder />);
    const button = screen.getByRole('button');
    fireEvent.keyDown(button, { key: 'Enter' });
    expect(screen.getByRole('dialog')).toBeInTheDocument();
  });

  it('calls onExpand when provided', () => {
    const onExpand = jest.fn();
    render(<ChatbotPlaceholder onExpand={onExpand} />);
    fireEvent.click(screen.getByRole('button'));
    expect(onExpand).toHaveBeenCalledTimes(1);
  });

  it('renders custom icon', () => {
    render(<ChatbotPlaceholder icon="💬" />);
    expect(screen.getByText('💬')).toBeInTheDocument();
  });
});
