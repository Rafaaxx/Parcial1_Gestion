/**
 * Zustand store factory with TypeScript generics
 * Provides consistent store creation with optional devtools integration
 */

import { create, StateCreator, StoreApi } from 'zustand'
import { devtools } from 'zustand/middleware'

export type Store<T> = StoreApi<T>

/**
 * Create a typed Zustand store with devtools support
 * @param name Store name for devtools
 * @param initialState Initial state
 * @returns Zustand hook for the store
 */
export const createStore = <T extends Record<string, any>>(
  name: string,
  stateCreator: StateCreator<T, [], []>,
): ((selector?: (state: T) => any) => any) => {
  return create<T, [['zustand/devtools', never]]>(
    devtools(stateCreator as any, {
      name,
      enabled: import.meta.env.VITE_DEBUG === 'true',
    }) as any
  )
}
