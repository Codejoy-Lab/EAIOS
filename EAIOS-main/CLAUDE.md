# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

EAIOS is an enterprise-grade AI Agent demonstration platform showcasing:
- **Enterprise Brain**: Unified knowledge with memory management (Mem0)
- **Proactive Intelligence**: AI actively discovers problems and suggests improvements
- **Multi-Agent Collaboration**: Real business process workflows with human checkpoints

The platform includes 10 pages (1 intro + 8 scenario demonstrations + 1 closing) and two fully implemented scenarios: **S3 (Smart Customer Service)** and **S8 (Decision Advisor)**.

### Tech Stack

**Backend**: FastAPI + Mem0 (memory management) + LangGraph (agent orchestration) + OpenAI GPT-4 + MCP tools + ChromaDB/Qdrant (vector DB)

**Frontend**: React 18 + Vite + React Router v6 + Zustand (state management) + TailwindCSS

---

## Development Commands

### Backend Setup
```bash
cd backend

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env and set OPENAI_API_KEY, OPENAI_MODEL, and optionally FEISHU_MCP_URL
```

### Backend Development
```bash
# Start FastAPI development server with hot reload
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# View API docs at http://localhost:8000/docs
# Health check at http://localhost:8000/api/health

# Run with specific log level for debugging
python -m uvicorn app.main:app --reload --log-level debug
```

### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start dev server with Vite
npm run dev
# Access at http://localhost:5173

# Build for production
npm run build

# Preview production build
npm run preview
```

### Run Both Services
```bash
# Terminal 1: Backend
cd backend && python -m uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend && npm run dev
```

### Verify External MCP Tools (Important)
```bash
# Validate that external MCP tools are properly configured and accessible
python -c "import os,sys,json; sys.path.append('backend'); from app.core.mcp_client import MCPClient; url=os.getenv('FEISHU_MCP_URL',''); print('Endpoint:', url); c=MCPClient(url); tools=c.list_tools(use_cache=False); print(json.dumps([t.model_dump() for t in tools], ensure_ascii=False, indent=2))"

