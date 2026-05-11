## ADDED Requirements

### Requirement: Unauthorized page displays 403 error

The system SHALL display an Unauthorized (403 Forbidden) page when a user attempts to access a route they don't have permission for.

#### Scenario: User sees 403 page on role mismatch
- **WHEN** a CLIENT user navigates to /app/admin/users (requires role ADMIN)
- **THEN** ProtectedRoute detects the role mismatch
- **THEN** Unauthorized component is rendered showing a 403 error page

#### Scenario: Unauthorized page shows clear message
- **WHEN** Unauthorized page is rendered
- **THEN** page displays: "403 - Forbidden", "You don't have permission to access this page", and a description of what they tried to access
- **THEN** page is styled consistently with the application design

### Requirement: Unauthorized page provides navigation options

The system SHALL provide clear next steps for the user on the Unauthorized page.

#### Scenario: Unauthorized page has button to go to dashboard
- **WHEN** user is on the Unauthorized page
- **THEN** there is a prominent button labeled "Go to Dashboard" or "Go Home"
- **THEN** clicking the button navigates to /app/dashboard or /app

#### Scenario: Unauthorized page has button to go back
- **WHEN** user is on the Unauthorized page
- **THEN** there is a button labeled "Go Back" that calls window.history.back()
- **THEN** user is returned to the previous page

#### Scenario: Unauthorized page shows contact admin link
- **WHEN** user is on the Unauthorized page
- **THEN** there is a link or message saying "If you believe this is an error, contact an administrator"
- **THEN** optional: link to /support or /contact page

### Requirement: Unauthorized page is responsive

The system SHALL style the Unauthorized page to be responsive on all device sizes.

#### Scenario: Unauthorized page displays correctly on mobile
- **WHEN** Unauthorized page is viewed on mobile (< 768px viewport width)
- **THEN** page content is readable without horizontal scrolling
- **THEN** buttons are easily tappable (minimum 44px height)
- **THEN** text size is readable (minimum 16px font)

#### Scenario: Unauthorized page displays correctly on desktop
- **WHEN** Unauthorized page is viewed on desktop (>= 768px)
- **THEN** page is centered and well-proportioned
- **THEN** maximum width is reasonable (e.g., 600px max-width)

### Requirement: Unauthorized page includes HTTP status code

The system SHALL clearly display the HTTP 403 status code so users understand it's a permissions issue.

#### Scenario: 403 status code is prominent
- **WHEN** Unauthorized page renders
- **THEN** "403" is displayed prominently (e.g., large heading)
- **THEN** status code is accompanied by short explanation (e.g., "Forbidden")
