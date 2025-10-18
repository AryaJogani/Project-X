#!/bin/bash

# Knowledge Transfer Bot - Setup Script
# Enhanced implementation with LLM orchestration

echo "🚀 Setting up Knowledge Transfer Bot..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create environment files
echo "📝 Creating environment files..."

# Backend environment
if [ ! -f backend/.env ]; then
    cp backend/env.example backend/.env
    echo "✓ Created backend/.env from template"
    echo "⚠️  Please update backend/.env with your API keys"
else
    echo "✓ backend/.env already exists"
fi

# Frontend environment
if [ ! -f frontend/.env.local ]; then
    cat > frontend/.env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8001
NEXT_PUBLIC_WS_URL=ws://localhost:8001
EOF
    echo "✓ Created frontend/.env.local"
else
    echo "✓ frontend/.env.local already exists"
fi

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
if [ ! -d "node_modules" ]; then
    npm install
    echo "✓ Frontend dependencies installed"
else
    echo "✓ Frontend dependencies already installed"
fi
cd ..

# Start services with Docker Compose
echo "🐳 Starting services with Docker Compose..."
docker-compose up -d postgres redis rabbitmq

echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service health
echo "🔍 Checking service health..."

# Check PostgreSQL
if docker-compose exec postgres pg_isready -U kt_user -d kt_ai > /dev/null 2>&1; then
    echo "✓ PostgreSQL is ready"
else
    echo "❌ PostgreSQL is not ready"
fi

# Check Redis
if docker-compose exec redis redis-cli ping > /dev/null 2>&1; then
    echo "✓ Redis is ready"
else
    echo "❌ Redis is not ready"
fi

# Note about Azure AI Search
echo "ℹ️  Azure AI Search is a cloud service - configure your credentials in .env"

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Update backend/.env with your API keys:"
echo "   - OPENAI_API_KEY"
echo "   - ANTHROPIC_API_KEY"
echo "   - GOOGLE_API_KEY"
echo "   - AZURE_OPENAI_ENDPOINT"
echo "   - AZURE_OPENAI_API_KEY"
echo "   - AZURE_OPENAI_DEPLOYMENT_NAME"
echo "   - AZURE_SEARCH_ENDPOINT"
echo "   - AZURE_SEARCH_KEY"
echo ""
echo "2. Setup Azure AI Search:"
echo "   python scripts/setup-azure-search.py"
echo ""
echo "3. Setup Azure OpenAI:"
echo "   python scripts/setup-azure-openai.py"
echo ""
echo "4. Setup Azure Infrastructure (Optional):"
echo "   python scripts/azure-setup-simple.py"
echo ""
echo "5. Start the backend:"
echo "   cd backend && pip install -r requirements.txt"
echo "   uvicorn app.main:app --reload"
echo ""
echo "6. Start the frontend:"
echo "   cd frontend && npm run dev"
echo ""
echo "7. Or use Docker Compose for everything:"
echo "   docker-compose up"
echo ""
echo "🌐 Access the application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8001"
echo "   API Docs: http://localhost:8001/docs"
echo ""
echo "📚 Documentation:"
echo "   - README.md - Project overview"
echo "   - docs/ - Detailed documentation"
echo ""
echo "Happy coding! 🚀"
