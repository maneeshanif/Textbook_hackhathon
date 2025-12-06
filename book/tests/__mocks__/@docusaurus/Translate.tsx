import React from 'react';

interface TranslateProps {
  id?: string;
  description?: string;
  children: React.ReactNode;
}

export default function Translate({ children }: TranslateProps): JSX.Element {
  return <>{children}</>;
}
