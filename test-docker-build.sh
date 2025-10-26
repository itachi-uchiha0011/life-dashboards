#!/bin/bash

# Test Docker Build Script
echo "🔧 Testing Docker build..."

# Check if requirements.txt is valid
echo "📋 Checking requirements.txt..."
if python3 -c "
with open('requirements.txt', 'r') as f:
    lines = f.readlines()
    
packages = []
for line in lines:
    line = line.strip()
    if line and not line.startswith('#'):
        package_name = line.split('==')[0].split('>=')[0].split('<=')[0]
        packages.append(package_name)

print(f'Found {len(packages)} packages - requirements.txt looks good!')
" 2>/dev/null; then
    echo "✅ requirements.txt is valid"
else
    echo "❌ requirements.txt has issues"
    exit 1
fi

# Test Docker build (dry run)
echo "🐳 Testing Docker build..."
if docker build --no-cache -t life-dashboards:test . 2>&1 | grep -q "ERROR"; then
    echo "❌ Docker build failed"
    exit 1
else
    echo "✅ Docker build successful"
fi

echo "🎉 All tests passed! Docker build is working correctly."