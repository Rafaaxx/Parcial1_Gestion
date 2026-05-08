/**
 * Storage utility functions
 */
/**
 * Get item from localStorage with type safety
 */
export declare function getFromStorage<T>(key: string, defaultValue?: T): T | null;
/**
 * Set item to localStorage with type safety
 */
export declare function setToStorage<T>(key: string, value: T): void;
/**
 * Remove item from localStorage
 */
export declare function removeFromStorage(key: string): void;
/**
 * Clear all food-store items from localStorage
 */
export declare function clearStorage(): void;
//# sourceMappingURL=storage.d.ts.map