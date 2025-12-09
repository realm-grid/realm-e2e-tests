#!/bin/bash

# Test Runner Script for Realm Grid E2E Tests
# This script runs tests against Azure Dev Resources

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     Realm Grid E2E Tests - Azure Dev Environment        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${RED}✗ .env file not found!${NC}"
    echo "Please create .env file from .env.example"
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

echo -e "${GREEN}✓ Environment loaded${NC}"
echo -e "  Environment: ${BLUE}${ENVIRONMENT}${NC}"
echo -e "  Web URL: ${BLUE}${WEB_URL}${NC}"
echo -e "  Functions URL: ${BLUE}${FUNCTIONS_URL}${NC}"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python installed${NC}"
echo ""

# Check if virtual environment exists, if not create it
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo ""

# Install/upgrade dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -q --upgrade pip
pip install -q -r requirements.txt
pip install -q playwright
python3 -m playwright install chromium
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# Run tests based on argument
if [ -z "$1" ]; then
    # Run all web tests
    echo -e "${BLUE}Running all web tests...${NC}"
    echo -e "${YELLOW}Command: behave features/web/${NC}"
    echo ""
    behave features/web/ --tags=-@wip,-@skip
elif [ "$1" = "smoke" ]; then
    # Run smoke tests
    echo -e "${BLUE}Running smoke tests...${NC}"
    echo -e "${YELLOW}Command: behave features/web/ --tags=@smoke${NC}"
    echo ""
    behave features/web/ --tags=@smoke
elif [ "$1" = "auth" ]; then
    # Run authentication tests
    echo -e "${BLUE}Running authentication tests...${NC}"
    echo -e "${YELLOW}Command: behave features/web/ --tags=@authentication${NC}"
    echo ""
    behave features/web/ --tags=@authentication
elif [ "$1" = "billing" ]; then
    # Run billing tests
    echo -e "${BLUE}Running billing tests...${NC}"
    echo -e "${YELLOW}Command: behave features/web/ --tags=@billing${NC}"
    echo ""
    behave features/web/ --tags=@billing
elif [ "$1" = "report" ]; then
    # Generate HTML report
    echo -e "${BLUE}Generating test report...${NC}"
    behave features/web/ --tags=-@wip,-@skip --format=html --outfile=reports/test-report.html
    echo -e "${GREEN}✓ Report generated: reports/test-report.html${NC}"
else
    echo -e "${YELLOW}Usage: $0 [smoke|auth|billing|report|all]${NC}"
    echo ""
    echo "Options:"
    echo "  (no args)  Run all web tests"
    echo "  smoke      Run smoke tests only"
    echo "  auth       Run authentication tests only"
    echo "  billing    Run billing tests only"
    echo "  report     Generate HTML test report"
    echo ""
    exit 1
fi

echo ""
echo -e "${GREEN}✓ Tests completed${NC}"
