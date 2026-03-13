# Google Calendar 集成设置指南

本文档介绍如何设置 Google Calendar 自动事件创建功能。

## 功能概述

当用户在聊天中提到日期/时间相关的事件时，系统会自动：
1. 🔍 检测事件意图（如："tomorrow I have a meeting at 8am"）
2. 📅 解析日期、时间和事件标题
3. ✅ 自动在用户的 Google Calendar 中创建事件
4. 💬 AI 回复中确认已创建日历事件

## 支持的自然语言格式

系统可以识别以下类型的表达：

### 日期关键词
- **今天**: "today", "this morning", "this afternoon"
- **明天**: "tomorrow", "tmr", "tmrw"
- **具体日期**: "next Monday", "next week", "on Friday"
- **完整日期**: "January 15", "15th Jan", "2026-01-15"

### 时间格式
- "8am", "8:00am", "8 AM"
- "2:30pm", "14:30", "2:30 PM"
- "at 8", "at 9 o'clock"

### 事件类型
- meeting, appointment, call, conference
- class, lesson, session
- lunch, dinner, breakfast
- party, birthday
- 任何自定义事件名称

### 示例句子
```
✅ "tomorrow I have a meeting at 8am"
✅ "remind me about the dentist appointment at 2pm today"
✅ "schedule a call with John next Monday at 10:30am"
✅ "I have a birthday party on Friday at 7pm"
✅ "team meeting at 3pm tomorrow"
✅ "lunch with Sarah next Tuesday at noon"
```

## Google Cloud Console 设置

### 步骤 1: 创建 Google Cloud 项目

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目或选择现有项目
3. 记录您的项目 ID

### 步骤 2: 启用 Google Calendar API

1. 在 Google Cloud Console 中，导航到 "APIs & Services" > "Library"
2. 搜索 "Google Calendar API"
3. 点击 "Enable" 启用 API

### 步骤 3: 创建 OAuth 2.0 凭据

1. 导航到 "APIs & Services" > "Credentials"
2. 点击 "Create Credentials" > "OAuth client ID"
3. 如果是首次创建，需要先配置 OAuth consent screen：
   - User Type: External
   - App name: Anime Model Chatbot
   - User support email: 您的邮箱
   - Developer contact: 您的邮箱
   - Scopes: 添加 `https://www.googleapis.com/auth/calendar`

4. 创建 OAuth Client ID：
   - Application type: Web application
   - Name: Anime Chatbot Calendar
   - Authorized redirect URIs: 
     - `http://localhost:8000/api/calendar/oauth2callback`
     - 如果部署到生产环境，添加您的生产 URL

5. 下载 JSON 文件，保存为：
   ```
   backend/client_secret_XXXXX.apps.googleusercontent.com.json
   ```
   或
   ```
   backend/credentials/client_secret.json
   ```

### 步骤 4: 配置环境变量

编辑 `backend/.env` 文件（如果不存在，从 `.env.example` 复制）：

```env
GOOGLE_CLIENT_ID=your_client_id_here.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:8000/api/calendar/oauth2callback
```

替换为您从 Google Cloud Console 获取的实际值。

## 安装依赖

运行以下命令安装新的依赖：

```bash
# 进入项目根目录
cd "c:\Users\SeanTeng\Desktop\Anime Model Chatbot"

# 安装 Python 依赖
pip install -r requirements.txt
```

新增的依赖包括：
- `google-auth-oauthlib` - OAuth 认证
- `google-api-python-client` - Google Calendar API 客户端
- `dateparser` - 自然语言日期解析
- `python-dateutil` - 日期工具

## 用户授权流程

### 首次使用

当用户首次尝试创建日历事件时：

1. **自动检测**: 系统检测到事件意图（如 "tmr i have a meeting at 8am"）
2. **授权提示**: 如果用户未授权，后端会跳过事件创建，但仍会正常回复
3. **手动授权**: 用户需要访问授权 URL 完成 Google Calendar 授权

### 获取授权 URL

前端可以调用以下 API 获取授权状态和 URL：

```javascript
// 检查授权状态
const response = await fetch(`http://localhost:8000/api/calendar/status/${userId}`);
const data = await response.json();

if (!data.authorized) {
  // 重定向用户到授权页面
  window.open(data.authorization_url, '_blank');
}
```

### 授权后

- 用户凭据会保存在 `backend/app/static/calendar_tokens/`
- 后续事件创建会自动进行，无需再次授权
- Token 会自动刷新

## API 端点

### 1. 检查授权状态
```
GET /api/calendar/status/{user_id}

Response:
{
  "authorized": true/false,
  "authorization_url": "https://accounts.google.com/..." (if not authorized)
}
```

### 2. 解析事件（测试用）
```
POST /api/calendar/parse-event
Body: {
  "text": "tomorrow I have a meeting at 8am"
}

Response:
{
  "success": true,
  "event": {
    "title": "Meeting",
    "start_time": "2026-02-02T08:00:00",
    "end_time": "2026-02-02T09:00:00"
  }
}
```

### 3. 创建事件
```
POST /api/calendar/create-event/{user_id}
Body: {
  "title": "Team Meeting",
  "start_time": "2026-02-02T08:00:00",
  "end_time": "2026-02-02T09:00:00",
  "description": "Optional description",
  "location": "Optional location"
}
```

### 4. 列出即将到来的事件
```
GET /api/calendar/events/{user_id}?max_results=10

