# Next.js AI Agent Template with Claude SDK, RAG (Chroma), and MCP (Composio)

## Project Overview
A production-ready Next.js application template featuring an intelligent AI agent powered by Claude SDK, enhanced with Retrieval-Augmented Generation (RAG) using Chroma vector database, and extended capabilities through Model Context Protocol (MCP) integration with Composio.

## Architecture Overview

### Core Components
1. **Next.js Frontend & Backend**
   - App Router (Next.js 14+)
   - Server Components for optimal performance
   - API Routes for backend logic
   - Real-time streaming responses

2. **Claude SDK Integration**
   - Anthropic Claude API for LLM capabilities
   - Streaming conversation support
   - Context management
   - Token optimization

3. **RAG System (Chroma)**
   - Vector database for knowledge storage
   - Document embedding and retrieval
   - Semantic search capabilities
   - Dynamic context injection

4. **MCP Integration (Composio)**
   - Tool orchestration
   - External service integrations
   - Action execution framework
   - Multi-agent coordination

## Technology Stack

### Frontend
- Next.js 14+ (App Router)
- TypeScript
- Tailwind CSS
- shadcn/ui components
- React Query for state management
- Vercel AI SDK for streaming UI

### Backend
- Next.js API Routes
- Node.js runtime
- TypeScript
- Prisma ORM (optional for user data)

### AI & ML
- Anthropic Claude SDK
- LangChain.js for orchestration
- Chroma vector database
- OpenAI embeddings (or alternative)
- Composio MCP tools

### Infrastructure
- Docker for containerization
- PostgreSQL for application data
- Redis for caching (optional)
- Environment variable management

## Project Structure

```
next-ai-agent-template/
├── app/
│   ├── api/
│   │   ├── agent/
│   │   │   ├── chat/
│   │   │   │   └── route.ts
│   │   │   ├── tools/
│   │   │   │   └── route.ts
│   │   │   └── rag/
│   │   │       └── route.ts
│   │   └── webhooks/
│   │       └── composio/
│   │           └── route.ts
│   ├── components/
│   │   ├── chat/
│   │   │   ├── ChatInterface.tsx
│   │   │   ├── MessageList.tsx
│   │   │   └── InputArea.tsx
│   │   ├── rag/
│   │   │   ├── DocumentUpload.tsx
│   │   │   └── KnowledgeBase.tsx
│   │   └── ui/
│   ├── layout.tsx
│   └── page.tsx
├── lib/
│   ├── ai/
│   │   ├── claude/
│   │   │   ├── client.ts
│   │   │   └── streaming.ts
│   │   ├── rag/
│   │   │   ├── chroma.ts
│   │   │   ├── embeddings.ts
│   │   │   └── retrieval.ts
│   │   ├── mcp/
│   │   │   ├── composio.ts
│   │   │   ├── tools.ts
│   │   │   └── actions.ts
│   │   └── agents/
│   │       ├── base.ts
│   │       └── orchestrator.ts
│   ├── utils/
│   └── types/
├── config/
│   ├── ai.config.ts
│   ├── chroma.config.ts
│   └── composio.config.ts
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── tests/
├── .env.example
├── package.json
└── README.md
```

## Implementation Phases (HACKATHON TIMELINE: Until Sunday 9:30 AM)

### Phase 1: Foundation Setup (Saturday Morning - 4 hours)
**Target: Working Next.js app with basic UI**
1. **Initialize Next.js Project** (1 hour)
   - Create Next.js app with TypeScript
   - Install essential packages: Tailwind CSS, shadcn/ui basics
   - Set up minimal project structure
   - Create .env file with API keys

2. **Basic Chat Interface** (3 hours)
   - Create simple chat UI component
   - Add message display and input area
   - Basic styling with Tailwind
   - Set up API route structure

### Phase 2: Claude SDK Integration (Saturday Afternoon - 4 hours)
**Target: Working AI chat with Claude**
1. **Claude Client Setup** (2 hours)
   - Initialize Anthropic SDK
   - Configure API authentication
   - Create basic chat endpoint
   - Test simple Q&A

2. **Streaming Implementation** (2 hours)
   - Add streaming response handling
   - Update UI for real-time responses
   - Basic error handling
   - Test conversation flow

