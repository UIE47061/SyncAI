# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MBBuddy is a local privacy-focused AI meeting collaboration platform that combines anonymous opinion collection, real-time voting, AI assistance, and automatic summarization. The system uses FastAPI backend with llama-cpp-python for local AI inference and Vue 3 frontend.

## Key Architecture

### Backend Structure
- **FastAPI Application**: `backend/main.py` - Main entry point with CORS middleware
- **AI Module**: `backend/api/ai_api.py` - AnythingLLM integration for AI features (no longer local model)
- **AI Configuration**: `backend/api/ai_config.py` - AI client configuration and settings
- **AI Client**: `backend/api/ai_client.py` - AnythingLLM API client implementation  
- **AI Prompts**: `backend/api/ai_prompts.py` - Prompt building and topic parsing utilities
- **Meeting Management**: `backend/api/participants_api.py` - Room management, voting, participant handling
- **Network API**: `backend/api/network_api.py` - Network-related API endpoints
- **Utilities**: `backend/api/utility.py` - PDF report generation with ReportLab

### Frontend Structure  
- **Vue 3 + Vite**: `frontend/syncai-frontend/` - Single-page application
- **Components**: Modular UI components for room creation, host/participant panels
- **State Management**: `frontend/src/composables/useRoom.js` - Room state and API communication (no WebSocket)
- **API Layer**: `frontend/src/utils/api.js` - Backend communication wrapper

### AI Integration
- Uses AnythingLLM for AI features (external service integration)
- Configuration through environment variables in Docker dev setup
- Workspace-based AI context management per meeting room
- Supports meeting summarization and topic generation

## Development Commands

### Automated Setup Scripts (Recommended)

#### Quick Setup:
```bash
# macOS/Linux - One-time environment setup
scripts/setup_dev.sh

# Windows - One-time environment setup  
scripts\setup_dev.bat

# Start development servers (both backend and frontend)
scripts/start_dev.sh    # macOS/Linux
scripts\start_dev.bat   # Windows

# Stop development servers
scripts/stop_dev.sh     # macOS/Linux
scripts\stop_dev.bat    # Windows
```

### Manual Setup (Alternative)

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

# Run development server (with host binding for network access)
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

## AI Service Setup

**Note**: The system now uses AnythingLLM instead of local models. Configuration is handled through environment variables:

```bash
# Docker development environment automatically configures:
# ANYTHINGLLM_BASE_URL=http://host.docker.internal:3001
# ANYTHINGLLM_API_KEY=PNB2B7R-4EC4P21-NM0XHTX-4BHZBHJ
# ANYTHINGLLM_WORKSPACE_SLUG=mac

# For local development, ensure AnythingLLM service is running
# Test connection: GET /ai/test_connection
```

Legacy model files in `ai_models/` directory are no longer required for the current implementation.

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
- Uses AnythingLLM API for AI features via HTTP client
- Workspace-based context management for meeting rooms
- Supports meeting summarization, topic generation, and chat functionality
- Configurable through environment variables

### Meeting System
- Room-based architecture with unique room codes
- Real-time voting and opinion collection via polling (no WebSocket)
- In-memory data structures for rooms, topics, and votes
- PDF report generation with charts and analysis using ReportLab

### Data Architecture
- `ROOMS`: Meeting room metadata and settings
- `topics`: Topic-based comment organization (`{room_id}_{topic_name}`)
- `votes`: Comment voting records by device ID
- Participant tracking with heartbeat mechanism

### Frontend State Management
- `useRoom.js` composable handles room state and API communication
- Device ID generation and persistence for anonymous voting
- Real-time UI updates through periodic polling (3-second intervals)
- Local nickname storage per room

## Privacy & Security
- Local meeting data storage with in-memory persistence
- Anonymous participation through device ID system
- Network-local deployment recommended for privacy
- AnythingLLM integration allows for local AI processing when configured appropriately

## API Endpoints Structure

### Meeting Management
- `POST /api/create_room` - Create new meeting room
- `GET /api/rooms` - List all rooms
- `GET /api/rooms/{room}/state` - Get room state and comments
- `PUT /api/rooms/{room}/topic` - Update current topic

### Participants  
- `POST /api/participants/join` - Join meeting room
- `POST /api/participants/heartbeat` - Maintain connection
- `PUT /api/rooms/{room}/participants/{device_id}/nickname` - Update nickname

### Comments & Voting
- `POST /api/rooms/{room}/comments` - Submit comment
- `POST /api/rooms/{room}/comments/{comment_id}/vote` - Vote on comment
- `DELETE /api/rooms/{room}/comments/{comment_id}/vote` - Remove vote

### AI Features
- `POST /ai/summary` - Generate meeting summary
- `POST /ai/generate_topics` - Generate topic suggestions
- `POST /ai/ask` - Chat with AI assistant
- 進行合理的程式分段
- 目前所有的code最後都要部署到snapdragon elite x上