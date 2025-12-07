import React, { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useGuest } from '@/contexts/GuestContext';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { SignUpForm } from './SignUpForm';
import { LoginForm } from './LoginForm';

interface AuthDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  defaultTab?: 'login' | 'signup';
}

export function AuthDialog({ open, onOpenChange, defaultTab = 'signup' }: AuthDialogProps) {
  const { error, clearError } = useAuth();
  const { isLimitReached, interactionCount, GUEST_INTERACTION_LIMIT } = useGuest();
  const [activeTab, setActiveTab] = useState<string>(defaultTab);

  const handleOpenChange = (newOpen: boolean) => {
    if (!newOpen) {
      clearError();
    }
    onOpenChange(newOpen);
  };

  const handleSuccess = () => {
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>
            {isLimitReached ? 'Unlock Unlimited Questions' : 'Welcome to Physical AI Textbook'}
          </DialogTitle>
          <DialogDescription>
            {isLimitReached ? (
              <>
                You've explored {interactionCount} questions as a guest. Create an account to continue your AI learning journey!
              </>
            ) : (
              'Sign up or log in to save your progress and access personalized features.'
            )}
          </DialogDescription>
        </DialogHeader>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="signup">Sign Up</TabsTrigger>
            <TabsTrigger value="login">Log In</TabsTrigger>
          </TabsList>

          <TabsContent value="signup">
            <SignUpForm onSuccess={handleSuccess} onSwitchToLogin={() => setActiveTab('login')} />
          </TabsContent>

          <TabsContent value="login">
            <LoginForm onSuccess={handleSuccess} onSwitchToSignup={() => setActiveTab('signup')} />
          </TabsContent>
        </Tabs>

        {error && (
          <div className="mt-2 text-sm text-red-600 dark:text-red-400">
            {error}
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