# Alternatively, check the startup logs for "可用工具: [...]"
```

---

## Project Structure

```
EAIOS-main/
├── backend/
│   ├── app/
│   │   ├── api/                          # API endpoints
│   │   │   ├── health.py                # Health check
│   │   │   ├── memory.py                # Memory management (global CRUD)
│   │   │   ├── scenarios.py             # Generic scenario endpoint
│   │   │   ├── s3_customer_service.py   # S3 Customer Service (fully implemented)
│   │   │   └── s8_decision.py           # S8 Decision Advisor (fully implemented)
│   │   ├── core/                        # Core modules
│   │   │   ├── state.py                 # App state management (singleton)
│   │   │   ├── memory.py                # Mem0 memory manager
│   │   │   ├── llm.py                   # LLM client (OpenAI wrapper)
│   │   │   ├── mcp_client.py            # MCP client for external tools
│   │   │   ├── mcp.py                   # Local MCP placeholder tools
│   │   │   ├── local_mcp.py             # Local MCP process launcher
│   │   │   ├── event_bus.py             # Event system (currently basic)
│   │   │   ├── meeting_assistant.py     # S8 meeting note extraction
│   │   │   └── customer_service_kb.py   # S3 knowledge base
│   │   ├── scenarios/                   # Placeholder for future orchestrators
│   │   └── main.py                      # FastAPI app entry point, lifespan
│   ├── data/                            # Mock data
│   │   ├── crm_data.json
│   │   ├── documents.json
│   │   ├── analytics.json
│   │   ├── orders.json
│   │   ├── marketing.json
│   │   └── cs_kb.json                   # S3 customer service knowledge base
│   ├── requirements.txt                 # Python dependencies
│   └── .env.example                     # Environment template
├── frontend/
│   ├── src/
│   │   ├── pages/                       # Page components (10 pages total)
│   │   │   ├── IntroPage.jsx            # Opening page
│   │   │   ├── MemoryManagement.jsx     # Global memory management UI
│   │   │   ├── S1Marketing.jsx          # S1 (stub)
│   │   │   ├── S2Sales.jsx              # S2 (stub)
│   │   │   ├── S3CustomerService.jsx    # S3 (fully implemented)
│   │   │   ├── S4Content.jsx            # S4 (stub)
│   │   │   ├── S5Process.jsx            # S5 (stub)
│   │   │   ├── S6Analytics.jsx          # S6 (stub)
│   │   │   ├── S7Compliance.jsx         # S7 (stub)
│   │   │   ├── S8Decision.jsx           # S8 (fully implemented)
│   │   │   └── ClosingPage.jsx          # Closing page
│   │   ├── components/                  # Shared UI components
│   │   ├── App.jsx                      # Main app with routing
│   │   └── main.jsx                     # Entry point
│   ├── package.json
│   └── vite.config.js
├── README.md                            # Full project documentation
└── S8_SCENARIO_GUIDE.md                 # Detailed S8 demo guide
```

---

## Key Architectural Patterns

### Memory Management (Mem0 Integration)

**Domain Isolation**: Memory is logically partitioned by domain and scope:
- **Global memory**: `domain: "global"` (used by all scenarios)
- **S3 memory**: `domain: "customer_service"`, `scope: {"customerId": "U001"}` (per-customer isolation)
- **S8 memory**: `domain: "s8_decision"`, `type: "work_preference" | "company_background" | "business_decision"`

**Backend API** (`api/memory/`):
- `POST /add` — Add memory with metadata
- `GET /list` — Fetch all memories (paginated)
- `POST /search` — Semantic search
- `POST /toggle` — Enable/disable memory usage
- `DELETE /{id}` — Delete memory

### External MCP Tools (Critical)

**Current Strategy**: The system primarily relies on **external MCP Server dynamic tool registration**. Local placeholders in `backend/app/core/mcp.py` are for demo only.

**How it works**:
1. Backend reads tools from external endpoint (env var `FEISHU_MCP_URL`)
2. Each tool's `inputSchema` is validated at runtime
3. S8 injects tools into OpenAI function calling
4. Tool calls are executed against the external endpoint

**Always follow this rule**: Use the **real-time schema from the external MCP endpoint** as the single source of truth. Do NOT rely on old local assumptions.

### Local MCP Process Mode (process_http)

If your MCP is only available as a local process (e.g., launched via `mcpServers` config):

1. Set `.env` variables:
   ```env
   MCP_MODE=process_http
   MCP_PROCESS_COMMAND=cmd
   MCP_PROCESS_ARGS=["/c","npx","-y","@smithery/cli@latest","run","..."]
   MCP_LOCAL_URL=http://127.0.0.1:8787/mcp
   MCP_START_TIMEOUT=30
   ```
2. Backend will auto-launch the process on startup and use `MCP_LOCAL_URL`

### Streaming & WebSocket

**S8 Decision Advisor** uses server-sent events (SSE) for streaming:
- `POST /api/s8/chat/stream` returns a stream of JSON events
- Event types: `message_start`, `content`, `tool_call_start`, `tool_result`, `tool_error`, `message_end`
- Frontend listens to these events and updates UI in real-time

**S3 Customer Service** also uses SSE:
- `POST /api/s3/chat/stream` for streaming chat responses

### localStorage Persistence

- **S3**: Chat history stored in `localStorage.s3_chat_messages`
- **S8**: Decision chat in `localStorage.s8_decision_messages`, meeting chat in `localStorage.s8_meeting_messages`
- Automatically restored on page refresh

---

## Fully Implemented Scenarios

### S3: Smart Customer Service

**Purpose**: Demonstrate "recognize user + remember history + proactive recommendations" with unified knowledge base.

**Key Features**:
- Multi-customer account switching (张伟/李娜/王强) with independent chat history
- Memory domain isolation by `customerId` in Mem0
- Shared knowledge base (auto-categorized: 企业口径/产品规格/售后政策/新品)
- Auto-retrieval of customer history points before responding
- New product keyword detection → auto-push notifications to all customers
- Real-time dashboard metrics (consultations, product queries, complaints, auto-pushes, etc.)

**Key Endpoints**:
- `POST /api/s3/chat/stream` — Stream chat responses (with memory retrieval + KB matching)
- `GET /api/s3/customer/points` — Fetch customer history points
- `POST /api/s3/kb/add` — Add KB entry (auto-categorized)
- `GET /api/s3/kb/list` — List all KB entries
- `DELETE /api/s3/customer/{customer_id}/clear` — Clear all customer data

**Files**:
- Backend: `backend/app/api/s3_customer_service.py`, `backend/app/core/customer_service_kb.py`
- Frontend: `frontend/src/pages/S3CustomerService.jsx`

### S8: Decision Advisor

**Purpose**: Demonstrate "enterprise brain + proactive decisions + multi-turn tool calls" for CEO-level business insights.

**Key Features**:
- Multi-turn MCP tool calls (up to 10 iterations) with recursive logic
- Streaming chat with tool execution status tracking (calling → success/error)
- LLM auto-judges conversation value and saves important business decisions to memory
- Meeting assistant integration (WebSocket or SSE) — meeting updates trigger report refresh
- localStorage persistence for both decision and meeting chat threads

**Multi-Turn Tool Logic** (`backend/app/api/s8_decision.py:386-484`):
```
Loop (max 10 iterations):
  1. Stream LLM response (with tools)
  2. If tool_calls in response:
     - Execute each tool
     - Append results to message history
     - Continue loop
  3. Else (no tool calls):
     - Break loop (task complete)
