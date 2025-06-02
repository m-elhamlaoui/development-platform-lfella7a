'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { authService } from '@/services/authService';

interface User {
  id: number;
  username: string;
  email: string;
}

export default function DashboardPage() {
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState<User | null>(null);
  const router = useRouter();
  
  useEffect(() => {
    const checkAuth = async () => {
      try {
        // Check if the user is authenticated
        if (!authService.isAuthenticated()) {
          router.push('/login');
          return;
        }
        
        // Get the current user data
        const userData = await authService.getCurrentUser();
        if (!userData) {
          // If no user data, logout and redirect
          authService.logout();
          router.push('/login');
          return;
        }
        
        setUser(userData.user);
      } catch (error) {
        console.error('Error checking authentication:', error);
        router.push('/login');
      } finally {
        setLoading(false);
      }
    };
    
    checkAuth();
  }, [router]);

  // Function to handle logout
  const handleLogout = () => {
    authService.logout();
    router.push('/login');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-300">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-gray-800 dark:text-white">Dashboard</h1>
          <button
            onClick={handleLogout}
            className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
          >
            Logout
          </button>
        </div>
        
        <div className="bg-white dark:bg-gray-800 shadow-md rounded-lg p-6">
          {user && (
            <div className="mb-6">
              <h2 className="text-xl font-semibold text-gray-700 dark:text-gray-200">
                Welcome back, {user.username}!
              </h2>
              <p className="text-gray-600 dark:text-gray-400 mt-2">
                Your email: {user.email}
              </p>
            </div>
          )}
          
          <div className="mb-4">
            <h3 className="text-lg font-medium text-gray-700 dark:text-gray-200">Your Account</h3>
            <p className="text-gray-600 dark:text-gray-400 mt-2">
              This is your personal dashboard. Here you can manage your account and settings.
            </p>
          </div>
          
          <div className="mt-6 border-t dark:border-gray-700 pt-6">
            <p className="text-gray-500 dark:text-gray-400">More features will be added soon.</p>
          </div>
        </div>
      </div>
    </div>
  );
} 