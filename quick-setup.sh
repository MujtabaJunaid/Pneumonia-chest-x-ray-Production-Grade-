#!/bin/bash

# Pneumonia AI Detector - One-Click Setup Script
# Phase 4: Containerization with Docker Compose
#
# This script orchestrates the complete setup:
# 1. Build and start all Docker containers
# 2. Wait for PostgreSQL initialization
# 3. Create database tables
# 4. Generate 1,000 patients + 2,500 predictions (mock data)
# 5. Display access URLs

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Urdu messages
MESSAGES=(
    "ðŸš€ Ù†Ù…ÙˆÙ†ÛŒØ§ Ø§Û’ Ø¢Ø¦ÛŒ ÚˆÛŒÙ¹ÛŒÚ©Ù¹Ø± - Ø§ÛŒÚ© Ú©Ù„Ú© Ø³ÛŒÙ¹ Ø§Ù¾ Ø´Ø±ÙˆØ¹...|Starting Pneumonia AI Detector Setup..."
    "ðŸ“¦ ÚˆØ§Ú©Ø± Ú©Ù†Ù¹ÛŒÙ†Ø±Ø² Ø¨Ù† Ø±ÛÛ’ ÛÛŒÚº...|Building and starting Docker containers..."
    "â³ PostgreSQL Ú©Û’ Ù„ÛŒÛ’ Ø§Ù†ØªØ¸Ø§Ø± ÛÙˆ Ø±ÛØ§ ÛÛ’...|Waiting for PostgreSQL to initialize..."
    "âœ… ÚˆØ§Ú©Ø± Ú©Ù†Ù¹ÛŒÙ†Ø±Ø² Ø´Ø±ÙˆØ¹ ÛÙˆ Ú¯Ø¦Û’!|Docker containers started successfully!"
    "ðŸ“Š ÚˆÛŒÙ¹Ø§ Ø¨ÛŒØ³ Ù¹ÛŒØ¨Ù„Ø² Ø¨Ù† Ø±ÛÛŒ ÛÛŒÚº...|Creating database tables..."
    "âœ… ÚˆÛŒÙ¹Ø§ Ø¨ÛŒØ³ Ù¹ÛŒØ¨Ù„Ø² Ú©Ø§Ù…ÛŒØ§Ø¨ÛŒ Ø³Û’ Ø¨Ù†Ø§Ø¦Û’ Ú¯Ø¦Û’!|Database tables created successfully!"
    "ðŸ‘¥ Ù…Ø±ÛŒØ¶ Ø±ÛŒÚ©Ø§Ø±Úˆ Ø¨Ù† Ø±ÛÛ’ ÛÛŒÚº (1,000)...|Generating patient records (1,000)..."
    "ðŸ”¬ Ù¾ÛŒØ´ÛŒÙ† Ú¯ÙˆØ¦ÛŒ Ø±ÛŒÚ©Ø§Ø±Úˆ Ø¨Ù† Ø±ÛÛ’ ÛÛŒÚº (2,500)...|Generating prediction records (2,500)..."
    "âœ… ÚˆÛŒÙ¹Ø§ Ø¨ÛŒØ³ Ù…ÛŒÚº Ú©Ø§Ù…ÛŒØ§Ø¨ÛŒ Ø³Û’ ÚˆÛŒÙ¹Ø§ Ø¨Ú¾Ø± Ø¯ÛŒØ§ Ú¯ÛŒØ§!|Mock data successfully populated!"
    "ðŸŽ‰ Ø³ÛŒÙ¹ Ø§Ù¾ Ù…Ú©Ù…Ù„!|Setup Complete!"
)

# Function to print colored output
print_status() {
    local message=$1
    local status=$2
    
    case $status in
        "info")
            echo -e "${CYAN}Info: $message${NC}"
            ;;
        "success")
            echo -e "${GREEN}Success: $message${NC}"
            ;;
        "warning")
            echo -e "${YELLOW}Warning: $message${NC}"
            ;;
        "error")
            echo -e "${RED}Error: $message${NC}"
            ;;
    esac
}

# Function to print section header
print_header() {
    local message=$1
    echo ""
    echo -e "${BLUE}====================================================================="\u201d${NC}"
    echo -e "${BLUE}|${NC} $message"
    echo -e "${BLUE}====================================================================="\u201d${NC}"
    echo ""
}

# Function to check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_status "Docker is not installed. Please install Docker first." "error"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_status "Docker Compose is not installed. Please install Docker Compose first." "error"
        exit 1
    fi
}

