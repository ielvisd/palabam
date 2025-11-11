/**
 * Tests for useAuth composable
 * These tests ensure proper error handling and edge cases are covered
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'

// Mock Supabase client
const mockSupabaseClient = {
  auth: {
    getSession: vi.fn(),
    signInWithPassword: vi.fn(),
    signUp: vi.fn(),
    signOut: vi.fn(),
  },
  from: vi.fn(() => ({
    select: vi.fn(() => ({
      eq: vi.fn(() => ({
        single: vi.fn(),
        maybeSingle: vi.fn(),
      })),
      maybeSingle: vi.fn(),
    })),
    insert: vi.fn(() => ({
      select: vi.fn(() => ({
        single: vi.fn(),
      })),
    })),
  })),
}

// Mock useSupabaseClient
vi.mock('#imports', () => ({
  useSupabaseClient: () => mockSupabaseClient,
  useSupabaseUser: () => ({ value: null }),
  useRuntimeConfig: () => ({
    public: {
      apiUrl: 'http://localhost:8000',
    },
  }),
}))

describe('useAuth - getUserRole', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should handle user not existing in public.users table gracefully', async () => {
    // This is the exact error scenario the user encountered
    const mockError = {
      code: 'PGRST116',
      message: 'Cannot coerce the result to a single JSON object',
      details: 'The result contains 0 rows',
      hint: null,
    }

    // Mock session with user but no public.users record
    mockSupabaseClient.auth.getSession.mockResolvedValue({
      data: {
        session: {
          user: {
            id: '048458a7-73e2-4f45-aa06-e2a2f2b73237',
            email: 'test@example.com',
            user_metadata: {
              role: 'teacher',
              name: 'Test Teacher',
            },
          },
        },
      },
    })

    // Mock query that returns 0 rows (user doesn't exist in public.users)
    const mockMaybeSingle = vi.fn().mockResolvedValue({
      data: null,
      error: mockError,
    })

    mockSupabaseClient.from.mockReturnValue({
      select: vi.fn(() => ({
        eq: vi.fn(() => ({
          maybeSingle: mockMaybeSingle,
        })),
      })),
      insert: vi.fn(() => ({
        then: vi.fn((callback) => {
          // Simulate successful insert
          callback({ data: { role: 'teacher' }, error: null })
          return Promise.resolve({ data: { role: 'teacher' }, error: null })
        }),
      })),
    })

    // Import and test
    const { useAuth } = await import('./useAuth')
    const { getUserRole } = useAuth()

    // Should not throw, should handle gracefully
    const role = await getUserRole()

    // Should attempt to create user record from metadata
    expect(mockSupabaseClient.from).toHaveBeenCalledWith('users')
    // Should return role from metadata or created record
    expect(role).toBeTruthy()
  })

  it('should handle undefined user.id gracefully', async () => {
    mockSupabaseClient.auth.getSession.mockResolvedValue({
      data: {
        session: null,
      },
    })

    const { useAuth } = await import('./useAuth')
    const { getUserRole } = useAuth()

    const role = await getUserRole()

    // Should return null when no user ID available
    expect(role).toBeNull()
  })

  it('should use maybeSingle() instead of single() to avoid 406 errors', async () => {
    const mockMaybeSingle = vi.fn().mockResolvedValue({
      data: { role: 'teacher' },
      error: null,
    })

    mockSupabaseClient.from.mockReturnValue({
      select: vi.fn(() => ({
        eq: vi.fn(() => ({
          maybeSingle: mockMaybeSingle,
        })),
      })),
    })

    mockSupabaseClient.auth.getSession.mockResolvedValue({
      data: {
        session: {
          user: {
            id: 'test-id',
            email: 'test@example.com',
          },
        },
      },
    })

    const { useAuth } = await import('./useAuth')
    const { getUserRole } = useAuth()

    await getUserRole()

    // Verify maybeSingle() was called, not single()
    expect(mockMaybeSingle).toHaveBeenCalled()
  })
})

describe('useAuth - signInWithPassword', () => {
  it('should handle login errors gracefully', async () => {
    const mockError = {
      message: 'Invalid login credentials',
      status: 400,
    }

    mockSupabaseClient.auth.signInWithPassword.mockRejectedValue(mockError)

    const { useAuth } = await import('./useAuth')
    const { signInWithPassword } = useAuth()

    await expect(signInWithPassword('test@example.com', 'password')).rejects.toEqual(mockError)
  })
})

