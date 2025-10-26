#!/bin/bash

# Test Docker syntax
echo "🔧 Testing Docker syntax..."

# Test main Dockerfile
echo "📋 Testing Dockerfile..."
if docker build --no-cache -f Dockerfile -t test-main . > /dev/null 2>&1; then
    echo "✅ Dockerfile syntax is correct"
else
    echo "❌ Dockerfile has syntax errors"
    docker build --no-cache -f Dockerfile -t test-main . 2>&1 | grep -A 5 -B 5 "error"
fi

# Test Render Dockerfile
echo "📋 Testing Dockerfile.render..."
if docker build --no-cache -f Dockerfile.render -t test-render . > /dev/null 2>&1; then
    echo "✅ Dockerfile.render syntax is correct"
else
    echo "❌ Dockerfile.render has syntax errors"
    docker build --no-cache -f Dockerfile.render -t test-render . 2>&1 | grep -A 5 -B 5 "error"
fi

echo "🎉 Docker syntax test completed!"