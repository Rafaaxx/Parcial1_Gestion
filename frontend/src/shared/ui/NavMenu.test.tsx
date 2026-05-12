/**
 * Test suite for NavMenu navigation
 * Task 2.5: Verify Catalog link is present and accessible without login
 */

import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { NavMenu } from './NavMenu'

// Mock useAuth hook to simulate no user (logged out state)
vi.mock('@/shared/hooks/useAuth', () => ({
  useAuth: () => ({
    user: null,
    isAuthenticated: false,
  }),
}))

describe('NavMenu - Task 2.5: Catalog Navigation', () => {
  it('should render Catálogo link for public users (not logged in)', () => {
    render(
      <BrowserRouter>
        <NavMenu />
      </BrowserRouter>
    )

    const catalogLink = screen.getByRole('link', { name: /catálogo/i })
    expect(catalogLink).toBeInTheDocument()
  })

  it('should link Catálogo to /productos path', () => {
    render(
      <BrowserRouter>
        <NavMenu />
      </BrowserRouter>
    )

    const catalogLink = screen.getByRole('link', { name: /catálogo/i }) as HTMLAnchorElement
    expect(catalogLink.href).toContain('/productos')
  })

  it('should render Catálogo link in mobile menu', () => {
    render(
      <BrowserRouter>
        <NavMenu isMobile={true} />
      </BrowserRouter>
    )

    const catalogLink = screen.getByRole('link', { name: /catálogo/i })
    expect(catalogLink).toBeInTheDocument()
  })
})