# Function to start containers
start_containers() {
    print_header "ðŸš€ Ø¨Ù†Ø§Ø¤ Ø§ÙˆØ± Ø´Ø±ÙˆØ¹ Ú©Ø±ÛŒÚº | BUILD & START CONTAINERS"
    print_status "${MESSAGES[1]}" "info"
    
    # Change to project root directory
    cd "$(dirname "$0")"
    
    # Build and start containers in detached mode
    docker-compose down 2>/dev/null || true
    docker-compose up -d --build
    
    print_status "${MESSAGES[3]}" "success"
}

# Function to wait for PostgreSQL
wait_for_postgres() {
    print_header "â³ PostgreSQL Ø§Ù†ØªØ¸Ø§Ø± | WAIT FOR POSTGRESQL"
    print_status "${MESSAGES[2]}" "info"
    
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if docker-compose exec -T db pg_isready -U pneumonia_user -d pneumonia_detector > /dev/null 2>&1; then
            print_status "PostgreSQL ØªÛŒØ§Ø± ÛÛ’ | PostgreSQL is ready" "success"
            return 0
        fi
        
        attempt=$((attempt + 1))
        echo -ne "\r   Attempt $attempt/$max_attempts..."
        sleep 1
    done
    
    print_status "PostgreSQL Ø§Ø¨Ú¾ÛŒ ØªÚ© Ø´Ø±ÙˆØ¹ Ù†ÛÛŒÚº ÛÙˆØ§ | PostgreSQL failed to start" "error"
    return 1
}

# Function to create database tables
create_tables() {
    print_header "ðŸ“Š ÚˆÛŒÙ¹Ø§ Ø¨ÛŒØ³ Ù¹ÛŒØ¨Ù„Ø² | CREATE DATABASE TABLES"
    print_status "${MESSAGES[4]}" "info"
    
    # Run Python script inside backend container to create tables
    docker-compose exec -T backend python -c "
from app.database import create_tables, engine
create_tables()
print('âœ… ÚˆÛŒÙ¹Ø§ Ø¨ÛŒØ³ Ù¹ÛŒØ¨Ù„Ø² Ú©Ø§Ù…ÛŒØ§Ø¨ÛŒ Ø³Û’ Ø¨Ù†Ø§Ø¦Û’ Ú¯Ø¦Û’!')
"
    
    print_status "${MESSAGES[5]}" "success"
}

# Function to generate mock data
generate_mock_data() {
    print_header "ðŸŽ² Ù…ÚˆÚ¾ ÚˆÛŒÙ¹Ø§ | GENERATE MOCK DATA"
    print_status "${MESSAGES[6]}" "info"
    print_status "${MESSAGES[7]}" "info"
    
    # Run mock data generator inside backend container
    docker-compose exec -T backend python scripts/generate_mock_data.py
    
    print_status "${MESSAGES[8]}" "success"
}

