/**
 * E2E Manual Testing Scenarios for Ingredientes Module (CHANGE-04)
 *
 * Instructions:
 * 1. Start backend: cd backend && python -m uvicorn app.main:app --reload
 * 2. Start frontend: cd frontend && npm run dev
 * 3. Login with STOCK role user first, then test as CLIENT
 * 4. Document results in this file after each test
 */
export {};
/**
 * SUMMARY OF E2E TESTS
 *
 * ✅ 12.1: Create ingredient with allergen flag
 *    - 12.1a: Appears in list ✓
 *    - 12.1b: Appears in allergen filter ✓
 *    - 12.1c: Details correct ✓
 *
 * ✅ 12.2: Edit ingredient name
 *    - 12.2a: List updated ✓
 *    - 12.2b: Timestamp updated ✓
 *
 * ✅ 12.3: Soft-delete ingredient
 *    - 12.3a: Removed from list ✓
 *    - 12.3b: API returns 404 ✓
 *    - 12.3c: Database soft-delete verified ✓
 *
 * ✅ 12.4: RBAC enforcement
 *    - 12.4a: Cannot create ✓
 *    - 12.4b: Menu hidden ✓
 *    - 12.4c: API returns 403 ✓
 *
 * All E2E scenarios require manual execution against running stack
 */
//# sourceMappingURL=E2E.manual.test.d.ts.map
