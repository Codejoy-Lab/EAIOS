# EAIOS - 企业级Agent操作系统

**演示平台：展示企业级、主动式、带记忆管理的多Agent协同能力**

---

## 🎯 项目简介

EAIOS是一个企业级Agent演示平台，通过10个页面（1个介绍页 + 8个场景页 + 1个结尾页）展示：

- **🧠 企业大脑**：统一口径、自动想起、有据可查的记忆管理
- **⚡ 主动式**：AI主动发现问题、提出建议、推进业务流程
- **🔗 多Agent协同**：真实跑通业务流程，支持关键节点人工确认

---

## 📋 八大场景

| 场景 | 名称 | 主打特性 | 描述 |
|------|------|----------|------|
| S1 | AI全域营销 | 主动式 | 自动营销内容生成与投放建议 |
| S2 | AI智能销售 | 主动式 | 个性化销售跟进与触达 |
| S3 | AI智能客服 | 企业大脑 | 对话式客服，带记忆与来源 |
| S4 | AI内容生产 | 企业大脑 | 企业风格统一的内容生成 |
| S5 | AI全流程优化 | 主动式 | 项目/OKR进度管理与优化 |
| S6 | AI数据分析 | 主动式 | 自动异常检测与行动建议 |
| S7 | AI风控合规 | 企业大脑 | 基于企业红线的合同审查 |
| S8 | AI决策军师 | 企业大脑 | CEO视角的经营简报 |

---

## 🏗️ 技术架构

### 后端
- **框架**: FastAPI (异步Web框架)
- **记忆管理**: Mem0 (AI记忆层)
- **Agent编排**: LangGraph (状态图编排)
- **LLM**: OpenAI GPT-4
- **MCP工具**: Python MCP SDK
- **向量数据库**: ChromaDB / Qdrant

### 前端
- **框架**: React 18
- **构建工具**: Vite
- **路由**: React Router v6
- **状态管理**: Zustand
- **样式**: TailwindCSS
- **HTTP客户端**: Axios

### 项目结构
```
EAIOS/
├── backend/              # 后端
│   ├── app/
│   │   ├── api/         # API路由
│   │   ├── core/        # 核心模块
│   │   │   ├── memory.py      # Mem0记忆管理
│   │   │   ├── agent.py       # Agent编排
│   │   │   ├── mcp.py         # MCP工具
│   │   │   └── llm.py         # LLM调用
│   │   └── main.py      # FastAPI入口
│   ├── data/            # 模拟数据
│   └── requirements.txt
├── frontend/            # 前端
│   ├── src/
│   │   ├── pages/       # 10个页面
│   │   ├── components/  # 通用组件
│   │   └── App.jsx
│   └── package.json
└── README.md
```

---

## 🚀 快速开始

### 前置要求

- Python 3.10+
- Node.js 18+
- OpenAI API Key

### 1. 克隆项目

```bash
cd C:\EAIOS
```

### 2. 后端设置

```bash
cd backend

# 创建虚拟环境（推荐）
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑.env文件，填入你的OpenAI API Key
```

编辑 `.env` 文件：
```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4
```

### 3. 启动后端

```bash
# 在backend目录下
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端启动后访问：
- API文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/api/health

### 4. 前端设置

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端启动后访问：http://localhost:5173

---

## 📖 使用指南

### 记忆管理

1. 访问"记忆管理"页面
2. 添加新记忆（如："公司规定客服必须按照某某流程回答"）
3. 勾选需要启用的记忆
4. 在场景页面中，Agent将自动召回并使用这些记忆

### 场景演示

1. 选择任意场景（S1-S8）
2. 配置数据模式（内置/手动输入）
3. 点击"开始演示"
4. 观察多Agent工作流节点运行
5. 在关键节点进行人工确认
6. 查看输出结果和来源证明

### 记忆与场景联动验证

**验证步骤**：
1. 在记忆管理页面添加："客服必须在回答前先询问客户订单号"
2. 勾选该记忆
3. 进入S3智能客服场景
4. 开始对话
5. 观察：Agent会先询问订单号（符合新记忆规定）
6. 取消勾选该记忆
7. 重新开始对话
8. 观察：Agent直接回答（不受该记忆约束）

---

## 🔧 核心功能说明

### 1. 记忆管理（Mem0）

**特性**：
- ✅ 语义搜索（基于向量数据库）
- ✅ 可勾选/取消勾选（控制是否被Agent召回）
- ✅ 记忆类型：全局/场景/交互
- ✅ 来源溯源（每条记忆附带metadata）

**API接口**：
- `POST /api/memory/add` - 添加记忆
- `POST /api/memory/toggle` - 勾选/取消勾选
- `GET /api/memory/list` - 获取所有记忆
- `POST /api/memory/search` - 搜索记忆
- `DELETE /api/memory/{id}` - 删除记忆

### 2. Agent编排（LangGraph）

**特性**：
- ✅ 状态图编排
- ✅ 节点自动/手动流转
- ✅ 关键节点确认机制
- ✅ 来源证明链追踪

**编排器结构**：
```python
class ScenarioOrchestrator:
    def build_graph(self):
        # 定义节点和边
        workflow.add_node("node1", self.node1_func)
        workflow.add_edge("node1", "node2")
        ...
