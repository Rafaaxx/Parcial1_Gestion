/**
 * Zustand store factory with TypeScript generics
 * Provides consistent store creation with optional devtools integration
 */
import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
/**
 * Create a typed Zustand store with devtools support
 * @param name Store name for devtools
 * @param initialState Initial state
 * @returns Zustand hook for the store
 */
export const createStore = (name, stateCreator) => {
    return create(devtools(stateCreator, {
        name,
        enabled: import.meta.env.VITE_DEBUG === 'true',
    }));
};
//# sourceMappingURL=createStore.js.map