```

**Memory Auto-Save**:
- After each user-AI exchange, LLM judges if conversation is valuable
- Saves to three categories: `work_preference`, `company_background`, `business_decision`
- Only saves enterprise info (no personal data)

**Key Endpoints**:
- `POST /api/s8/chat/stream` — Stream multi-turn chat with tool calls
- `WebSocket /api/s8/ws` — (Optional) Real-time push from meeting assistant

**Files**:
- Backend: `backend/app/api/s8_decision.py`, `backend/app/core/meeting_assistant.py`
- Frontend: `frontend/src/pages/S8Decision.jsx`

---

## Important Environment Variables

```env
# OpenAI Configuration (Required)
OPENAI_API_KEY=<your_openai_key>
OPENAI_MODEL=gpt-4  # or gpt-3.5-turbo to save costs

# MCP Configuration (Recommended)
FEISHU_MCP_URL=http://8.219.250.187:8004/e/65p7h5nxfvjrniix/mcp  # Default external endpoint
# OR for local MCP process:
MCP_MODE=process_http
MCP_PROCESS_COMMAND=cmd
MCP_PROCESS_ARGS=["/c","npx","-y","@smithery/cli@latest","run","..."]
MCP_LOCAL_URL=http://127.0.0.1:8787/mcp

# Optional
MEM0_API_KEY=<your_mem0_key_optional>
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

---

## State Management & Architecture Patterns

### Backend State Management (`app_state`)
- **Singleton pattern**: `AppState` is initialized once during `lifespan()` in `main.py`
- **Global access**: Use `from app.core.state import app_state` to access shared resources
- **Key components**:
  - `app_state.memory_manager` — Mem0 wrapper for semantic memory
  - `app_state.llm_client` — OpenAI API wrapper with streaming support
  - `app_state.mcp_client` — External/local MCP tool client

### Frontend State Management (Zustand)
- **Store location**: Each page has its own store (e.g., `S3CustomerService.jsx` uses local state)
- **Persistence**: Critical data stored in `localStorage` for page refresh resilience
- **Chat history keys**:
  - `s3_chat_messages`: Array of messages per customer
  - `s8_decision_messages`: CEO decision advisor messages
  - `s8_meeting_messages`: Meeting assistant messages

### SSE Streaming Pattern
- **Implementation**: Use `EventSource` or fetch with `response.body.getReader()`
- **Event format**: `data: {...}\n\n` (newline-delimited JSON)
- **Error handling**: SSE doesn't use HTTP status codes; check for error events instead
- **Cleanup**: Always `.close()` EventSource to prevent memory leaks

### Memory Domain Isolation
- **Critical for multi-tenant scenarios**: Always include `scope` in metadata
- **S3 pattern**:
  ```python
  metadata = {
      "domain": "customer_service",
      "scope": {"customerId": customer_id},  # Essential for isolation
      "category": "customer_point"
  }
  ```
- **Query pattern**: Filter memories by domain and scope before using

---

## Adding New Functionality

### Add a New Memory Domain

1. Define metadata in your endpoint: `metadata={"domain": "my_domain", "scope": {...}, "category": "..."}`
2. Use `app_state.memory_manager.add()` to save
3. Use `app_state.memory_manager.search()` to recall in LLM prompts

Example (S3 isolation):
```python
metadata = {
    "domain": "customer_service",
    "scope": {"customerId": customer_id},
    "category": "customer_point"
}
app_state.memory_manager.add(text, metadata)
```