```

### 3. MCP 工具层（以外部注册为主）

**当前策略（很重要）**：系统主要依赖“外部 MCP Server 动态注册工具”。本地仅保留演示用的占位工具类（`backend/app/core/mcp.py`），真实调用走外部端点。

- 外部端点配置：环境变量 `FEISHU_MCP_URL`
- 后端启动日志会打印“可用工具: [...]”，以外部端点返回为准
- S8 流式接口会将外部工具注入到 OpenAI function calling，运行期按工具返回的 schema 严格调用

验证外部工具：

```bash
# 在项目根目录执行（Windows PowerShell）
python -c "import os,sys,json; sys.path.append('backend'); from app.core.mcp_client import MCPClient; url=os.getenv('FEISHU_MCP_URL',''); print('Endpoint:', url); c=MCPClient(url); tools=c.list_tools(use_cache=False); print(json.dumps([t.model_dump() for t in tools], ensure_ascii=False, indent=2))"
```

对齐前端提示词与工具 schema：
- 请始终以“外部端点实时返回的 schema 为准”，不要使用旧版本地假设
- 例如 `anpaitask` 最新 schema（示例自端点返回，说明字段若有编码异常不影响调用）：

```json
{
  "name": "anpaitask",
  "inputSchema": {
    "title": "assign_task_to_userArguments",
    "type": "object",
    "properties": {
      "taskname": { "type": "string" },
      "openid": { "type": "string" }
    },
    "required": ["taskname", "openid"]
  }
}
```

如需扩展工具（推荐在外部 MCP Server 实现）：
- 在外部服务新增/更新工具与 schema
- 重启/热更新后端将自动读取最新工具列表

#### 本地 MCP（process_http 模式，推荐）

当你的 MCP 只能“本地启动”为一个进程（例如通过 `mcpServers` 配置拉起命令），可使用本项目的本地进程兼容模式：

1) 在 `.env` 中配置：
```env
MCP_MODE=process_http
# 启动 MCP 的命令与参数（args 支持 JSON 数组或空格分隔字符串）
MCP_PROCESS_COMMAND=cmd
MCP_PROCESS_ARGS=["/c","npx","-y","@smithery/cli@latest","run","@Deploya-labs/mcp-resend","--key","<your_key>","--profile","<your_profile>"]

# 本地 MCP 进程启动后提供的 HTTP JSON-RPC 端点（tools/list, tools/call）
MCP_LOCAL_URL=http://127.0.0.1:8787/mcp

# 可选：等待 MCP 就绪的超时秒数（默认 30）
MCP_START_TIMEOUT=30
```

2) 启动后端时，系统会先拉起本地 MCP 进程，再用 `MCP_LOCAL_URL` 初始化 MCP 客户端。

3) 验证：在后端日志中打印“可用工具: [...]”，或使用上文的“验证外部工具”脚本。

### 4. WebSocket实时通信

**用途**：场景执行时实时推送节点状态

**连接地址**：
```
ws://localhost:8000/ws/scenario/{scenario_id}/{client_id}
```

---

## 📊 模拟数据

项目内置了完整的模拟数据（位于`backend/data/`），包括：

- `crm_data.json` - CRM客户、线索、商机数据
- `documents.json` - 企业文档、会议纪要、政策规定
- `analytics.json` - 业务指标、异常检测、改进建议
- `orders.json` - 订单、工单、历史案例
- `marketing.json` - 营销活动、内容日历、渠道洞察

**数据可随时替换为真实数据源**。

---

## 🛠️ 开发指南

### 添加新场景

1. 在`backend/app/core/agent.py`中定义场景编排器：
```python
@register_scenario("S9")
class S9Orchestrator(ScenarioOrchestrator):
    def build_graph(self):
        # 定义场景的状态图
        ...
