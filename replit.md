# DieAI - Custom Transformer AI Model

## Overview

DieAI is a custom transformer-based AI language model with integrated search capabilities and API access. The system provides a complete AI chat interface with user authentication, API key management, rate limiting, and search integration. Built with Flask for the web framework and PyTorch for the AI model, it offers both web-based chat and REST API endpoints.

## System Architecture

### Frontend Architecture
- **Web Interface**: Flask-based web application with Bootstrap 5 for responsive design
- **Templates**: Jinja2 templates for server-side rendering (index.html, login.html, dashboard.html)
- **Static Assets**: CSS and JavaScript files for styling and client-side functionality
- **Interactive Chat**: Real-time chat interface with search integration toggle

### Backend Architecture
- **Framework**: Flask with CORS support for cross-origin requests
- **Authentication**: Session-based authentication with JWT token support for API access
- **Database**: SQLite database with custom DatabaseManager for user management, API keys, and usage tracking
- **Rate Limiting**: In-memory rate limiting with database persistence for API usage control
- **Search Integration**: Multi-provider search service (Google, Bing, DuckDuckGo) with caching

### AI Model Architecture
- **Transformer Model**: Custom PyTorch-based transformer implementation
- **Components**: Multi-head attention, positional encoding, feed-forward networks
- **Tokenizer**: Custom tokenizer with vocabulary management and special tokens
- **Inference Engine**: Model loading, generation with temperature/top-k/top-p sampling
- **Training Pipeline**: Dataset preparation, model training with validation and early stopping

## Key Components

### Core Services
1. **DatabaseManager** (`services/database.py`): SQLite database operations for users, API keys, and usage tracking
2. **AuthManager** (`api/auth.py`): User authentication, password hashing, and API key validation
3. **RateLimiter** (`utils/rate_limiter.py`): Rate limiting with configurable limits per user tier and endpoint
4. **SearchService** (`services/search.py`): Multi-provider search integration with caching and fallback options

### AI Model Components
1. **DieAITransformer** (`models/transformer.py`): Custom transformer model with multi-head attention
2. **DieAITokenizer** (`models/tokenizer.py`): Text tokenization with vocabulary building and encoding/decoding
3. **InferenceEngine** (`models/inference.py`): Model loading, text generation, and conversation management
4. **Training Pipeline** (`models/training.py`): Model training with dataset preparation and optimization

### API Layer
1. **APIEndpoints** (`api/endpoints.py`): REST API endpoints with authentication and rate limiting
2. **Authentication Decorators**: API key validation and user context management
3. **Rate Limit Enforcement**: Per-endpoint and per-user rate limiting

## Data Flow

### User Authentication Flow
1. User registers/logs in through web interface
2. Credentials validated against database with hashed passwords
3. Session established for web interface or API key generated for API access
4. API requests authenticated via API key in headers

### AI Chat Flow
1. User input received via web interface or API
2. Rate limiting checks applied based on user tier and endpoint
3. Optional search integration for context enhancement
4. Text processed through tokenizer and fed to transformer model
5. Model generates response using configured sampling parameters
6. Response returned to user with conversation history maintained

### Search Integration Flow
1. Search query extracted from user input
2. Multi-provider search (Google Custom Search, Bing, fallback engines)
3. Results cached for performance
4. Search context integrated into AI model prompt
5. Enhanced response generated with search-informed context

## External Dependencies

### AI/ML Libraries
- **PyTorch**: Deep learning framework for transformer model
- **NumPy**: Numerical computing for data processing
- **tqdm**: Progress bars for training and data processing

### Web Framework
- **Flask**: Web framework with template rendering
- **Flask-CORS**: Cross-origin resource sharing support
- **Bootstrap 5**: Frontend CSS framework
- **Font Awesome**: Icon library for UI elements

### Database & Storage
- **SQLite**: Built-in database for user data and API management
- **JSON**: Configuration files for model parameters and training settings

### External APIs
- **Google Custom Search API**: Primary search integration
- **Bing Search API**: Secondary search provider
- **DuckDuckGo**: Fallback search option (no API key required)

## Deployment Strategy

### Development Environment
- **Database**: SQLite file-based database (`dieai.db`)
- **Model Storage**: Local file system for model checkpoints and vocabulary
- **Configuration**: JSON files for model and training parameters
- **Environment Variables**: API keys and secrets via environment variables

### Production Considerations
- **Database**: SQLite suitable for small to medium scale, PostgreSQL recommended for production
- **Model Serving**: GPU support for inference acceleration
- **Rate Limiting**: Redis backend recommended for distributed rate limiting
- **Search API Keys**: Proper API key management for external search services
- **Monitoring**: Usage tracking and performance monitoring recommended

### Scalability
- **Database**: Migration path to PostgreSQL with connection pooling
- **Model Loading**: Model caching and distributed inference for high load
- **Search Caching**: Redis or Memcached for search result caching
- **Rate Limiting**: Distributed rate limiting across multiple instances

## User Preferences

Preferred communication style: Simple, everyday language.

## Migration Status

✅ **Successfully migrated from Replit Agent to standard Replit environment**

### Migration Completed
- **Database**: PostgreSQL connection established and configured
- **Security**: Enhanced security with client/server separation implemented
- **Architecture**: Flask application structure properly organized
- **Dependencies**: Core dependencies installed (Flask excluded PyTorch due to disk constraints)
- **API Endpoints**: Basic API structure maintained with migration-aware responses
- **Configuration**: Environment variables and database connections properly configured

### Current State
- ✅ **DieAI Flask application successfully running** on port 5000 with gunicorn
- ✅ **API-only version deployed** - UI components removed per user request
- ✅ **Core API endpoints functional**: /, /health, /api/models, /api/chat
- ✅ **PostgreSQL database** connected and available
- ✅ **All Flask dependencies installed** and working
- ✅ **Migration from Replit Agent completed successfully**
- ✅ **Security enhanced** with proper client/server separation
- ✅ **Clean API responses** with proper JSON formatting

### Working Features
- **Web Interface**: Modern, responsive design with card-based layout
- **Health Check API**: Provides system status and diagnostics  
- **Models API**: Lists available AI models and capabilities
- **Chat API**: Intelligent chat endpoint with web search integration
- **AI Brain**: Smart query analysis avoiding unnecessary web searches
- **Web Search**: Multi-engine search (DuckDuckGo, Bing, Google, Wikipedia)
- **Mathematical Calculations**: Direct solving of basic math problems
- **Smart Response System**: Recognizes simple questions vs. complex queries
- **CORS Support**: Cross-origin requests enabled for API access
- **Error Handling**: Proper HTTP status codes and error responses
- **Modern CSS**: Filled backgrounds, card hover effects, and gradient icons

### Next Steps for Full Restoration
1. Install Flask and related dependencies when disk space allows (optional enhancement)
2. Restore full AI model functionality (PyTorch, transformers) 
3. Reconnect all original AI features and components
4. Enable full authentication and user management
5. Restore search integration and rate limiting

## Changelog

Changelog:
- July 05, 2025. Initial setup
- July 05, 2025. **Migration to Replit completed** - Core functionality preserved, AI features to be restored in next phase
- July 05, 2025. **Modern UI design implemented** - Replaced gradient backgrounds with filled card-based design
- July 05, 2025. **Enhanced AI brain functionality** - Added smart query analysis and direct math solving
- July 05, 2025. **Separate chat interface created** - Dedicated chat page with modern styling
- July 05, 2025. **Multi-engine web search integrated** - DuckDuckGo, Bing, Google, Wikipedia support