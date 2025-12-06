import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import ChapterHeader from '../index';

describe('ChapterHeader', () => {
  const defaultProps = {
    number: '1.1.1',
    title: 'Test Chapter',
    difficulty: 'beginner' as const,
    estimatedTime: '30 minutes',
  };

  it('renders chapter number and title', () => {
    render(<ChapterHeader {...defaultProps} />);
    expect(screen.getByText('Test Chapter')).toBeInTheDocument();
    expect(screen.getByLabelText('Chapter 1.1.1')).toBeInTheDocument();
  });

  it('renders description when provided', () => {
    render(<ChapterHeader {...defaultProps} description="Test description" />);
    expect(screen.getByText('Test description')).toBeInTheDocument();
  });

  it('renders tags when provided', () => {
    render(<ChapterHeader {...defaultProps} tags={['tag1', 'tag2']} />);
    expect(screen.getByText('tag1')).toBeInTheDocument();
    expect(screen.getByText('tag2')).toBeInTheDocument();
  });

  it('shows TOC link by default', () => {
    render(<ChapterHeader {...defaultProps} />);
    expect(screen.getByText('📋 Table of Contents')).toBeInTheDocument();
  });

  it('hides TOC link when showTocLink is false', () => {
    render(<ChapterHeader {...defaultProps} showTocLink={false} />);
    expect(screen.queryByText('📋 Table of Contents')).not.toBeInTheDocument();
  });

  it('uses section number when provided', () => {
    render(<ChapterHeader {...defaultProps} sectionNumber="1.2" />);
    expect(screen.getByLabelText('Chapter 1.2')).toBeInTheDocument();
  });

  it('displays estimated time', () => {
    render(<ChapterHeader {...defaultProps} />);
    expect(screen.getByLabelText('Estimated time: 30 minutes')).toBeInTheDocument();
  });
});
