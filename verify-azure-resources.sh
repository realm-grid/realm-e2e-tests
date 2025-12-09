#!/bin/bash

# Azure Dev Resources Verification Script
# Checks connectivity to configured Azure resources

echo "╔════════════════════════════════════════════════════════════╗"
echo "║       Azure Dev Resources Connectivity Check              ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Load environment variables
if [ ! -f .env ]; then
    echo "✗ .env file not found!"
    exit 1
fi

export $(cat .env | grep -v '^#' | xargs)

echo "Testing Azure Dev Resources..."
echo ""

# Check Web App
echo "1. Web App (realm-dev-website-wa)"
WEB_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$WEB_URL")
if [ "$WEB_RESPONSE" -eq 200 ] || [ "$WEB_RESPONSE" -eq 301 ] || [ "$WEB_RESPONSE" -eq 302 ]; then
    echo "   ✓ Online (HTTP $WEB_RESPONSE)"
else
    echo "   ✗ Offline or error (HTTP $WEB_RESPONSE)"
    echo "   URL: $WEB_URL"
fi

# Check Function App
echo ""
echo "2. Function App (realm-dev-api-fa)"
FUNC_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$FUNCTIONS_URL")
if [ "$FUNC_RESPONSE" -eq 200 ] || [ "$FUNC_RESPONSE" -eq 301 ] || [ "$FUNC_RESPONSE" -eq 302 ] || [ "$FUNC_RESPONSE" -eq 404 ]; then
    echo "   ✓ Online (HTTP $FUNC_RESPONSE)"
else
    echo "   ✗ Offline or error (HTTP $FUNC_RESPONSE)"
    echo "   URL: $FUNCTIONS_URL"
fi

echo ""
echo "Environment Configuration:"
echo "   ENVIRONMENT: $ENVIRONMENT"
echo "   WEB_URL: $WEB_URL"
echo "   FUNCTIONS_URL: $FUNCTIONS_URL"
echo "   ADMIN_URL: $ADMIN_URL"
echo ""

# DNS resolution check
echo "DNS Resolution:"
WEB_HOST=$(echo $WEB_URL | sed 's|https://||' | cut -d'/' -f1)
FUNC_HOST=$(echo $FUNCTIONS_URL | sed 's|https://||' | cut -d'/' -f1)

echo "   Web: $WEB_HOST"
nslookup $WEB_HOST 2>/dev/null | grep -i "address" | tail -1

echo "   Function: $FUNC_HOST"
nslookup $FUNC_HOST 2>/dev/null | grep -i "address" | tail -1

echo ""
echo "✓ Verification complete!"
