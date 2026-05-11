/**
 * Zustand store factory with TypeScript generics
 * Provides consistent store creation with optional devtools integration
 */
import { StateCreator, StoreApi } from 'zustand';
export type Store<T> = StoreApi<T>;
/**
 * Create a typed Zustand store with devtools support
 * @param name Store name for devtools
 * @param initialState Initial state
 * @returns Zustand hook for the store
 */
export declare const createStore: <T extends Record<string, any>>(name: string, stateCreator: StateCreator<T, [], []>) => ((selector?: (state: T) => any) => any);
//# sourceMappingURL=createStore.d.ts.map