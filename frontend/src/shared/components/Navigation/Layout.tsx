/**
 * Main Layout component with Header + Sidebar + Outlet
 * Manages responsive behavior and sidebar toggle
 */

import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Header } from './Header';
import { Sidebar } from './Sidebar';

/**
 * Layout: Main layout wrapper for authenticated routes
 * Renders Header (sticky top), Sidebar (left), and main content (Outlet)
 * Sidebar is collapsible on mobile
 */
export const Layout: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const handleToggleSidebar = () => {
    setSidebarOpen((prev) => !prev);
  };

  const handleCloseSidebar = () => {
    setSidebarOpen(false);
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50 dark:bg-gray-950">
      {/* Header */}
      <Header onToggleSidebar={handleToggleSidebar} />

      {/* Main Content Area */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <Sidebar isOpen={sidebarOpen} onClose={handleCloseSidebar} />

        {/* Main Content */}
        <main className="flex-1 overflow-auto bg-gray-50 dark:bg-gray-950">
          <div className="h-full">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
};