### Phase 3: RAG Implementation with Chroma (Saturday Evening - 5 hours)
**Target: Document upload and retrieval working**
1. **Chroma Quick Setup** (1.5 hours)
   - Run Chroma in Docker (simple setup)
   - Install required packages
   - Basic collection setup

2. **Document Processing** (2 hours)
   - Simple file upload component
   - Basic text chunking (simple strategy)
   - Generate embeddings
   - Store in Chroma

3. **Retrieval System** (1.5 hours)
   - Basic semantic search
   - Inject retrieved context into Claude
   - Test with sample documents
   - Display sources in UI

### Phase 4: MCP Integration with Composio (Saturday Night/Sunday Morning - 4 hours)
**Target: At least 2-3 working tools**
1. **Composio Quick Setup** (1 hour)
   - Configure Composio SDK
   - Set up API key
   - Register 2-3 simple tools (e.g., web search, calculator, GitHub)

2. **Tool Integration** (2 hours)
   - Define minimal tool schemas
   - Implement tool execution in agent
   - Basic error handling
   - Test each tool individually

3. **Connect to Agent** (1 hour)
   - Integrate tools with Claude agent
   - Add tool calling logic
   - Test tool selection and execution

### Phase 5: Demo Polish (Sunday Morning - 3 hours)
**Target: Presentable demo**
1. **UI/UX Improvements** (1.5 hours)
   - Clean up styling
   - Add loading states
   - Improve error messages
   - Mobile responsive basics

2. **Demo Preparation** (1.5 hours)
   - Prepare sample documents
   - Test full user flow
   - Fix critical bugs
   - Prepare demo script
   - Create quick README

### Phase 6: Final Testing & Backup (Sunday Morning - 1.5 hours before deadline)
**Target: Stable, deployable demo**
1. **Critical Path Testing** (1 hour)
   - Test complete workflows
   - Fix show-stopping bugs
   - Verify all API keys work
   - Test deployment

2. **Documentation** (30 minutes)
   - Quick setup instructions
   - Demo walkthrough
   - Known limitations
   - Future improvements list

## Key Features

### Core Functionality
- Real-time chat interface with Claude
- Document upload and knowledge base management
- Semantic search across uploaded documents
- Tool execution through Composio MCP
- Multi-turn conversations with context retention
- Streaming responses for better UX

### RAG Features
- Document chunking strategies
- Multiple embedding models support
- Hybrid search (semantic + keyword)
- Metadata filtering
- Dynamic context window management
- Source attribution in responses

### MCP Capabilities
- Email integration
- Calendar management
- File operations
- Web scraping
- API integrations
- Custom tool creation

### Advanced Features
- User authentication and sessions
- Conversation history
- Knowledge base versioning
- Rate limiting
- Cost tracking
- Multi-language support

## Configuration & Setup

### Environment Variables
```env
# Claude API
ANTHROPIC_API_KEY=your_api_key

# Chroma
CHROMA_HOST=localhost
CHROMA_PORT=8000
CHROMA_API_KEY=your_chroma_key

# Composio
COMPOSIO_API_KEY=your_composio_key
COMPOSIO_WEBHOOK_SECRET=your_webhook_secret

# Embeddings
OPENAI_API_KEY=your_openai_key  # If using OpenAI embeddings

# Database (optional)
DATABASE_URL=postgresql://...

# Redis (optional)
REDIS_URL=redis://...
```

### Docker Setup
```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
    depends_on:
      - chroma
      - redis

  chroma:
    image: chromadb/chroma
    ports:
      - "8000:8000"
    volumes:
      - chroma_data:/chroma/data

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
```

## API Endpoints

### Chat Endpoints
- `POST /api/agent/chat` - Send message to agent
- `GET /api/agent/chat/history` - Get conversation history
- `DELETE /api/agent/chat/:id` - Delete conversation

### RAG Endpoints
- `POST /api/rag/documents` - Upload documents
- `GET /api/rag/search` - Search knowledge base
- `DELETE /api/rag/documents/:id` - Remove document

### Tool Endpoints
- `GET /api/tools` - List available tools
- `POST /api/tools/execute` - Execute tool action
- `GET /api/tools/:id/status` - Check tool execution status

## Security Considerations

1. **API Key Management**
   - Secure storage in environment variables
   - Key rotation policies
   - Rate limiting per API key

2. **Data Privacy**
   - Encryption at rest for sensitive data
   - GDPR compliance features
   - User data deletion capabilities

