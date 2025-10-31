# 🌐 LLM多模式配置指南

## 📋 快速切换LLM模式

### 方式1：使用OpenAI（需梯子）
```env
# backend/.env
LLM_MODE=openai
```

### 方式2：使用DeepSeek（国内直连）
```env
# backend/.env
LLM_MODE=deepseek
```

---

## 🚀 DeepSeek注册与配置（5分钟搞定）

### 1️⃣ 注册账号
访问：https://platform.deepseek.com
- 点击"注册"
- 使用邮箱或微信注册
- 新用户送500万tokens免费额度（价值5元）

### 2️⃣ 获取API Key
1. 登录后点击右上角头像
2. 选择"API Keys"
3. 点击"创建新密钥"
4. 复制生成的密钥（格式：`sk-xxx`）

### 3️⃣ 配置到项目
打开 `backend/.env`，填入API Key：
```env
DEEPSEEK_API_KEY=sk-你复制的密钥
```

### 4️⃣ 切换模式
```env
LLM_MODE=deepseek
```

### 5️⃣ 重启后端
```bash
# 停止当前后端（Ctrl+C）
# 重新启动
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

启动日志应显示：
```
🌐 LLM模式: DeepSeek (deepseek-chat) - 国内直连
```

---

## 💰 价格对比

| 模型 | 价格 | 速度 | 需要梯子 |
|-----|------|------|---------|
| OpenAI GPT-4 | $30/百万tokens | ⚡⚡⚡ | ✅ 需要 |
| DeepSeek | ¥1/百万tokens | ⚡⚡⚡ | ❌ 不需要 |

**DeepSeek性价比极高**：
- 1元 = 100万tokens
- 展会演示一天预计花费：< 1元
- 新用户免费500万tokens

---

## 🎯 使用场景建议

### 场景1：开发调试（建议DeepSeek）
```env
LLM_MODE=deepseek
```
- ✅ 国内直连，稳定快速
- ✅ 价格便宜，随便用
- ✅ 团队成员无需配置梯子

### 场景2：展会演示（有梯子）
```env
LLM_MODE=openai
```
- ✅ 最佳效果
- ⚠️ 需要确认现场有梯子

### 场景3：展会演示（没梯子/不确定）
```env
LLM_MODE=deepseek
```
- ✅ 保险方案，100%能用
- ✅ 效果也很好

---

## 🔧 故障排查

### 问题1：DeepSeek报错 "Invalid API Key"
**解决**：
1. 检查 `DEEPSEEK_API_KEY` 是否正确填写
2. 确认API Key前后没有空格
3. 检查DeepSeek账户是否有余额

### 问题2：DeepSeek超时
**解决**：
1. 检查网络连接
2. DeepSeek国内直连，一般不会超时
3. 如果超时，可能是DeepSeek服务故障，切换回OpenAI

### 问题3：想切换回OpenAI
**解决**：
```env
LLM_MODE=openai
```
重启后端即可

---

## 📞 技术支持

- DeepSeek官方文档：https://platform.deepseek.com/docs
- DeepSeek API定价：https://platform.deepseek.com/pricing
