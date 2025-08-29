# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SyncAI is a local privacy-focused AI meeting collaboration platform that combines anonymous opinion collection, real-time voting, AI assistance, and automatic summarization. The system uses FastAPI backend with llama-cpp-python for local AI inference and Vue 3 frontend.

## Key Architecture

### Backend Structure
- **FastAPI Application**: `backend/main.py` - Main entry point with CORS middleware
- **AI Module**: `backend/api/ai_api.py` - Local Mistral 7B model integration via llama-cpp-python
- **Meeting Management**: `backend/api/participants_api.py` - Room management, voting, participant handling
- **Utilities**: `backend/api/utility.py` - PDF report generation with ReportLab

### Frontend Structure  
- **Vue 3 + Vite**: `frontend/syncai-frontend/` - Single-page application
- **Components**: Modular UI components for room creation, host/participant panels
- **State Management**: `frontend/src/composables/useRoom.js` - Room state and WebSocket communication
- **API Layer**: `frontend/src/utils/api.js` - Backend communication wrapper

### AI Model Integration
- Uses local Mistral 7B model (`ai_models/mistral-7b-instruct-v0.2.Q5_K_M.gguf`)
- Model must be downloaded separately (5.1GB) using provided scripts
- Global singleton pattern for model loading in `ai_api.py:12`
- Supports NPU acceleration on Snapdragon X devices

## Development Commands

### Local Development Setup

#### Backend (from project root):
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate

# Install dependencies
pip install -r requirement.txt

# Run development server
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8001
```

#### Frontend (from frontend/syncai-frontend/):
```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Docker Development

#### Development Environment (with hot reload):
```bash
# Start development containers
docker-compose -f docker/docker-compose.dev.yml up -d

# View logs
docker-compose -f docker/docker-compose.dev.yml logs -f

# Stop containers
docker-compose -f docker/docker-compose.dev.yml down
```

#### Production Environment:
```bash
# Start production containers
docker-compose -f docker/docker-compose.yml up -d

# Stop containers
docker-compose -f docker/docker-compose.yml down
```

## Model Setup Requirements

**CRITICAL**: AI model must be downloaded before running the application:

```bash
# Automatic download (recommended)
./download_model.sh      # macOS/Linux
# or download_model.bat   # Windows

# Manual download
cd ai_models
wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q5_K_M.gguf
```

Verify download: `ls -lh ai_models/mistral-7b-instruct-v0.2.Q5_K_M.gguf` (should be ~5.1GB)

## Service Ports

### Development:
- Frontend: `http://[IP]:5173`
- Backend: `http://[IP]:8001`

### Production:  
- Frontend: `http://[IP]:80`
- Backend: `http://[IP]:8000`

## Testing

The project includes a basic test file (`test.py`) but no comprehensive test framework is configured. When implementing tests, examine existing patterns in the codebase first.

## Key Implementation Notes

### AI Integration
- Model loaded as global singleton in `ai_api.py` for memory efficiency
- Local inference only - no cloud dependencies
- Supports text generation and meeting summarization endpoints

### Meeting System
- Room-based architecture with unique room codes
- Real-time voting and opinion collection
- WebSocket communication for live updates
- PDF report generation with charts and analysis

### Docker Volume Mounting
- AI models are volume-mounted (not copied into containers) for efficiency
- Development containers mount source code for hot reload
- Ensure model file exists locally before Docker deployment

## Privacy & Security
- Full local operation - no external API calls
- All meeting data stays on local server
- Designed for internal/private network deployment