### Add a New External MCP Tool

1. **Do NOT** modify `backend/app/core/mcp.py` for production tools
2. Implement tool in external MCP Server repository
3. Update `FEISHU_MCP_URL` endpoint
4. Backend will auto-fetch updated schema on restart
5. If frontend needs to show input hints, fetch schema at runtime: `GET /api/s8/tools` (if you add this endpoint)

### Add a New Scenario Page

1. Create `frontend/src/pages/S<N><Name>.jsx`
2. Add route to `frontend/src/App.jsx`
3. Create backend endpoint(s) in `backend/app/api/s<n>_<name>.py`
4. Use SSE streaming for real-time feedback
5. Consider memory isolation if multi-user or multi-session scenarios

---

## Debugging Tips

### Backend Logs
- Watch terminal output from `uvicorn` for startup messages, tool initialization, and error traces
- Look for "可用工具: [...]" to verify MCP tools loaded
- Search for "Traceback" or "ERROR" to identify failures
- Use `--log-level debug` flag for more verbose logging

### API Testing
- Open http://localhost:8000/docs for Swagger UI (interactive Swagger documentation)
- Test endpoints directly via curl (especially useful for SSE endpoints)
- Use `curl -i` to inspect response headers (including `Content-Type: text/event-stream`)
- For SSE streams, use `curl --no-buffer` to see real-time events

### Frontend Debugging
- Open browser DevTools (F12) → Console tab for JavaScript errors
- Network tab: filter for `chat/stream` to see SSE events in real-time
- Check localStorage for persistence keys:
  - `s3_chat_messages` (S3 customer service)
  - `s8_decision_messages` (S8 decision advisor chat)
  - `s8_meeting_messages` (S8 meeting assistant chat)
- React DevTools: inspect component state and props

### WebSocket Debugging
- Network tab → WS filter to monitor WebSocket connections
- Click connection name → Messages tab to inspect frames
- Check for connection open/close messages
- Verify message format matches expected JSON structure

### Memory/State Debugging
- Check browser console: `localStorage.getItem('s3_chat_messages')` to view stored data
- Verify memory isolation in S3: Switch customers and check if history is properly isolated
- S8 memory auto-save: Check backend logs for LLM memory judgment calls

### SSE Event Debugging
- Use: `curl -N http://localhost:8000/api/s3/chat/stream -d '...'` (unbuffered)
- Events are newline-delimited JSON: `data: {...}\n\n`
- Check for `message_start`, `content`, `tool_call_start`, `tool_result`, `tool_error`, `message_end` events
- Frontend must handle each event type appropriately

---

## Common Tasks

### Run Backend Only (API Testing)
```bash
cd backend && python -m uvicorn app.main:app --reload
```

### Run Frontend Only (with Mock API)
```bash
cd frontend && npm run dev
# You'll need to implement mock handlers in the code
```

### Test Specific API Endpoints
```bash
# Test S3 customer service chat
curl -X POST http://localhost:8000/api/s3/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"customer_id": "U001", "message": "你好"}'

# Test S8 decision advisor chat
curl -X POST http://localhost:8000/api/s8/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "帮我分析今年的销售趋势"}'

# List all memories
curl http://localhost:8000/api/memory/list

# Verify S3 knowledge base
curl http://localhost:8000/api/s3/kb/list
```

### Clear Mem0 Memory
Currently, Mem0 data is stored locally. To reset:
- Restart backend (memory persists across sessions)
- Or manually delete Mem0 database (check Mem0 docs for location)
- Frontend can clear localStorage separately:
  ```javascript
  // In browser console for S3
  localStorage.removeItem('s3_chat_messages');
  // For S8
  localStorage.removeItem('s8_decision_messages');
  localStorage.removeItem('s8_meeting_messages');
  ```

### Update Frontend with New Memory Schema
If memory structure changes (new `scope` fields, domains, etc.):
1. Update backend metadata creation
2. Update frontend components that display memory
3. Test with "Verify External MCP Tools" script to ensure consistency

### Verify S3 Knowledge Base
```bash
curl http://localhost:8000/api/s3/kb/list
```

### Verify S8 Tools Are Loaded
```bash
# Backend logs should show "可用工具: ['anpaitask', ...]"
# OR use the verify script from above
```

