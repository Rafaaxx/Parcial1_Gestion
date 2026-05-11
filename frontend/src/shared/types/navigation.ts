/**
 * Navigation and routing shared types
 */

import type React from 'react'

export type Role = 'ADMIN' | 'STOCK' | 'PEDIDOS' | 'CLIENT'

export interface NavItem {
  label: string
  path: string
  icon?: string
  roles?: Role[]
  children?: NavItem[]
}

export interface BreadcrumbItem {
  label: string
  path: string
  isActive?: boolean
}

export interface RouteConfig {
  path: string
  element: React.ReactNode
  protected?: boolean
  roles?: Role[]
  children?: RouteConfig[]
}