# Function to display success information
display_success() {
    print_header "ðŸŽ‰ Ú©Ø§Ù…ÛŒØ§Ø¨ | SUCCESS!"
    
    echo ""
    echo -e "${GREEN}Ø³ÛŒÙ¹ Ø§Ù¾ Ù…Ú©Ù…Ù„! Setup Complete!${NC}"
    echo ""
    
    # Get container IPs and port info
    local frontend_port=80
    local backend_port=8000
    
    echo -e "${CYAN}â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•${NC}"
    echo -e "${CYAN}ðŸ“ Ø±Ø³Ø§Ø¦ÛŒ Ú©Û’ Ù„Ù†Ú©Ø³ | ACCESS LINKS:${NC}"
    echo -e "${CYAN}â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•${NC}"
    echo ""
    echo -e "${GREEN}ðŸŒ Frontend (React Dashboard):${NC}"
    echo -e "   http://localhost"
    echo -e "   http://localhost:${frontend_port}"
    echo ""
    echo -e "${GREEN}ðŸ“š Backend API Documentation:${NC}"
    echo -e "   http://localhost/api/docs"
    echo -e "   http://localhost:${backend_port}/docs"
    echo ""
    echo -e "${GREEN}ðŸ“Š Database Health:${NC}"
    echo -e "   http://localhost/health"
    echo ""
    echo -e "${CYAN}â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•${NC}"
    echo -e "${CYAN}ðŸ”§ Ù…ÙÛŒØ¯ Ú©Ù…Ø§Ù†ÚˆØ² | USEFUL COMMANDS:${NC}"
    echo -e "${CYAN}â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•${NC}"
    echo ""
    echo "  Ù„Ø§Ú¯Ø² Ø¯ÛŒÚ©Ú¾ÛŒÚº | View logs:"
    echo -e "  ${YELLOW}docker-compose logs -f backend${NC}"
    echo -e "  ${YELLOW}docker-compose logs -f frontend${NC}"
    echo ""
    echo "  Ú©Ù†Ù¹ÛŒÙ†Ø±Ø² Ú©Ùˆ Ø¨Ù†Ø¯ Ú©Ø±ÛŒÚº | Stop containers:"
    echo -e "  ${YELLOW}docker-compose down${NC}"
    echo ""
    echo "  ÚˆÛŒÙ¹Ø§ Ø¨ÛŒØ³ Ù…ÛŒÚº Ø¯Ø§Ø®Ù„ ÛÙˆÚº | Access database:"
    echo -e "  ${YELLOW}docker-compose exec db psql -U pneumonia_user -d pneumonia_detector${NC}"
    echo ""
    echo "  Ù…Ø±ÛŒØ¶ÙˆÚº Ú©ÛŒ ØªØ¹Ø¯Ø§Ø¯ Ú†ÛŒÚ© Ú©Ø±ÛŒÚº | Check patient count:"
    echo -e "  ${YELLOW}docker-compose exec db psql -U pneumonia_user -d pneumonia_detector -c 'SELECT COUNT(*) FROM patient;'${NC}"
    echo ""
    echo -e "${CYAN}â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•${NC}"
    echo ""
    
    # Default credentials
    echo -e "${YELLOW}ðŸ”‘ ÚˆÛŒÙ¹Ø§ Ø¨ÛŒØ³ Ú©Ø±ÛŒÚˆÙ†Ø´Ù„Ø² | DATABASE CREDENTIALS:${NC}"
    echo "   User: pneumonia_user"
    echo "   Password: pneumonia_secure_password_2026"
    echo "   Database: pneumonia_detector"
    echo ""
    
    # Data statistics
    echo -e "${YELLOW}ðŸ“ˆ Ù…ÙˆØ¬ÙˆØ¯ ÚˆÛŒÙ¹Ø§ | GENERATED DATA:${NC}"
    echo "   Patients: 1,000"
    echo "   Predictions: 2,500"
    echo "   Audit Logs: Auto-populated"
    echo ""
}

# Function to check current status
check_container_status() {
    print_header "ðŸ” Ú©Ù†Ù¹ÛŒÙ†Ø± Ø³Ù¹ÛŒÙ¹Ø³ | CONTAINER STATUS"
    
    echo -e "Ø§Ø³ØªØ¹Ù…Ø§Ù„ Ù…ÛŒÚº Ú©Ù†Ù¹ÛŒÙ†Ø±Ø² | Running Containers:"
    echo ""
    docker-compose ps
    echo ""
}

# Function to handle errors
handle_error() {
    local error_msg=$1
    echo ""
    print_status "Ø®Ø±Ø§Ø¨ÛŒ ÙˆØ§Ù‚Ø¹ ÛÙˆØ¦ÛŒ! Setup failed! Error: $error_msg" "error"
    echo ""
    print_status "Ù„Ø§Ú¯Ø² Ú†ÛŒÚ© Ú©Ø±ÛŒÚº | Check logs with: docker-compose logs" "info"
    exit 1
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

main() {
    print_header "ðŸ¥ Ù†Ù…ÙˆÙ†ÛŒØ§ Ø§Û’ Ø¢Ø¦ÛŒ ÚˆÛŒÙ¹ÛŒÚ©Ù¹Ø± | PNEUMONIA AI DETECTOR"
    print_header "ðŸš€ Ø§ÛŒÚ© Ú©Ù„Ú© Ø³ÛŒÙ¹ Ø§Ù¾ | ONE-CLICK SETUP"
    
    # Check prerequisites
    check_docker
    
    # Start containers
    start_containers || handle_error "Failed to start containers"
    
    # Wait for PostgreSQL
    wait_for_postgres || handle_error "PostgreSQL initialization timeout"
    
    # Give services a moment to fully initialize
    sleep 5
    
    # Create database tables
    create_tables || handle_error "Failed to create database tables"
    
    # Generate mock data
    generate_mock_data || handle_error "Failed to generate mock data"
    
    # Check container status
    check_container_status
    
    # Display success and access information
    display_success
}

# Run main function
main