3. **Input Validation**
   - Sanitize user inputs
   - Prevent prompt injection
   - File upload restrictions

4. **Access Control**
   - User authentication
   - Role-based permissions
   - API endpoint protection

## Deployment Strategy

### Development
```bash
npm run dev
# Start Chroma locally
docker-compose up chroma
```

### Staging
- Deploy to Vercel Preview
- Use staging API keys
- Test with limited data

### Production
- Deploy to Vercel/AWS/GCP
- Set up monitoring
- Configure auto-scaling
- Enable CDN for static assets

## Performance Metrics

### Target Metrics
- Initial response time: < 500ms
- Streaming start: < 1s
- RAG retrieval: < 200ms
- Tool execution: < 2s
- 99th percentile latency: < 3s

### Optimization Strategies
- Vector index optimization
- Response caching
- Connection pooling
- Lazy loading components
- Edge function deployment

## Monitoring & Maintenance

### Logging
- Application logs (Winston/Pino)
- API request/response logs
- Error tracking (Sentry)
- Performance monitoring (Datadog/New Relic)

### Metrics to Track
- Response times
- Token usage
- API costs
- User engagement
- Error rates
- Tool execution success rate

## Future Enhancements

### Potential Features
- Voice input/output
- Multi-modal support (images, videos)
- Fine-tuned models
- Collaborative agents
- Advanced analytics dashboard
- Mobile app support
- Plugin marketplace
- Self-hosted option

### Scalability Considerations
- Horizontal scaling strategy
- Database sharding
- Vector database clustering
- Load balancing
- Queue-based processing
- Microservices architecture

## Resources & References

### Documentation
- [Next.js Documentation](https://nextjs.org/docs)
- [Anthropic Claude API](https://docs.anthropic.com)
- [Chroma Documentation](https://docs.trychroma.com)
- [Composio Documentation](https://docs.composio.dev)
- [LangChain.js](https://js.langchain.com)

### Example Repositories
- Next.js AI examples
- Claude SDK examples
- RAG implementation patterns
- MCP integration samples

## Success Criteria

### MVP Requirements
- Working chat interface with Claude
- Basic RAG functionality with 5+ documents
- At least 3 integrated Composio tools
- Streaming responses
- Basic error handling

### Production Requirements
- 99.9% uptime
- < 3s response time for 95% of requests
- Support for 100+ concurrent users
- Comprehensive test coverage (>80%)
- Full documentation

## Timeline Summary (HACKATHON - Until Sunday 9:30 AM)

**Total Time: ~21.5 hours of focused development**

- **Phase 1 (4h)**: Saturday Morning - Foundation & basic chat UI
- **Phase 2 (4h)**: Saturday Afternoon - Claude integration with streaming
- **Phase 3 (5h)**: Saturday Evening - RAG with Chroma
- **Phase 4 (4h)**: Saturday Night/Early Sunday - MCP/Composio tools
- **Phase 5 (3h)**: Sunday Morning - Demo polish & UX
- **Phase 6 (1.5h)**: Final testing & deployment preparation

**DEADLINE: Sunday 9:30 AM**

## MVP Success Criteria (Must-Haves for Demo)

1. Working chat interface with Claude AI
2. At least 3-5 documents successfully indexed in RAG system
3. At least 2 working Composio tools integrated
4. Streaming responses visible in UI
5. Basic error handling (app doesn't crash)
6. Deployed and accessible via URL
7. 2-minute demo script ready

## Nice-to-Haves (If Time Permits)

- Conversation history persistence
- Multiple embedding models
- Advanced styling/animations
- More than 3 tools
- Admin dashboard
- User authentication

## Hackathon Strategy

**Focus on working features over perfect code:**
- Get each component barely working before moving to next
- Use simple implementations (can refactor later)
- Don't spend time on edge cases unless critical
- Copy examples from documentation liberally
- Test frequently to catch issues early
- Have working backup at each phase

**Time Management:**
- Build sequentially - don't start Phase N until Phase N-1 works
- Set timer for each phase
- If stuck >30 min, simplify or skip to next task
- Save last 4 hours for polish and bug fixing
- Deploy early (Saturday night) to catch deployment issues

This template will serve as a hackathon MVP demonstrating AI-powered applications, combining Claude's language understanding, Chroma's vector search capabilities, and Composio's tool integration ecosystem.