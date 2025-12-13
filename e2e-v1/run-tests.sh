#!/bin/bash

# RealmGrid E2E Test Runner (v1)
# 
# This script:
# 1. Installs dependencies if needed
# 2. Starts the web server on port 5005
# 3. Starts the Azure Functions server on port 7071
# 4. Runs Playwright tests
# 5. Cleans up servers after tests

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Configuration
WEB_PORT=5005
FUNCTIONS_PORT=7071
ADMIN_PORT=4321

# PIDs for cleanup
WEB_PID=""
FUNCTIONS_PID=""

echo -e "${BLUE}🎭 RealmGrid E2E Tests (v1)${NC}"
echo "======================================"
echo ""
echo -e "${YELLOW}[DEBUG]${NC} Script directory: $SCRIPT_DIR"
echo -e "${YELLOW}[DEBUG]${NC} Repo root: $REPO_ROOT"
echo ""

# Cleanup function
cleanup() {
    echo ""
    echo -e "${BLUE}🧹 Cleaning up...${NC}"
    
    if [ -n "$WEB_PID" ]; then
        echo -e "${YELLOW}[DEBUG]${NC} Stopping web server (PID: $WEB_PID)"
        kill $WEB_PID 2>/dev/null || true
    fi
    
    if [ -n "$FUNCTIONS_PID" ]; then
        echo -e "${YELLOW}[DEBUG]${NC} Stopping functions server (PID: $FUNCTIONS_PID)"
        kill $FUNCTIONS_PID 2>/dev/null || true
    fi
    
    # Kill any remaining processes on our ports
    lsof -ti:$WEB_PORT | xargs kill -9 2>/dev/null || true
    lsof -ti:$FUNCTIONS_PORT | xargs kill -9 2>/dev/null || true
    
    echo -e "${GREEN}✅ Cleanup complete${NC}"
}

# Set up trap for cleanup on exit
trap cleanup EXIT INT TERM

# Navigate to test directory
cd "$SCRIPT_DIR"

# Check and install node modules
if [ ! -d "node_modules" ]; then
    echo -e "${BLUE}📦 Installing E2E test dependencies...${NC}"
    npm install
    echo ""
fi

# Check if Playwright browsers are installed
if [ ! -d "$HOME/.cache/ms-playwright" ]; then
    echo -e "${BLUE}🌐 Installing Playwright browsers...${NC}"
    npx playwright install chromium
    echo ""
fi

# Parse command line arguments
HEADED=""
DEBUG=""
GREP=""
SKIP_SERVERS=false
SHOW_REPORT=false
UI_MODE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --headed)
            HEADED="--headed"
            shift
            ;;
        --debug)
            DEBUG="--debug"
            shift
            ;;
        --ui)
            UI_MODE=true
            shift
            ;;
        --skip-servers)
            SKIP_SERVERS=true
            shift
            ;;
        --api)
            GREP="--grep=API"
            shift
            ;;
        --web)
            GREP="--grep=Web"
            shift
            ;;
        --admin)
            GREP="--grep=Admin"
            shift
            ;;
        --flow)
            GREP="--grep=E2E"
            shift
            ;;
        --report)
            SHOW_REPORT=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --headed        Run tests with visible browser"
            echo "  --debug         Run tests in debug mode"
            echo "  --ui            Open Playwright UI mode"
            echo "  --skip-servers  Don't start servers (use existing)"
            echo "  --api           Run only API tests"
            echo "  --web           Run only web app tests"
            echo "  --admin         Run only admin tests"
            echo "  --flow          Run only complete E2E flow tests"
            echo "  --report        Show test report after run"
            echo "  -h, --help      Show this help"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to wait for a server to be ready
wait_for_server() {
    local url=$1
    local name=$2
    local max_attempts=30
    local attempt=1
    
    echo -e "${YELLOW}[DEBUG]${NC} Waiting for $name at $url..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s --max-time 2 "$url" > /dev/null 2>&1; then
            echo -e "${GREEN}  ✅ $name is ready${NC}"
            return 0
        fi
        echo -e "${YELLOW}[DEBUG]${NC}   Attempt $attempt/$max_attempts..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo -e "${RED}  ❌ $name failed to start${NC}"
    return 1
}

