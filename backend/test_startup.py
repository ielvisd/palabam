#!/usr/bin/env python3
"""
Minimal test to verify Python and uvicorn work
"""
import sys
import os

print(f"Python version: {sys.version}", flush=True)
print(f"Working directory: {os.getcwd()}", flush=True)
print(f"Files in directory: {os.listdir('.')}", flush=True)
print(f"PORT env var: {os.getenv('PORT', 'not set')}", flush=True)
print(f"SUPABASE_URL env var: {os.getenv('SUPABASE_URL', 'not set')[:30]}...", flush=True)

print("\nTrying to import FastAPI...", flush=True)
try:
    from fastapi import FastAPI
    print("✓ FastAPI imported successfully", flush=True)
except Exception as e:
    print(f"✗ Failed to import FastAPI: {e}", flush=True)
    sys.exit(1)

print("\nTrying to import uvicorn...", flush=True)
try:
    import uvicorn
    print("✓ uvicorn imported successfully", flush=True)
except Exception as e:
    print(f"✗ Failed to import uvicorn: {e}", flush=True)
    sys.exit(1)

print("\nTrying to import main module...", flush=True)
try:
    import main
    print("✓ main module imported successfully", flush=True)
    print(f"✓ App object exists: {hasattr(main, 'app')}", flush=True)
except Exception as e:
    print(f"✗ Failed to import main: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✓ All imports successful!", flush=True)
print("Starting uvicorn...", flush=True)

# Start uvicorn
port = int(os.getenv('PORT', '8080'))
uvicorn.run(main.app, host="0.0.0.0", port=port, log_level="info")

