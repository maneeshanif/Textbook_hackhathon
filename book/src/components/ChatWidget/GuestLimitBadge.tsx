import React from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useGuest } from '@/contexts/GuestContext';

export function GuestLimitBadge() {
  const { user } = useAuth();
  const { count, limit, isLimitReached } = useGuest();

  // Don't show badge for authenticated users
  if (user) {
    return null;
  }

  // Calculate percentage for color coding
  const percentage = (count / limit) * 100;
  const isWarning = percentage >= 80; // 8+ interactions
  const isDanger = isLimitReached;

  return (
    <div
      className={`
        inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium
        transition-all duration-300
        ${isDanger ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200 animate-pulse' : ''}
        ${isWarning && !isDanger ? 'bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200 animate-pulse' : ''}
        ${!isWarning && !isDanger ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200' : ''}
      `}
      aria-label={`Guest interactions: ${count} of ${limit} used`}
    >
      <svg
        className="w-3 h-3 mr-1"
        fill="currentColor"
        viewBox="0 0 20 20"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          fillRule="evenodd"
          d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
          clipRule="evenodd"
        />
      </svg>
      <span>
        {count}/{limit} free questions
      </span>
    </div>
  );
}
