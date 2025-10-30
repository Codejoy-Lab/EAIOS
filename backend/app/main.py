"""
FastAPI Main Application
企业级Agent平台主入口
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

# 导入API路由
from app.api import memory, scenarios, health, s8_decision

# 导入核心模块
from app.core.memory import MemoryManager
from app.core.llm import LLMClient
from app.core.mcp_client import MCPClient
from app.core.state import app_state, get_app_state

# 加载环境变量
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    print("🚀 启动企业级Agent平台...")

    # 初始化记忆管理器
    app_state.memory_manager = MemoryManager()
    print("✅ 记忆管理器初始化完成")

    # 初始化LLM客户端
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("⚠️  警告: OPENAI_API_KEY 未设置")
    app_state.llm_client = LLMClient(api_key=openai_key)
    print("✅ LLM客户端初始化完成")

    # 初始化MCP客户端（飞书任务）
    feishu_mcp_url = os.getenv("FEISHU_MCP_URL", "http://8.219.250.187:8004/e/65p7h5nxfvjrniix/mcp")
    try:
        app_state.mcp_client = MCPClient(feishu_mcp_url)
        # 测试连接并获取可用工具
        tools = app_state.mcp_client.list_tools()
        print(f"✅ MCP客户端初始化完成，可用工具: {[t.name for t in tools]}")
    except Exception as e:
        print(f"⚠️  警告: MCP客户端初始化失败: {e}")
        app_state.mcp_client = None

    print("🎉 平台启动成功！")

    yield

    # 关闭时清理
    print("👋 关闭平台...")


# 创建FastAPI应用
app = FastAPI(
    title="EAIOS - 企业级Agent平台",
    description="演示企业级、主动式、带记忆管理的多Agent协同平台",
    version="1.0.0",
    lifespan=lifespan
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 根路由
@app.get("/")
async def root():
    """根路由"""
    return {
        "message": "欢迎使用EAIOS - 企业级Agent平台",
        "version": "1.0.0",
        "docs": "/docs"
    }


# 注册路由
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(memory.router, prefix="/api/memory", tags=["Memory"])
app.include_router(scenarios.router, prefix="/api/scenarios", tags=["Scenarios"])
app.include_router(s8_decision.router, prefix="/api/s8", tags=["S8-Decision"])


# WebSocket连接管理
class ConnectionManager:
    """WebSocket连接管理器"""
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def send_message(self, message: dict, client_id: str):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)


manager = ConnectionManager()


@app.websocket("/ws/scenario/{scenario_id}/{client_id}")
async def websocket_endpoint(websocket: WebSocket, scenario_id: str, client_id: str):
    """
    场景执行WebSocket
    用于实时推送Agent节点状态
    """
    await manager.connect(websocket, client_id)

    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_json()
            action = data.get("action")

            if action == "start":
                # 启动场景
                await manager.send_message({
                    "type": "scenario_started",
                    "scenario_id": scenario_id,
                    "message": f"场景 {scenario_id} 已启动"
                }, client_id)

                # TODO: 这里将来会调用Agent编排引擎
                # orchestrator = ScenarioOrchestrator(scenario_id, app_state.memory_manager)
                # await orchestrator.run(websocket, data.get("input"))

            elif action == "confirm":
                # 用户确认某个节点
                node_id = data.get("node_id")
                await manager.send_message({
                    "type": "node_confirmed",
                    "node_id": node_id
                }, client_id)

    except WebSocketDisconnect:
        manager.disconnect(client_id)
        print(f"客户端 {client_id} 断开连接")
    except Exception as e:
        print(f"WebSocket错误: {e}")
        manager.disconnect(client_id)


# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "服务器内部错误",
            "detail": str(exc)
        }
    )




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )
