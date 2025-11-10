# Environment Variables Setup Guide

## Overview

You need **three different Supabase credentials** in different places:

1. **Anon/Public Key** - Safe for client-side (frontend)
2. **Service Role Key** - Private, for server-side operations (backend)
3. **Access Token** - For MCP admin operations (root)

## What Goes Where

### 1. Frontend (`frontend/.env`)
**Purpose**: Client-side Supabase operations (respects Row Level Security)

- ✅ `NUXT_PUBLIC_SUPABASE_URL` - Your project URL
- ✅ `NUXT_PUBLIC_SUPABASE_ANON_KEY` - **Anon/Public key** (safe to expose to browser)
- ❌ **DO NOT** put service role key here (security risk!)

**Why**: The anon key is safe for client-side use because it respects RLS policies.

### 2. Backend (`backend/.env`)
**Purpose**: Server-side operations that may bypass RLS

- ✅ `SUPABASE_URL` - Your project URL (same as frontend)
- ✅ `SUPABASE_KEY` - **Service Role Key** (private, bypasses RLS)
- ❌ **DO NOT** put anon key here (won't work for admin operations)

**Why**: The service role key allows the backend to perform operations that bypass RLS, like creating user records, bulk operations, etc.

### 3. Root (`.env` for MCP)
**Purpose**: Cursor's Supabase MCP server for database migrations

- ✅ `SUPABASE_URL` - Your project URL (same as frontend/backend)
- ✅ `SUPABASE_ACCESS_TOKEN` - **Service Role Key** (same value as backend's `SUPABASE_KEY`)

**Why**: MCP needs admin privileges to apply migrations and manage the database.

## Summary

| Variable | Frontend | Backend | Root (MCP) |
|----------|----------|---------|------------|
| **URL** | ✅ (NUXT_PUBLIC_SUPABASE_URL) | ✅ (SUPABASE_URL) | ✅ (SUPABASE_URL) |
| **Anon Key** | ✅ (NUXT_PUBLIC_SUPABASE_ANON_KEY) | ❌ | ❌ |
| **Service Key** | ❌ | ✅ (SUPABASE_KEY) | ✅ (SUPABASE_ACCESS_TOKEN) |

## Where to Find These

1. Go to your Supabase project: https://app.supabase.com/project/_/settings/api
2. **Project URL**: Found at the top (e.g., `https://xxxxx.supabase.co`)
3. **Anon Key**: Under "Project API keys" → `anon` `public` key
4. **Service Role Key**: Under "Project API keys" → `service_role` `secret` key ⚠️ Keep this secret!

## Quick Setup

```bash
# 1. Copy example files
cp frontend/.env.example frontend/.env
cp backend/.env.example backend/.env
cp .env.example .env

# 2. Fill in the values:
# - Frontend: URL + anon key
# - Backend: URL + service role key
# - Root: URL + service role key (same as backend)
```

## Security Notes

- ⚠️ **Never commit `.env` files** (they're in `.gitignore`)
- ⚠️ **Never expose service role key** to the frontend
- ✅ **Anon key is safe** for client-side use (respects RLS)
- ✅ **Service role key** should only be in backend/root (server-side only)
