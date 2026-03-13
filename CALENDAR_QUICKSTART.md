# Google Calendar 功能快速入门

## 🎯 快速开始（5分钟设置）

### 1. 安装依赖
```powershell
cd "c:\Users\SeanTeng\Desktop\Anime Model Chatbot"
pip install -r requirements.txt
```

### 2. 获取 Google Calendar API 凭据

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 启用 **Google Calendar API**
3. 创建 **OAuth 2.0 Client ID** (Web application)
4. 添加 Redirect URI: `http://localhost:8000/api/calendar/oauth2callback`
5. 下载 JSON 文件，保存到：
   ```
   backend/client_secret_XXXXX.apps.googleusercontent.com.json
   ```

### 3. 配置环境变量

编辑 `backend/.env`:
```env
GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/calendar/oauth2callback
```

### 4. 启动服务器

```powershell
# 后端
cd backend
python run.py

# 前端（新终端）
cd frontend
npm run dev
```

### 5. 授权 Google Calendar

首次使用前，需要授权：

```powershell
# 检查授权状态
curl http://localhost:8000/api/calendar/status/your_user_id
```

访问返回的 `authorization_url` 完成授权。

## 💬 使用示例

在聊天中输入以下任意句子，系统会自动创建日历事件：

```
✅ "tomorrow I have a meeting at 8am"
✅ "remind me about dentist at 2pm today"  
✅ "schedule a call next Monday at 10:30am"
✅ "team lunch on Friday at noon"
✅ "birthday party next Saturday at 7pm"
```

## 🔍 测试事件解析

```powershell
# 测试自然语言解析
curl -X POST http://localhost:8000/api/calendar/parse-event `
  -H "Content-Type: application/json" `
  -d '{\"text\": \"tomorrow I have a meeting at 8am\"}'
```

## 📱 前端集成（可选）

### 检查授权状态

```javascript
const response = await fetch(`/api/calendar/status/${userId}`);
const { authorized, authorization_url } = await response.json();

if (!authorized) {
  window.open(authorization_url, '_blank');
}
```

### 显示日历事件通知

AI 响应中会包含 `calendar_event` 字段：

```javascript
{
  "text": "Sure! I've added 'Meeting' to your calendar. 📅",
  "emotion": "happy",
  "calendar_event": {
    "id": "event_123",
    "title": "Meeting",
    "link": "https://calendar.google.com/calendar/event?eid=...",
    "start": "2026-02-02T08:00:00",
    "end": "2026-02-02T09:00:00"
  }
}
```

## ⚠️ 常见问题

**Q: 事件没有创建？**
- 检查用户是否已授权（后端日志会显示）
- 测试事件解析 API 确认格式正确

**Q: "Module not found" 错误？**
```powershell
pip install -r requirements.txt
```

**Q: "Client secrets not found" 错误？**
- 确保已从 Google Cloud Console 下载凭据文件
- 文件名应为 `client_secret_XXXXX.json`
- 放在 `backend/` 目录下

## 📚 完整文档

详细设置和 API 文档请参考：
- [GOOGLE_CALENDAR_SETUP.md](GOOGLE_CALENDAR_SETUP.md) - 完整设置指南

## 🎉 就这么简单！

现在用户说 "tmr i have a meeting at 8am"，系统会：
1. ✅ 自动创建 Google Calendar 事件
2. 💬 AI 回复确认已添加到日历
3. 🎤 语音播报确认信息
