# EAIOS 快速启动指南

## ✅ 当前状态

前后端已成功启动！

```
🌐 前端: http://localhost:5173
🔌 后端: http://localhost:8000
📚 API文档: http://localhost:8000/docs
```

## 🚀 快速开始

### 1. 打开应用
浏览器访问：**http://localhost:5173**

### 2. 体验核心场景

#### ✨ S3 智能客服（推荐首先体验）
- 点击"S3智能客服"进入
- 支持3个客户切换：张伟、李娜、王强
- 功能：
  - 💬 实时聊天（带流式输出）
  - 📚 知识库管理（自动分类）
  - 📊 Dashboard 实时统计
  - 🔄 客户历史隔离
  - 📢 新品自动推送

#### 🎯 S8 决策军师（展示Agent复杂度）
- 点击"S8决策军师"进入
- 功能：
  - 🔧 多轮MCP工具调用（最多10轮）
  - 📈 实时流式输出事件
  - 💾 自动记忆保存（企业信息）
  - 🗣️ 会议助手集成
  - 📊 Agent状态可视化

#### 📝 记忆管理
- 点击"记忆管理"
- 可添加企业规则、客服流程等
- 支持启用/禁用/删除记忆

### 3. 其他场景
S1-S2, S4-S7 目前仅有UI框架，暂无后端逻辑

---

## 🔧 API 接口速查

### 健康检查
```bash
curl http://localhost:8000/api/health
```

### S3 客服对话（SSE流式）
```bash
curl -X POST http://localhost:8000/api/s3/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"customer_id": "U001", "message": "你好"}'
```

### S3 知识库列表
```bash
curl http://localhost:8000/api/s3/kb/list
```

### S8 决策对话（SSE流式，支持工具调用）
```bash
curl -X POST http://localhost:8000/api/s8/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "帮我分析今年的销售趋势"}'
```

### 全局内存管理
```bash
# 列出所有记忆
curl http://localhost:8000/api/memory/list

# 添加记忆
curl -X POST http://localhost:8000/api/memory/add \
  -H "Content-Type: application/json" \
  -d '{
    "content": "客服必须礼貌待人",
    "memory_type": "global"
  }'
```

---

## ⚙️ 配置说明

### 环境变量（`.env`）

```env
# OpenAI 配置
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4

# 服务器
HOST=0.0.0.0
PORT=8000

# MCP 工具（可选）
FEISHU_MCP_URL=http://8.219.250.187:8004/e/65p7h5nxfvjrniix/mcp
```

**更新 API Key 的方法：**
1. 编辑 `backend/.env`
2. 替换 `OPENAI_API_KEY` 为真实密钥
3. 后端会自动重加载

---

## 📊 后端服务状态

### 已加载的模块
- ✅ Mem0 记忆管理（本地 Qdrant 向量库）
- ✅ OpenAI LLM 客户端（流式 + 非流式）
- ✅ MCP 工具客户端（已加载工具：`anpaitask`）
- ✅ FastAPI + SSE 流式支持
- ✅ CORS 中间件

### 已禁用的功能（临时）
- ⚠️ S3 内存搜索功能（避免 Mem0 超时）
- ⚠️ S3 自动记忆保存（等待 Mem0 稳定化）

---

## 🧪 测试流程

### 1. 测试 S3 智能客服
```
1. 打开 http://localhost:5173
2. 点击"S3智能客服"
3. 确认选中"张伟"（U001）
4. 输入："你好，我想了解产品"
5. 观察：
   - 应该收到AI回复
   - Dashboard 数据增加
```

### 2. 测试 S8 决策军师
```
1. 点击"S8决策军师"
2. 点击右上角"开始演示"
3. 输入："请帮我安排三个任务：优化营销、降低成本、提升质量"
4. 观察：
   - 实时流式输出
   - 工具调用状态（calling → success）
   - 自动记忆保存
```

### 3. 测试记忆管理
```
1. 点击"记忆管理"
2. 添加："客服必须先询问订单号"
3. 勾选启用
4. 回到 S3，开始新对话
5. 观察：AI 是否遵循新规则
```

---

## 📋 项目结构概览

```
EAIOS-main/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── s3_customer_service.py  (完全实现)
│   │   │   ├── s8_decision.py          (完全实现)
│   │   │   ├── memory.py               (全局记忆)
│   │   │   └── ...
│   │   └── core/
│   │       ├── memory.py               (Mem0管理器)
│   │       ├── llm.py                  (LLM客户端)
│   │       ├── mcp_client.py           (工具调用)
│   │       └── ...
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── S3CustomerService.jsx   (21KB, 完全实现)
│   │   │   ├── S8Decision.jsx          (29KB, 完全实现)
│   │   │   └── ...
│   │   └── components/
│   └── package.json
│
└── CLAUDE.md                           (开发指南)
```

---

## 🐛 常见问题

### Q: 后端启动报错？
**A:** 检查 Python 版本（需要 3.10+）和依赖安装：
```bash
cd backend
pip install -r requirements.txt
```

### Q: 前端无法连接后端？
**A:** 检查 CORS 配置，确保后端运行在 `:8000`

### Q: 对话没有 AI 回复？
**A:** 检查 `OPENAI_API_KEY` 是否正确，使用真实密钥替换演示密钥

### Q: Mem0 初始化很慢？
**A:** 首次运行会下载嵌入模型（~1-2分钟），之后速度会快

### Q: S3 历史要点无法显示？
**A:** Mem0 搜索功能临时禁用，等待稳定化后会启用

---

## 📝 下一步

1. **替换真实 API Key**
   - 编辑 `backend/.env`
   - 设置 `OPENAI_API_KEY`

2. **测试完整流程**
   - S3：多客户切换 → 聊天 → 知识库 → 推送
   - S8：对话 → 工具调用 → 记忆保存

3. **快速补全其他场景**（S1-S2, S4-S7）
   - 预计 2-3 天完成基础实现

4. **修复 Mem0 集成**（可选）
   - 启用 S3 内存搜索
   - 验证客户隔离

---

## 🆘 需要帮助？

- 查看 `CLAUDE.md` 了解架构和调试技巧
- 访问 http://localhost:8000/docs 查看完整 API 文档
- 检查后端日志（终端输出）

---

**祝你体验愉快！** 🎉
