/**
 * Vitest setup file
 * Configures test environment and global mocks
 */

import { vi } from 'vitest'

// Mock Nuxt composables
global.useSupabaseClient = vi.fn()
global.useSupabaseUser = vi.fn()
global.useRuntimeConfig = vi.fn()

