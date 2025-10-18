#!/bin/bash

# Quick Start Script for Knowledge Transfer Bot
# This script provides a guided setup for the KT-AI application

echo "🚀 Knowledge Transfer Bot - Quick Start"
echo "======================================"
echo ""

# Check if running in the correct directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

echo "📋 Setup Options:"
echo "1. Local Development (PostgreSQL + Redis + Docker)"
echo "2. Azure Cloud Setup (Azure OpenAI + Azure AI Search)"
echo "3. Hybrid Setup (Local + Azure)"
echo ""

read -p "Select setup option (1-3): " choice

case $choice in
    1)
        echo "🏠 Setting up Local Development Environment..."
        echo ""
        echo "This will:"
        echo "- Start PostgreSQL and Redis containers"
        echo "- Use local ChromaDB for vector search"
        echo "- Use OpenAI API for LLM"
        echo ""
        read -p "Continue? (y/n): " confirm
        if [ "$confirm" = "y" ]; then
            echo "Starting local setup..."
            ./setup.sh
        fi
        ;;
    2)
        echo "☁️  Setting up Azure Cloud Environment..."
        echo ""
        echo "This will:"
        echo "- Create Azure OpenAI resource"
        echo "- Create Azure AI Search resource"
        echo "- Configure search index"
        echo "- Generate .env file"
        echo ""
        read -p "Continue? (y/n): " confirm
        if [ "$confirm" = "y" ]; then
            echo "Starting Azure setup..."
            python scripts/azure-setup-simple.py
        fi
        ;;
    3)
        echo "🔀 Setting up Hybrid Environment..."
        echo ""
        echo "This will:"
        echo "- Start local PostgreSQL and Redis"
        echo "- Use Azure OpenAI for LLM"
        echo "- Use Azure AI Search for vector search"
        echo ""
        read -p "Continue? (y/n): " confirm
        if [ "$confirm" = "y" ]; then
            echo "Starting hybrid setup..."
            echo "1. Setting up Azure resources..."
            python scripts/azure-setup-simple.py
            echo ""
            echo "2. Starting local services..."
            docker-compose up -d postgres redis
            echo ""
            echo "3. Starting application..."
            docker-compose up
        fi
        ;;
    *)
        echo "❌ Invalid option. Please run the script again."
        exit 1
        ;;
esac

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📚 Next Steps:"
echo "1. Deploy models in Azure OpenAI Studio (if using Azure)"
echo "2. Test the setup with the provided test scripts"
echo "3. Start the application"
echo "4. Access the application at http://localhost:3000"
echo ""
echo "📖 Documentation:"
echo "- Setup Guide: docs/AZURE_SETUP_GUIDE.md"
echo "- Azure OpenAI Integration: docs/AZURE_OPENAI_INTEGRATION.md"
echo "- Azure Search Migration: docs/AZURE_SEARCH_MIGRATION.md"
echo ""
echo "🆘 Need Help?"
echo "- Check the documentation in the docs/ folder"
echo "- Run the test scripts to verify your setup"
echo "- Check the logs for any errors"
