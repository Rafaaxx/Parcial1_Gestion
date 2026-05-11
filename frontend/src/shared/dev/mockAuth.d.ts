/**
 * Development helper to mock authentication without login
 * Use this in the browser console during development:
 *
 * import { mockAuthAsStockUser } from '@/shared/dev/mockAuth'
 * mockAuthAsStockUser()
 *
 * Then navigate to /admin/ingredientes
 */
/**
 * Mock authentication as a STOCK user for testing inventory management
 */
export declare function mockAuthAsStockUser(): void;
/**
 * Mock authentication as an ADMIN user for testing all features
 */
export declare function mockAuthAsAdminUser(): void;
/**
 * Mock authentication as a CLIENT (no privileged access)
 */
export declare function mockAuthAsClientUser(): void;
/**
 * Clear auth state (logout)
 */
export declare function clearMockAuth(): void;
//# sourceMappingURL=mockAuth.d.ts.map
