#!/bin/bash
# Accounts Module Test Runner
# Run Playwright tests for the Accounts module

echo "=================================="
echo "Accounts Module Test Runner"
echo "=================================="
echo ""

# Check if Django server is running
if ! curl -s http://localhost:8000 > /dev/null; then
    echo "⚠️  Django server not running!"
    echo "Please start server with: python manage.py runserver"
    echo ""
    read -p "Start server now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Starting Django server..."
        python manage.py runserver &
        SERVER_PID=$!
        echo "Server started with PID: $SERVER_PID"
        sleep 3
    else
        echo "Exiting..."
        exit 1
    fi
fi

echo "Select test suite to run:"
echo "1. Smoke tests (15 tests, ~30 seconds)"
echo "2. Comprehensive tests (~90 tests, ~5 minutes)"
echo "3. All Accounts tests"
echo "4. Run with browser visible (headed mode)"
echo ""
read -p "Choice (1-4): " choice

case $choice in
    1)
        echo "Running smoke tests..."
        pytest tests/playwright/test_accounts_smoke.py -v
        ;;
    2)
        echo "Running comprehensive tests..."
        pytest tests/playwright/test_accounts_comprehensive.py -v
        ;;
    3)
        echo "Running all Accounts tests..."
        pytest tests/playwright/test_accounts*.py -v
        ;;
    4)
        echo "Running smoke tests in headed mode..."
        pytest tests/playwright/test_accounts_smoke.py -v --headed
        ;;
    *)
        echo "Invalid choice. Running smoke tests by default..."
        pytest tests/playwright/test_accounts_smoke.py -v
        ;;
esac

# Kill server if we started it
if [ ! -z "$SERVER_PID" ]; then
    echo ""
    read -p "Stop Django server? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kill $SERVER_PID
        echo "Server stopped."
    fi
fi

echo ""
echo "=================================="
echo "Test run complete!"
echo "=================================="
