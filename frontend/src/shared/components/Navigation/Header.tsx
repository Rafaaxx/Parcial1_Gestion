/**
 * Header component for the main layout
 * Displays user info, role badge, logout button, and hamburger menu for mobile
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/features/auth/store';
import { useUIStore } from '@/features/ui/store';
import { Badge, Button } from '@/shared/ui';

interface HeaderProps {
  onToggleSidebar?: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onToggleSidebar }) => {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const { sidebarOpen } = useUIStore();

  const handleLogout = () => {
    logout();
    navigate('/login', { replace: true });
  };

  return (
    <header className="sticky top-0 z-40 w-full border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 shadow-sm">
      <div className="flex items-center justify-between h-16 px-4 sm:px-6">
        {/* Left: Hamburger + Title */}
        <div className="flex items-center gap-4">
          <button
            onClick={onToggleSidebar}
            className="md:hidden p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            aria-label="Toggle sidebar"
          >
            {/* Hamburger icon */}
            <svg
              className="w-6 h-6 text-gray-700 dark:text-gray-300"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 6h16M4 12h16M4 18h16"
              />
            </svg>
          </button>

          <h1 className="text-xl font-bold text-gray-900 dark:text-white hidden sm:block">
            Food Store
          </h1>
        </div>

        {/* Right: User info + Logout */}
        {user && (
          <div className="flex items-center gap-4">
            {/* User Info */}
            <div className="flex items-center gap-3">
              <div className="text-right hidden sm:block">
                <p className="text-sm font-medium text-gray-900 dark:text-white">{user.name}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">{user.email}</p>
              </div>

              {/* Role Badge */}
              <div className="flex gap-1 flex-wrap">
                {user.roles.slice(0, 1).map((role) => (
                  <Badge key={role} variant="primary" size="sm">
                    {role}
                  </Badge>
                ))}
              </div>
            </div>

            {/* Logout Button */}
            <Button
              onClick={handleLogout}
              variant="secondary"
              className="text-sm"
            >
              Cerrar sesión
            </Button>
          </div>
        )}
      </div>
    </header>
  );
};
