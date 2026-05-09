/**
 * Storage utility functions
 */
const PREFIX = 'food-store:';
/**
 * Get item from localStorage with type safety
 */
export function getFromStorage(key, defaultValue) {
    try {
        const fullKey = `${PREFIX}${key}`;
        const item = localStorage.getItem(fullKey);
        return item ? JSON.parse(item) : defaultValue || null;
    }
    catch (error) {
        console.error(`Error reading from storage: ${key}`, error);
        return defaultValue || null;
    }
}
/**
 * Set item to localStorage with type safety
 */
export function setToStorage(key, value) {
    try {
        const fullKey = `${PREFIX}${key}`;
        localStorage.setItem(fullKey, JSON.stringify(value));
    }
    catch (error) {
        console.error(`Error writing to storage: ${key}`, error);
    }
}
/**
 * Remove item from localStorage
 */
export function removeFromStorage(key) {
    try {
        const fullKey = `${PREFIX}${key}`;
        localStorage.removeItem(fullKey);
    }
    catch (error) {
        console.error(`Error removing from storage: ${key}`, error);
    }
}
/**
 * Clear all food-store items from localStorage
 */
export function clearStorage() {
    try {
        const keys = Object.keys(localStorage).filter((key) => key.startsWith(PREFIX));
        keys.forEach((key) => localStorage.removeItem(key));
    }
    catch (error) {
        console.error('Error clearing storage', error);
    }
}
//# sourceMappingURL=storage.js.map