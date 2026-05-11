/**
 * MenuItem component for sidebar navigation
 * Displays a menu item with icon, label, and active state
 */

import React from 'react';
import { Link, useLocation } from 'react-router-dom';

interface MenuItemProps {
  icon: string;
  label: string;
  path: string;
  isCollapsed?: boolean;
}

export const MenuItem: React.FC<MenuItemProps> = ({ icon, label, path, isCollapsed = false }) => {
  const location = useLocation();
  const isActive = location.pathname === path || location.pathname.startsWith(path + '/');

  return (
    <Link
      to={path}
      className={`flex items-center gap-3 px-4 py-2 rounded-lg transition-all ${
        isActive
          ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-200 font-medium'
          : 'text-gray-700 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800'
      } ${isCollapsed ? 'justify-center' : ''}`}
      title={isCollapsed ? label : undefined}
    >
      <span className="text-lg flex-shrink-0">{icon}</span>
      {!isCollapsed && <span className="truncate">{label}</span>}
    </Link>
  );
};
