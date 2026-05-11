import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * Main Layout component with Header + Sidebar + Outlet
 * Manages responsive behavior and sidebar toggle
 */
import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Header } from './Header';
import { Sidebar } from './Sidebar';
/**
 * Layout: Main layout wrapper for authenticated routes
 * Renders Header (sticky top), Sidebar (left), and main content (Outlet)
 * Sidebar is collapsible on mobile
 */
export const Layout = () => {
    const [sidebarOpen, setSidebarOpen] = useState(true);
    const handleToggleSidebar = () => {
        setSidebarOpen((prev) => !prev);
    };
    const handleCloseSidebar = () => {
        setSidebarOpen(false);
    };
    return (_jsxs("div", { className: "flex flex-col h-screen bg-gray-50 dark:bg-gray-950", children: [_jsx(Header, { onToggleSidebar: handleToggleSidebar }), _jsxs("div", { className: "flex flex-1 overflow-hidden", children: [_jsx(Sidebar, { isOpen: sidebarOpen, onClose: handleCloseSidebar }), _jsx("main", { className: "flex-1 overflow-auto bg-gray-50 dark:bg-gray-950", children: _jsx("div", { className: "h-full", children: _jsx(Outlet, {}) }) })] })] }));
};
//# sourceMappingURL=Layout.js.map