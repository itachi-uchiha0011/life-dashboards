#!/bin/bash

# Docker Run Script for Life Dashboards
# Usage: ./docker-run.sh [dev|prod|compose]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if .env files exist
check_env_files() {
    if [ ! -f ".env" ]; then
        print_warning ".env file not found. Creating from .env.example..."
        cp .env.example .env
        print_warning "Please update .env file with your configuration"
    fi
    
    if [ ! -f ".env.production" ]; then
        print_warning ".env.production file not found. Creating from .env.example..."
        cp .env.example .env.production
        print_warning "Please update .env.production file with your production configuration"
    fi
}

# Development mode
run_dev() {
    print_status "Starting development environment..."
    check_env_files
    
    # Build development image
    docker build -f Dockerfile.dev -t life-dashboards:dev .
    
    # Run development container
    docker run -d \
        --name life-dashboards-dev \
        -p 5000:5000 \
        --env-file .env \
        -v $(pwd):/app \
        -v /app/__pycache__ \
        life-dashboards:dev
    
    print_status "Development server started at http://localhost:5000"
    print_status "To view logs: docker logs -f life-dashboards-dev"
    print_status "To stop: docker stop life-dashboards-dev"
}

# Production mode
run_prod() {
    print_status "Starting production environment..."
    check_env_files
    
    # Build production image
    docker build -t life-dashboards:prod .
    
    # Run production container
    docker run -d \
        --name life-dashboards-prod \
        -p 8080:8080 \
        --env-file .env.production \
        life-dashboards:prod
    
    print_status "Production server started at http://localhost:8080"
    print_status "To view logs: docker logs -f life-dashboards-prod"
    print_status "To stop: docker stop life-dashboards-prod"
}

# Docker Compose mode
run_compose() {
    print_status "Starting with Docker Compose..."
    check_env_files
    
    # Start services
    docker-compose up -d
    
    print_status "All services started!"
    print_status "Web app: http://localhost:8080"
    print_status "Database: localhost:5432"
    print_status "To view logs: docker-compose logs -f"
    print_status "To stop: docker-compose down"
}

# Docker Compose development mode
run_compose_dev() {
    print_status "Starting development with Docker Compose..."
    check_env_files
    
    # Start development services
    docker-compose -f docker-compose.dev.yml up -d
    
    print_status "Development services started!"
    print_status "Web app: http://localhost:5000"
    print_status "Database: localhost:5432"
    print_status "To view logs: docker-compose -f docker-compose.dev.yml logs -f"
    print_status "To stop: docker-compose -f docker-compose.dev.yml down"
}

# Clean up containers
cleanup() {
    print_status "Cleaning up containers..."
    docker stop life-dashboards-dev life-dashboards-prod 2>/dev/null || true
    docker rm life-dashboards-dev life-dashboards-prod 2>/dev/null || true
    docker-compose down 2>/dev/null || true
    docker-compose -f docker-compose.dev.yml down 2>/dev/null || true
    print_status "Cleanup completed!"
}

# Main script
case "${1:-help}" in
    "dev")
        run_dev
        ;;
    "prod")
        run_prod
        ;;
    "compose")
        run_compose
        ;;
    "compose-dev")
        run_compose_dev
        ;;
    "cleanup")
        cleanup
        ;;
    "help"|*)
        echo "Usage: $0 [dev|prod|compose|compose-dev|cleanup]"
        echo ""
        echo "Commands:"
        echo "  dev         - Run development container with hot reload"
        echo "  prod        - Run production container"
        echo "  compose     - Run with Docker Compose (production)"
        echo "  compose-dev - Run with Docker Compose (development)"
        echo "  cleanup     - Stop and remove all containers"
        echo "  help        - Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0 dev          # Development mode"
        echo "  $0 prod         # Production mode"
        echo "  $0 compose      # Full stack with database"
        echo "  $0 compose-dev  # Development with database"
        ;;
esac