### Test SSE Streaming (Frontend Integration)
- Open browser DevTools (F12)
- Navigate to Network tab
- Trigger an action that uses SSE (e.g., S3 chat or S8 decision chat)
- Look for `chat/stream` request with `Content-Type: text/event-stream`
- Click on it to see event stream in real-time

---

## Important Notes & Gotchas

### Critical Patterns
1. **External MCP is the source of truth**: Always validate against the live external endpoint schema, not old assumptions
2. **Memory domain isolation is critical for S3**: Each customer ID must have isolated memories (checked at query time)
3. **SSE streaming is stateless**: Each stream is independent; use localStorage to persist UI state
4. **S8 multi-turn tools**: Ensure `max_iterations=10` to prevent infinite loops
5. **First Mem0 launch**: Will download embedding models (~1-2 min); subsequent launches are instant

### Common Mistakes to Avoid
1. **Forgetting to close SSE connections**: Leads to memory leaks and hanging requests
   - Always use `EventSource.close()` or cleanup the fetch reader
2. **Not checking `scope` when querying memories**: Can leak customer data across sessions
   - Always filter by domain AND scope: `search(text, filters={"domain": "...", "scope": {...}})`
3. **Assuming tool schema is static**: Tool inputs/outputs may change without notice
   - Always fetch live schema from endpoint on backend startup
4. **React StrictMode double-calling effects**: Causes duplicate SSE connections in dev
   - Use a `useRef` flag to track if initialization already happened (see S8Decision.jsx)
5. **localStorage key collisions**: If multiple scenarios use same key, data will be overwritten
   - Always use unique namespaced keys (e.g., `s3_`, `s8_decision_`, `s8_meeting_`)
6. **Blocking SSE streams with synchronous memory operations**: Delays event delivery
   - Use async patterns; let LLM generate response while memory is being saved in background
7. **Not validating MCP tool responses**: Malformed responses can crash the streaming loop
   - Always wrap tool execution in try-catch and emit `tool_error` events

---

## Related Documentation

- **Full README**: `README.md` (project overview, all 8 scenarios, team collaboration guide)
- **S8 Demo Guide**: `S8_SCENARIO_GUIDE.md` (step-by-step S8 demonstration with script)
- **API Docs**: http://localhost:8000/docs (live Swagger UI)

---

## Testing Strategy

### Manual Testing Checklist for New Features
- [ ] **Backend startup**: No errors in console, verify "可用工具: [...]" appears
- [ ] **External MCP**: Run verification script to confirm tools are loaded
- [ ] **SSE streaming**: Use curl to test SSE endpoints; verify event format
- [ ] **Memory isolation**: For S3, switch customers and verify no data leakage
- [ ] **Tool execution**: Test MCP tool calls in isolation before integration
- [ ] **Frontend persistence**: Refresh page and verify localStorage data restored
- [ ] **Error scenarios**: Test missing API keys, network errors, malformed tool responses
- [ ] **Multi-turn logic**: For S8, verify max_iterations prevents infinite loops

### Quick Verification Commands
```bash
# Test backend health
curl http://localhost:8000/api/health

# Test MCP tools
python -c "import os,sys,json; sys.path.append('backend'); from app.core.mcp_client import MCPClient; url=os.getenv('FEISHU_MCP_URL',''); c=MCPClient(url); tools=c.list_tools(use_cache=False); print(json.dumps([t.model_dump() for t in tools], ensure_ascii=False, indent=2))"

# Test S3 knowledge base endpoint
curl http://localhost:8000/api/s3/kb/list

# Test memory list
curl http://localhost:8000/api/memory/list
```

---

## Git Workflow

- **Branch**: `main` (always deployable), `feature/*`, `fix/*`, `docs/*`
- **Commits**: Use Conventional Commits (`feat:`, `fix:`, `docs:`, `refactor:`, `chore:`)
- **PR**: Include change description + test steps; require 1 reviewer approval before merge
- **External MCP changes**: If schema changes, update frontend logic accordingly
- **Before merge**: Verify all manual testing checklist items pass

---

## Next Steps / Known Limitations

- [ ] Implement remaining 6 scenarios (S1, S2, S4, S5, S6, S7)
- [ ] Add proper error recovery in SSE streams
- [ ] Implement better conflict detection for S8 (auto-detect contradictory decisions)
- [ ] Deploy to cloud
- [ ] Add more robust tool schema validation