```

2. 在`frontend/src/pages/`中创建场景页面组件

3. 在路由中注册新场景

### 添加/更新 MCP 工具（外部优先）

1. 在外部 MCP Server 仓库中新增/更新工具与 `inputSchema`
2. 部署或重启外部服务，确保 `FEISHU_MCP_URL` 可访问
3. 本项目无需改后端代码；如前端涉及工具入参提示或表单，请以实时 schema 更新前端逻辑

本地占位实现仅用于演示，不作为生产来源。

### 调试技巧

- **后端日志**：查看终端输出
- **API测试**：访问 http://localhost:8000/docs
- **前端调试**：浏览器开发者工具
- **WebSocket调试**：使用浏览器Network面板

---

## ⚠️ 注意事项

1. **OpenAI API Key**：确保在`.env`中正确配置
2. **FEISHU_MCP_URL**：外部 MCP 端点必须可达，且返回 tools/list、tools/call 标准 JSON-RPC 响应
3. **首次启动 Mem0**：会自动下载嵌入模型（约1-2分钟）
4. **模型选择**：默认使用 `gpt-4`，可改为 `gpt-3.5-turbo` 降低成本
5. **记忆存储**：Mem0 数据存储在本地，重启不会丢失

---

## 🤝 团队协作与提交流程（给新同事）

### 环境配置
- 后端：复制 `.env.example` 为 `.env`，设置 `OPENAI_API_KEY`、`FEISHU_MCP_URL`
- 前端：`npm install` 后 `npm run dev`

### 分支策略
- `main`：受保护分支，保持可演示、可部署
- 开发分支：`feature/<short-desc>`、`fix/<short-desc>`、`docs/<short-desc>`

### 提交规范（建议）
- 使用 Conventional Commits：
  - `feat: ...` 新功能
  - `fix: ...` 修复
  - `docs: ...` 文档
  - `refactor: ...` 重构（无功能变化）
  - `chore: ...` 其他

### 开发步骤（每位同事）
1. 从 `main` 拉最新代码：`git pull origin main`
2. 新建分支：`git checkout -b feature/<short-desc>`
3. 开发与自测：
   - 后端：`uvicorn app.main:app --reload`
   - 前端：`npm run dev`
   - 验证外部 MCP：运行上文“验证外部工具”脚本
4. 提交并推送：`git commit -m "feat: xxx" && git push -u origin <branch>`
5. 发起 PR（目标分支 `main`），填写变更说明与测试步骤

### 代码评审与合并
- 至少 1 名维护者代码审核通过
- CI（如有）通过后，Squash & Merge 到 `main`
- 维护者负责解决冲突与最终合并

### 与外部 MCP 的对齐
- 前端/提示词变更必须以实时工具 schema 为准
- 若外部工具 schema 调整（如新增 `starttime/duetime`），请：
  - 更新前端调用与交互提示
  - 必要时在后端日志中加强校验与报错信息（无需改工具定义）

### 版本发布与演示准备
- 合并前验证：
  - S8 页生成 v1.0 报告是否正常
  - 会议助手写入记忆并触发 `REPORT_UPDATED`
  - 流式对话工具调用的 `tool_call_start/tool_result/tool_error` 能在前端正确呈现
- 演示脚本参考 `S8_SCENARIO_GUIDE.md`

---

## 🔮 下一步计划

- [ ] 实现8个场景的完整Agent逻辑
- [ ] 添加真实LLM调用与流式输出
- [ ] 完善来源证明卡片UI
- [ ] 实现三分屏对比内容
- [ ] 接入真实MCP工具（非模拟数据）
- [ ] 添加录屏兜底方案
- [ ] 部署到云服务器

---

## 📄 许可证

MIT License

---

## 🤝 贡献

欢迎提交Issue和Pull Request！

---

## 📞 联系方式

- 项目地址：C:\EAIOS
- 演示日期：2025年11月5日

---

**祝演示成功！** 🎉
