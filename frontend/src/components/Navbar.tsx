'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { authService } from '@/services/authService';

export default function Navbar() {
  const pathname = usePathname();
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    // Check authentication status when the component mounts
    const checkAuth = () => {
      setIsAuthenticated(authService.isAuthenticated());
      setLoading(false);
    };
    
    checkAuth();
    
    // Listen for storage events (for logout from another tab)
    const handleStorageChange = () => {
      checkAuth();
    };
    
    window.addEventListener('storage', handleStorageChange);
    return () => {
      window.removeEventListener('storage', handleStorageChange);
    };
  }, []);

  const handleLogout = () => {
    authService.logout();
    setIsAuthenticated(false);
    router.push('/login');
  };

  return (
    <nav className="bg-blue-800 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <Link href="/" className="text-xl font-bold">
              WaterWatch
            </Link>
            <div className="hidden md:block ml-10">
              <div className="flex space-x-4">
                <Link
                  href="/water-quality"
                  className={`px-3 py-2 rounded-md text-sm font-medium ${
                    pathname === '/water-quality'
                      ? 'bg-blue-900 text-white'
                      : 'text-blue-100 hover:bg-blue-700'
                  }`}
                >
                  Water Quality
                </Link>
                <Link
                  href="/documentation"
                  className={`px-3 py-2 rounded-md text-sm font-medium ${
                    pathname === '/documentation'
                      ? 'bg-blue-900 text-white'
                      : 'text-blue-100 hover:bg-blue-700'
                  }`}
                >
                  Documentation
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
} 