Response:
{
  "success": true,
  "count": 5,
  "events": [...]
}
```

## WebSocket 集成

日历功能已集成到现有的 WebSocket 聊天流程中：

```javascript
// 用户发送消息
ws.send(JSON.stringify({
  text: "tomorrow I have a meeting at 8am"
}));

// 收到 AI 回复（如果创建了事件）
{
  "text": "I understand. I've also added 'Meeting' to your Google Calendar. 📅",
  "emotion": "neutral",
  "calendar_event": {
    "id": "event_id",
    "title": "Meeting",
    "link": "https://calendar.google.com/...",
    "start": "2026-02-02T08:00:00",
    "end": "2026-02-02T09:00:00"
  }
}
```

## 前端实现建议

### 1. 显示授权按钮

在设置页面或首次使用时：

```vue
<template>
  <div v-if="!calendarAuthorized">
    <button @click="authorizeCalendar">
      📅 Connect Google Calendar
    </button>
  </div>
</template>

<script>
async function authorizeCalendar() {
  const response = await fetch(`/api/calendar/status/${userId}`);
  const data = await response.json();
  if (!data.authorized && data.authorization_url) {
    window.open(data.authorization_url, '_blank');
  }
}
</script>
```

### 2. 显示日历事件通知

在聊天界面中，当收到包含 `calendar_event` 的响应时：

```vue
<template>
  <div v-if="message.calendar_event" class="calendar-notification">
    <span class="icon">📅</span>
    <div>
      <strong>Event Added to Calendar</strong>
      <p>{{ message.calendar_event.title }}</p>
      <a :href="message.calendar_event.link" target="_blank">
        View in Google Calendar
      </a>
    </div>
  </div>
</template>
```

### 3. 设置页面显示即将到来的事件

```vue
<template>
  <div class="upcoming-events">
    <h3>Upcoming Events</h3>
    <div v-for="event in upcomingEvents" :key="event.id">
      <strong>{{ event.title }}</strong>
      <span>{{ formatDateTime(event.start) }}</span>
    </div>
  </div>
</template>

<script>
async function loadUpcomingEvents() {
  const response = await fetch(`/api/calendar/events/${userId}?max_results=5`);
  const data = await response.json();
  upcomingEvents.value = data.events;
}
</script>
```

## 测试

### 1. 测试事件解析

```bash
curl -X POST http://localhost:8000/api/calendar/parse-event \
  -H "Content-Type: application/json" \
  -d '{"text": "tomorrow I have a meeting at 8am"}'
```

### 2. 测试授权状态

```bash
curl http://localhost:8000/api/calendar/status/test_user
```

### 3. 通过聊天测试完整流程

在聊天界面中输入：
- "tomorrow I have a meeting at 8am"
- "remind me about the dentist at 2pm today"
- "schedule lunch with Sarah next Friday at noon"

## 故障排除

### 问题 1: "No module named 'dateparser'"

**解决方案**: 安装依赖
```bash
pip install -r requirements.txt
```

### 问题 2: "Client secrets file not found"

**解决方案**: 
1. 确保已从 Google Cloud Console 下载 OAuth 凭据 JSON 文件
2. 将文件放在正确位置：
   - `backend/credentials/client_secret.json` 或
   - `backend/client_secret_XXXXX.apps.googleusercontent.com.json`

### 问题 3: 事件未创建，但 AI 回复正常

**原因**: 用户未授权 Google Calendar 访问

**解决方案**:
1. 检查后端日志，查看是否有 "User not authorized" 消息
2. 调用 `/api/calendar/status/{user_id}` 获取授权 URL
3. 打开授权 URL 完成 Google 授权

### 问题 4: 时间解析不正确

**调试方法**:
1. 使用 `/api/calendar/parse-event` 端点测试解析结果
2. 检查是否使用了支持的日期/时间格式
3. 查看 `event_parser.py` 中的 `time_patterns` 和 `date_keywords`

### 问题 5: OAuth 回调错误

**解决方案**:
1. 确保 Google Cloud Console 中配置了正确的 Redirect URI
2. 检查 `.env` 文件中的 `GOOGLE_REDIRECT_URI` 配置
3. 确保 URI 完全匹配（包括 http/https 和端口）

## 安全注意事项

1. **保护凭据文件**: 
   - 不要将 `client_secret_*.json` 提交到 Git
   - 添加到 `.gitignore`

2. **Token 安全**:
   - 用户 token 存储在 `backend/app/static/calendar_tokens/`
   - 确保此目录不被公开访问
   - 添加到 `.gitignore`

3. **生产环境**:
   - 使用 HTTPS
   - 更新 Redirect URI 为生产域名
   - 考虑使用数据库存储 token 而非文件系统

## 未来增强

可能的功能扩展：

- ✅ 自动创建日历事件
- 🔄 更新/删除现有事件
- 🔔 事件提醒设置
- 📅 显示今天/明天的日程
- 🎯 基于日历的智能回复（"你明天很忙"等）
- 🌐 支持多时区
- 🗓️ 重复事件创建
- 👥 邀请其他参与者

## 相关文件

- `backend/app/services/event_parser.py` - 自然语言事件解析
- `backend/app/services/calendar_service.py` - Google Calendar API 集成
- `backend/app/api/calendar.py` - Calendar API 端点
- `backend/app/api/websockets.py` - WebSocket 集成
- `requirements.txt` - Python 依赖
