# ⚡ Google Calendar 快速设置检查清单

## 📝 5 分钟快速检查

### ✅ 步骤 1: Google Cloud Console (5分钟)
```
1. 访问 https://console.cloud.google.com/
2. 创建新项目 "Anime Chatbot Calendar"
3. 启用 "Google Calendar API"
4. 配置 OAuth consent screen (External)
5. 添加 Scope: .../auth/calendar
6. 添加测试用户（你的Gmail）
7. 创建 OAuth Client ID (Web application)
8. 添加 Redirect URI: http://localhost:8000/api/calendar/oauth2callback
9. 下载 JSON 凭据文件
```

### ✅ 步骤 2: 项目配置 (2分钟)
```powershell
# 1. 移动凭据文件
# 将下载的 client_secret_*.json 放到：
C:\Users\SeanTeng\Desktop\Anime Model Chatbot\backend\

# 2. 编辑 .env 文件
GOOGLE_CLIENT_ID=你的Client_ID.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=你的Client_Secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/calendar/oauth2callback

# 3. 安装依赖
conda activate aniChatbot_final
pip install -r requirements.txt
```

### ✅ 步骤 3: 测试 (2分钟)
```powershell
# 1. 启动后端
cd backend
python run.py

# 2. 测试解析（新窗口）
curl -X POST http://localhost:8000/api/calendar/parse-event `
  -H "Content-Type: application/json" `
  -d '{\"text\": \"tomorrow meeting at 8am\"}'

# 3. 获取授权URL
curl http://localhost:8000/api/calendar/status/test_user

# 4. 打开返回的 authorization_url 完成授权
```

---

## 🔑 关键信息速查

### Google Cloud Console URL
```
https://console.cloud.google.com/
```

### 必须配置的 Redirect URI
```
http://localhost:8000/api/calendar/oauth2callback
```

### 凭据文件位置
```
backend/client_secret_*.json
```

### 环境变量位置
```
backend/.env
```

---

## 🧪 快速测试命令

### 测试 1: 服务器运行
```powershell
curl http://localhost:8000/
```
✅ 应返回: `"status": "online"`

### 测试 2: 事件解析
```powershell
curl -X POST http://localhost:8000/api/calendar/parse-event `
  -H "Content-Type: application/json" `
  -d '{\"text\": \"tomorrow I have a meeting at 8am\"}'
```
✅ 应返回: `"success": true`

### 测试 3: 授权状态
```powershell
curl http://localhost:8000/api/calendar/status/YOUR_USER_ID
```
✅ 未授权: `"authorized": false` + authorization_url
✅ 已授权: `"authorized": true`

---

## 🎯 聊天测试示例

授权后在聊天中输入：

```
✅ tomorrow I have a meeting at 8am
✅ remind me dentist at 2pm today
✅ schedule call next Monday 10:30am
✅ team lunch Friday noon
✅ party next Saturday 7pm
```

应该看到：
- 💬 AI 回复包含 "📅" 图标
- 📅 Google Calendar 中出现新事件
- 🔊 语音确认

---

## ⚠️ 最常见的 3 个问题

### 1. "Redirect URI mismatch"
**修复：** 检查 Google Console 的 Redirect URI 是否完全匹配：
```
http://localhost:8000/api/calendar/oauth2callback
```

### 2. "Access blocked"
**修复：** 在 OAuth consent screen 添加用户为测试用户

### 3. 事件未创建但AI正常回复
**修复：** 用户需要先授权，访问 `/api/calendar/status/{user_id}` 获取授权URL

---

## 📁 文件结构检查

```
backend/
├── client_secret_*.json          ← 必须存在！
├── .env                          ← 配置 GOOGLE_CLIENT_ID 和 SECRET
├── app/
│   ├── services/
│   │   ├── event_parser.py       ← 事件解析
│   │   └── calendar_service.py   ← Calendar API
│   └── api/
│       ├── calendar.py           ← API 端点
│       └── websockets.py         ← 集成到聊天
└── static/
    └── calendar_tokens/          ← 自动创建（用户令牌）
```

---

## 🚀 完整启动命令

```powershell
# 终端 1: 后端
cd "C:\Users\SeanTeng\Desktop\Anime Model Chatbot\backend"
conda activate aniChatbot_final
python run.py

# 终端 2: 前端（可选）
cd "C:\Users\SeanTeng\Desktop\Anime Model Chatbot\frontend"
npm run dev

# 浏览器
http://localhost:5173
```

---

## 📚 详细文档

遇到问题？查看完整指南：
- 📖 [GOOGLE_CALENDAR_详细设置步骤.md](GOOGLE_CALENDAR_详细设置步骤.md) - 逐步截图说明
- 📖 [GOOGLE_CALENDAR_SETUP.md](GOOGLE_CALENDAR_SETUP.md) - 完整技术文档
- 📖 [CALENDAR_QUICKSTART.md](CALENDAR_QUICKSTART.md) - 快速开始

---

**⏱️ 预计总时间: 10-15 分钟**
**🎯 难度: ⭐⭐☆☆☆ (简单)**