# Start servers if not skipped
if [ "$SKIP_SERVERS" = false ]; then
    echo -e "${BLUE}🚀 Starting servers...${NC}"
    echo ""
    
    # Check if ports are already in use
    if check_port $WEB_PORT; then
        echo -e "${YELLOW}[DEBUG]${NC} Port $WEB_PORT already in use, killing existing process..."
        lsof -ti:$WEB_PORT | xargs kill -9 2>/dev/null || true
        sleep 1
    fi
    
    if check_port $FUNCTIONS_PORT; then
        echo -e "${YELLOW}[DEBUG]${NC} Port $FUNCTIONS_PORT already in use, killing existing process..."
        lsof -ti:$FUNCTIONS_PORT | xargs kill -9 2>/dev/null || true
        sleep 1
    fi
    
    # Start the web server on port 5005
    echo -e "${BLUE}Starting web server on port $WEB_PORT...${NC}"
    if [ -d "$REPO_ROOT/realm-web" ]; then
        cd "$REPO_ROOT/realm-web"
        echo -e "${YELLOW}[DEBUG]${NC} Web server directory: $(pwd)"
        
        # Try to start with PORT env var
        PORT=$WEB_PORT npm run dev > "$SCRIPT_DIR/test-results/web-server.log" 2>&1 &
        WEB_PID=$!
        echo -e "${YELLOW}[DEBUG]${NC} Web server started with PID: $WEB_PID"
        cd "$SCRIPT_DIR"
    else
        echo -e "${YELLOW}[DEBUG]${NC} realm-web not found, trying realm-admin..."
        cd "$REPO_ROOT/realm-admin"
        echo -e "${YELLOW}[DEBUG]${NC} Admin server directory: $(pwd)"
        
        PORT=$WEB_PORT npm run dev > "$SCRIPT_DIR/test-results/web-server.log" 2>&1 &
        WEB_PID=$!
        echo -e "${YELLOW}[DEBUG]${NC} Web server started with PID: $WEB_PID"
        cd "$SCRIPT_DIR"
    fi
    
    # Start Azure Functions server
    echo -e "${BLUE}Starting Azure Functions on port $FUNCTIONS_PORT...${NC}"
    cd "$REPO_ROOT/realm-functions"
    echo -e "${YELLOW}[DEBUG]${NC} Functions directory: $(pwd)"
    
    # Install Python dependencies if needed
    if [ -f "requirements.txt" ]; then
        if [ ! -d ".venv" ]; then
            echo -e "${YELLOW}[DEBUG]${NC} Creating Python virtual environment..."
            python3 -m venv .venv
        fi
        source .venv/bin/activate 2>/dev/null || true
        pip install -r requirements.txt -q 2>/dev/null || true
    fi
    
    func start --port $FUNCTIONS_PORT > "$SCRIPT_DIR/test-results/functions-server.log" 2>&1 &
    FUNCTIONS_PID=$!
    echo -e "${YELLOW}[DEBUG]${NC} Functions started with PID: $FUNCTIONS_PID"
    cd "$SCRIPT_DIR"
    
    # Wait for servers to be ready
    echo ""
    echo -e "${BLUE}Waiting for servers to be ready...${NC}"
    
    # Create test-results directory if it doesn't exist
    mkdir -p test-results
    
    wait_for_server "http://localhost:$WEB_PORT" "Web Server" || {
        echo -e "${YELLOW}[DEBUG]${NC} Web server log:"
        tail -20 test-results/web-server.log 2>/dev/null || echo "No log available"
        echo ""
    }
    
    wait_for_server "http://localhost:$FUNCTIONS_PORT/api/health_check" "Azure Functions" || {
        echo -e "${YELLOW}[DEBUG]${NC} Functions server log:"
        tail -20 test-results/functions-server.log 2>/dev/null || echo "No log available"
        echo ""
    }
    
    echo ""
else
    echo -e "${YELLOW}[DEBUG]${NC} Skipping server startup (--skip-servers)"
    echo ""
fi

# Run the tests
if [ "$UI_MODE" = true ]; then
    echo -e "${BLUE}🎭 Opening Playwright UI...${NC}"
    npx playwright test --ui
else
    echo -e "${BLUE}🧪 Running Playwright tests...${NC}"
    echo -e "${YELLOW}[DEBUG]${NC} Command: npx playwright test $HEADED $DEBUG $GREP"
    echo ""
    
    # Set environment variables
    export WEB_URL="http://localhost:$WEB_PORT"
    export FUNCTIONS_URL="http://localhost:$FUNCTIONS_PORT"
    export ADMIN_URL="http://localhost:$ADMIN_PORT"
    
    # Run tests
    npx playwright test $HEADED $DEBUG $GREP
    
    TEST_EXIT_CODE=$?
    
    echo ""
    if [ $TEST_EXIT_CODE -eq 0 ]; then
        echo -e "${GREEN}✅ All tests passed!${NC}"
    else
        echo -e "${RED}❌ Some tests failed (exit code: $TEST_EXIT_CODE)${NC}"
    fi
fi

# Show report if requested
if [ "$SHOW_REPORT" = true ]; then
    echo ""
    echo -e "${BLUE}📊 Opening test report...${NC}"
    npx playwright show-report playwright-report
fi

echo ""
echo -e "${BLUE}📊 Test artifacts:${NC}"
echo "  - Screenshots: test-results/"
echo "  - Videos: test-results/"
echo "  - HTML Report: playwright-report/"
echo ""
echo -e "${YELLOW}To view the report:${NC} npx playwright show-report playwright-report"
