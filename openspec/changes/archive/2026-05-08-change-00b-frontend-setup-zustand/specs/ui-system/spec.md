## ADDED Requirements

### Requirement: Button Component
The system SHALL provide a reusable Button component with variants: primary, secondary, danger, and states: default, loading, disabled.

#### Scenario: Render primary button
- **WHEN** developer renders `<Button variant="primary">Click Me</Button>`
- **THEN** a styled button appears with primary theme color

#### Scenario: Button has loading state
- **WHEN** developer renders `<Button isLoading>Submit</Button>`
- **THEN** button shows spinner, text is hidden, click is disabled

#### Scenario: Button can be disabled
- **WHEN** developer renders `<Button disabled>Unavailable</Button>`
- **THEN** button is grayed out and unclickable

### Requirement: Card Component
The system SHALL provide a reusable Card component for content containers with padding, border, and shadow.

#### Scenario: Render basic card
- **WHEN** developer renders `<Card><h2>Title</h2><p>Content</p></Card>`
- **THEN** content is wrapped in a styled container with padding and border

#### Scenario: Card supports interactive hover effect
- **WHEN** user hovers over a Card with `interactive` prop
- **THEN** the card shadow increases (elevation effect)

### Requirement: Modal Component
The system SHALL provide a Modal dialog for overlays, confirmations, and forms.

#### Scenario: Open and close modal
- **WHEN** developer renders `<Modal isOpen={true} onClose={handler}><p>Content</p></Modal>`
- **THEN** a modal appears with backdrop, content, and close button

#### Scenario: Modal with title and actions
- **WHEN** developer renders `<Modal title="Confirm" actions={[okBtn, cancelBtn]}>`
- **THEN** modal displays title at top and action buttons at bottom

### Requirement: Form Components (Input, Textarea, Select)
The system SHALL provide form input components with validation styling, labels, and error messages.

#### Scenario: Render text input with label
- **WHEN** developer renders `<Input label="Email" type="email" />`
- **THEN** a labeled input field appears

#### Scenario: Show validation error
- **WHEN** developer renders `<Input error="Email is required" />`
- **THEN** input border turns red and error message appears below

#### Scenario: Select dropdown
- **WHEN** developer renders `<Select options={[{label: 'A', value: 1}]} />`
- **THEN** a dropdown appears with options

### Requirement: Tailwind CSS Theme System
The system SHALL use Tailwind CSS with custom theme variables for colors, spacing, and typography.

#### Scenario: Light mode colors
- **WHEN** user is in light mode
- **THEN** background is white, text is dark gray, accent is brand blue

#### Scenario: Dark mode colors
- **WHEN** user is in dark mode
- **THEN** background is dark gray, text is light, accent is bright blue

#### Scenario: Theme switching
- **WHEN** user clicks theme toggle
- **THEN** the `<html>` element class changes from `light` to `dark` (or vice versa)
- **THEN** all components automatically adapt their colors via Tailwind's `dark:` prefix

### Requirement: Responsive Design
The system SHALL support responsive layout using Tailwind breakpoints: mobile, tablet, desktop.

#### Scenario: Grid layout responsive
- **WHEN** component renders on mobile (< 640px)
- **THEN** layout is single-column
- **WHEN** component renders on tablet (640px - 1024px)
- **THEN** layout is 2 columns
- **WHEN** component renders on desktop (> 1024px)
- **THEN** layout is 3 columns

### Requirement: Alert / Toast Notification Component
The system SHALL provide dismissible toast notifications for success, error, warning, and info messages.

#### Scenario: Show success toast
- **WHEN** developer calls `showToast({ type: 'success', message: 'Saved!' })`
- **THEN** a green toast appears in top-right corner and auto-dismisses after 3 seconds

#### Scenario: Dismiss manual toast
- **WHEN** user clicks X button on toast
- **THEN** toast disappears immediately

### Requirement: Loading Skeleton
The system SHALL provide a skeleton/loader component for displaying content placeholders during data fetching.

#### Scenario: Show loading skeleton
- **WHEN** data is being fetched
- **THEN** skeleton appears as gray shimmer placeholders matching the final layout
