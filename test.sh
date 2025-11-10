#!/bin/bash

# Palabam Quick Test Script
# Tests the API endpoints

echo "🧪 Palabam API Test Suite"
echo "=========================="
echo ""

# Check if backend is running
echo "Checking if backend is running..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is running"
else
    echo "❌ Backend is not running!"
    echo "   Start it with: cd backend && python -m uvicorn main:app --reload"
    exit 1
fi

echo ""
echo "Running API tests..."
echo ""

# Run the test script
cd backend/scripts
python3 test_api.py

echo ""
echo "=========================="
echo "Test complete!"
echo ""
echo "Next steps:"
echo "1. Test the frontend manually at http://localhost:3000"
echo "2. Follow the TESTING_GUIDE.md for detailed test scenarios"
echo "3. Check browser console for any frontend errors"

