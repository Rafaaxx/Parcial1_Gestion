## ADDED Requirements

### Requirement: Layout component wraps protected pages with header and sidebar

The system SHALL implement a Layout component that renders a consistent structure for all protected pages: Header at the top, Sidebar on the left (collapsible on mobile), and content area (Outlet) on the right.

#### Scenario: Layout renders with header, sidebar, and content area
- **WHEN** user is on a protected page (e.g., /app/orders)
- **THEN** Layout component is rendered with three sections: Header (top), Sidebar (left), main content (center/right)
- **THEN** Header shows user info and logout button
- **THEN** Sidebar shows role-specific menu items
- **THEN** main content area renders the current page via react-router Outlet

#### Scenario: Layout persists across page navigation
- **WHEN** user clicks a menu item to navigate from /app/orders to /app/profile
- **THEN** Layout remains visible (does not re-render or flicker)
- **THEN** only the content in Outlet changes

### Requirement: Layout is responsive

The system SHALL make the Layout responsive for mobile, tablet, and desktop viewports.

#### Scenario: Desktop layout shows full sidebar
- **WHEN** viewport width is >= 768px (md breakpoint)
- **THEN** Sidebar is always visible (not collapsed) with full text and icons

#### Scenario: Mobile layout shows collapsed sidebar
- **WHEN** viewport width is < 768px (md breakpoint)
- **THEN** Sidebar collapses to icons only or hides completely
- **THEN** Hamburger toggle button appears in Header

#### Scenario: Content area adapts to sidebar state
- **WHEN** Sidebar toggles between expanded and collapsed states
- **THEN** main content area reflows to use available width
- **THEN** no content is cut off

### Requirement: Layout supports mobile sidebar overlay

The system SHALL implement a mobile-friendly sidebar that overlays the content when expanded on mobile.

#### Scenario: Sidebar overlay covers content on mobile
- **WHEN** user is on mobile and opens sidebar via hamburger
- **THEN** Sidebar expands as an overlay on top of the content
- **THEN** optional: semi-transparent backdrop appears behind sidebar

#### Scenario: Clicking backdrop or menu item closes sidebar
- **WHEN** user clicks outside the sidebar or selects a menu item
- **THEN** Sidebar collapses/closes
- **THEN** uiStore.sidebarOpen is set to false

### Requirement: Layout styling is consistent with design system

The system SHALL style Layout and its child components (Header, Sidebar, content area) using Tailwind CSS utility classes with a consistent color scheme and spacing.

#### Scenario: Header styling is consistent
- **WHEN** Header is rendered
- **THEN** Header uses consistent background color (e.g., bg-blue-600), text color, and padding
- **THEN** user info and logout button are properly aligned

#### Scenario: Sidebar styling is consistent
- **WHEN** Sidebar is rendered
- **THEN** Sidebar uses consistent background, border, and text colors
- **THEN** menu items have hover states and active state highlighting
- **THEN** spacing between items is consistent (e.g., py-2, px-4)

#### Scenario: Content area has proper padding
- **WHEN** content area (main/section) is rendered inside Layout
- **THEN** content has proper margin/padding from edges
- **THEN** no content is flush against borders or overlaps with header/sidebar

### Requirement: Layout includes footer (optional)

The system MAY include a footer at the bottom of the page within or below the Layout.

#### Scenario: Footer appears on all protected pages
- **WHEN** user is on a protected page
- **THEN** Footer is visible at the bottom with copyright, links, or company info
