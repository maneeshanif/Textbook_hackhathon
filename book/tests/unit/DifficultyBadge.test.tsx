import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import DifficultyBadge from '../index';

describe('DifficultyBadge', () => {
  it('renders beginner badge correctly', () => {
    render(<DifficultyBadge level="beginner" />);
    expect(screen.getByText(/beginner/i)).toBeInTheDocument();
    expect(screen.getByRole('status')).toHaveClass('beginner');
  });

  it('renders intermediate badge correctly', () => {
    render(<DifficultyBadge level="intermediate" />);
    expect(screen.getByText(/intermediate/i)).toBeInTheDocument();
    expect(screen.getByRole('status')).toHaveClass('intermediate');
  });

  it('renders advanced badge correctly', () => {
    render(<DifficultyBadge level="advanced" />);
    expect(screen.getByText(/advanced/i)).toBeInTheDocument();
    expect(screen.getByRole('status')).toHaveClass('advanced');
  });

  it('applies custom className', () => {
    render(<DifficultyBadge level="beginner" className="custom-class" />);
    expect(screen.getByRole('status')).toHaveClass('custom-class');
  });

  it('renders as block display', () => {
    render(<DifficultyBadge level="beginner" display="block" />);
    expect(screen.getByRole('status')).toHaveClass('block');
  });

  it('has proper accessibility attributes', () => {
    render(<DifficultyBadge level="intermediate" />);
    const badge = screen.getByRole('status');
    expect(badge).toHaveAttribute('aria-label', 'Difficulty: intermediate');
  });
});
