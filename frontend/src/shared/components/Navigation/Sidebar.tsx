/**
 * Sidebar component for navigation
 * Renders menu items based on user roles
 * Responsive: full width on desktop, collapsed to icons on mobile
 */

import React from 'react';
import { useAuthStore, userHasRole } from '@/features/auth/store';
import { useUIStore } from '@/features/ui/store';
import { MenuItem } from './MenuItem';
import { MENU_BY_ROLE } from './menuConfig';

interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ isOpen = true, onClose }) => {
  const { user } = useAuthStore();
  const { sidebarOpen } = useUIStore();

  // Determine if sidebar should be visible (mobile: by isOpen prop, desktop: always visible)
  const shouldShow = isOpen ?? sidebarOpen;

  // Filter menu items based on user roles
  const visibleMenuItems = MENU_BY_ROLE.filter((item) => userHasRole(user, item.roles));

  return (
    <>
      {/* Mobile Overlay */}
      {!shouldShow && (
        <div
          className="fixed inset-0 bg-black/50 z-30 md:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed md:static left-0 top-0 h-full md:h-[calc(100vh-64px)] w-64 md:w-64 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800 shadow-lg md:shadow-sm z-40 md:z-auto transform transition-transform duration-300 ${
          shouldShow ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
        }`}
      >
        <div className="h-full flex flex-col overflow-hidden">
          {/* Sidebar Header (Mobile only) */}
          <div className="md:hidden p-4 border-b border-gray-200 dark:border-gray-800 flex items-center justify-between">
            <h2 className="font-bold text-gray-900 dark:text-white">Menu</h2>
            <button
              onClick={onClose}
              className="p-1 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
              aria-label="Close sidebar"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>

          {/* User Info */}
          {user && (
            <div className="px-4 py-4 border-b border-gray-200 dark:border-gray-800 hidden md:block">
              <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                {user.name}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400 truncate">{user.email}</p>
              <div className="mt-2 flex gap-1 flex-wrap">
                {user.roles.map((role) => (
                  <span
                    key={role}
                    className="inline-block px-2 py-1 text-xs font-medium bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded"
                  >
                    {role}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-2 overflow-y-auto">
            {visibleMenuItems.length > 0 ? (
              visibleMenuItems.map((item) => (
                <MenuItem
                  key={item.path}
                  icon={item.icon}
                  label={item.label}
                  path={item.path}
                  isCollapsed={false}
                />
              ))
            ) : (
              <p className="text-sm text-gray-500 dark:text-gray-400 px-4 py-2">
                No menu items available
              </p>
            )}
          </nav>
        </div>
      </aside>
    </>
  );
};
