# Google Calendar API 设置完整步骤指南

## 📋 目录
1. [前期准备](#前期准备)
2. [创建 Google Cloud 项目](#步骤-1-创建-google-cloud-项目)
3. [启用 Calendar API](#步骤-2-启用-calendar-api)
4. [配置 OAuth 同意屏幕](#步骤-3-配置-oauth-同意屏幕)
5. [创建 OAuth 2.0 凭据](#步骤-4-创建-oauth-20-凭据)
6. [下载和配置凭据文件](#步骤-5-下载和配置凭据文件)
7. [配置环境变量](#步骤-6-配置环境变量)
8. [安装依赖](#步骤-7-安装依赖)
9. [测试设置](#步骤-8-测试设置)
10. [用户授权流程](#步骤-9-用户授权流程)

---

## 前期准备

### 需要的材料：
- ✅ Google 账号（Gmail）
- ✅ 浏览器（Chrome/Edge/Firefox）
- ✅ 本项目已运行

### 预计时间：
- ⏱️ 15-20 分钟

---

## 步骤 1: 创建 Google Cloud 项目

### 1.1 访问 Google Cloud Console

1. 打开浏览器，访问：
   ```
   https://console.cloud.google.com/
   ```

2. 使用你的 Google 账号登录

### 1.2 创建新项目

1. 点击顶部导航栏的 **项目选择器**（Project Selector）
   - 通常显示为当前项目名称或 "Select a project"
   
2. 在弹出窗口中，点击右上角 **"NEW PROJECT"** (新建项目) 按钮

3. 填写项目信息：
   ```
   Project name (项目名称): Anime Chatbot Calendar
   Organization (组织): 留空（如果是个人账号）
   Location (位置): 留空或选择 "No organization"
   ```

4. 点击 **"CREATE"** (创建) 按钮

5. 等待项目创建完成（通常 10-30 秒）

6. 创建完成后，确保顶部显示的是你新创建的项目名称
   - 如果没有，点击项目选择器切换到新项目

---

## 步骤 2: 启用 Calendar API

### 2.1 进入 API Library

1. 在 Google Cloud Console 左侧菜单中，找到并点击：
   ```
   APIs & Services (API 和服务) > Library (库)
   ```
   
   或者直接访问：
   ```
   https://console.cloud.google.com/apis/library
   ```

### 2.2 搜索并启用 API

1. 在搜索框中输入：
   ```
   Google Calendar API
   ```

2. 点击搜索结果中的 **"Google Calendar API"**

3. 在 API 详情页面，点击蓝色的 **"ENABLE"** (启用) 按钮

4. 等待启用完成（通常几秒钟）

5. 启用成功后，页面会跳转到 API 的概览页面

---

## 步骤 3: 配置 OAuth 同意屏幕

### 3.1 进入 OAuth consent screen

1. 在左侧菜单中，点击：
   ```
   APIs & Services > OAuth consent screen
   ```

### 3.2 选择用户类型

1. 选择 **"External"** (外部)
   - 这允许任何 Google 账号使用你的应用
   - 如果你有 Google Workspace 账号，也可以选择 "Internal"

2. 点击 **"CREATE"** (创建) 按钮

### 3.3 填写应用信息

#### 第 1 页：OAuth consent screen (基本信息)

填写以下必填字段：

1. **App name (应用名称)**:
   ```
   Anime Model Chatbot
   ```

2. **User support email (用户支持电子邮件)**:
   ```
   [你的 Gmail 地址]
   ```

3. **App logo (应用徽标)**: 可选，暂时跳过

4. **App domain (应用域名)**: 可选，暂时跳过

5. **Authorized domains (已获授权的网域)**: 可选，暂时跳过

6. **Developer contact information (开发者联系信息)**:
   ```
   [你的 Gmail 地址]
   ```

7. 点击 **"SAVE AND CONTINUE"** (保存并继续)

#### 第 2 页：Scopes (范围)

1. 点击 **"ADD OR REMOVE SCOPES"** (添加或移除范围) 按钮

2. 在弹出窗口中，找到或搜索：
   ```
   Google Calendar API
   ```

3. 勾选以下范围（Scope）：
   ```
   ✅ .../auth/calendar
   说明: See, edit, share, and permanently delete all the calendars you can access using Google Calendar
   ```

4. 点击 **"UPDATE"** (更新) 按钮

5. 点击 **"SAVE AND CONTINUE"** (保存并继续)

#### 第 3 页：Test users (测试用户)

1. 点击 **"ADD USERS"** (添加用户) 按钮

2. 输入你要测试的 Gmail 地址（可以是你自己的）：
   ```
   your-email@gmail.com
   ```
   
   💡 **重要**: 在发布应用之前，只有这里添加的测试用户才能使用日历功能！

3. 点击 **"ADD"** (添加)

4. 点击 **"SAVE AND CONTINUE"** (保存并继续)

#### 第 4 页：Summary (摘要)

1. 检查信息是否正确

2. 点击 **"BACK TO DASHBOARD"** (返回信息中心)

---

## 步骤 4: 创建 OAuth 2.0 凭据

### 4.1 进入 Credentials 页面

1. 在左侧菜单中，点击：
   ```
   APIs & Services > Credentials (凭据)
   ```

### 4.2 创建 OAuth Client ID

1. 点击顶部的 **"+ CREATE CREDENTIALS"** (创建凭据) 按钮

2. 选择 **"OAuth client ID"**

### 4.3 配置 OAuth Client

1. **Application type (应用类型)**:
   ```
   选择: Web application (网页应用)
   ```

2. **Name (名称)**:
   ```
   Anime Chatbot Calendar Client
   ```

3. **Authorized JavaScript origins (已获授权的 JavaScript 来源)**:
   ```
   http://localhost:8000
   http://localhost:5173
   ```
   
   点击 **"+ ADD URI"** 添加每个 URI

4. **Authorized redirect URIs (已获授权的重定向 URI)**:
   ```
   http://localhost:8000/api/calendar/oauth2callback
   ```
   
   💡 **非常重要**: 这个 URI 必须完全匹配，包括端口号！

5. 点击 **"CREATE"** (创建) 按钮

### 4.4 保存客户端信息

创建成功后，会弹出窗口显示：

```
Your Client ID
[一串很长的字符串].apps.googleusercontent.com

Your Client Secret
[另一串字符串]
```

**❗ 暂时不要关闭这个窗口！**

记下这两个值，或者继续下一步直接下载文件。

---

## 步骤 5: 下载和配置凭据文件

### 5.1 下载 JSON 文件

1. 在刚才的弹窗中，点击 **"DOWNLOAD JSON"** (下载 JSON) 按钮

2. 或者，在 Credentials 页面：
   - 找到你刚创建的 OAuth 2.0 Client ID
   - 点击右侧的 **下载图标** (↓)

3. 文件会保存到你的下载文件夹，文件名类似：
   ```
   client_secret_123456789-abc123.apps.googleusercontent.com.json
   ```

### 5.2 移动文件到项目目录

1. 打开文件资源管理器，找到下载的 JSON 文件

2. 将文件复制到项目的 backend 目录：
   ```
   C:\Users\SeanTeng\Desktop\Anime Model Chatbot\backend\
   ```

3. **保持原文件名**，不要重命名！
   - 正确示例：`client_secret_321691644457-blm788i9mv5jt9qnh0fq93aa7qf4eigu.apps.googleusercontent.com.json`

### 5.3 验证文件位置

在 PowerShell 中运行：

```powershell
cd "C:\Users\SeanTeng\Desktop\Anime Model Chatbot\backend"
ls client_secret*.json
```

应该能看到你的文件列出来。

---

## 步骤 6: 配置环境变量

### 6.1 打开 .env 文件

在 VS Code 中打开：
```
C:\Users\SeanTeng\Desktop\Anime Model Chatbot\backend\.env
```

### 6.2 添加/修改配置

在 `.env` 文件中添加或修改以下内容：

```env
# Google OAuth Configuration
GOOGLE_CLIENT_ID=你的Client_ID.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=你的Client_Secret

# Google Calendar OAuth Redirect URI
GOOGLE_REDIRECT_URI=http://localhost:8000/api/calendar/oauth2callback

# Frontend URL (for CORS)
FRONTEND_URL=http://localhost:5173

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=dolphin-llama3:latest

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

**替换实际值：**
- `GOOGLE_CLIENT_ID`: 从 Google Cloud Console 复制的 Client ID
- `GOOGLE_CLIENT_SECRET`: 从 Google Cloud Console 复制的 Client Secret

### 6.3 保存文件

按 `Ctrl + S` 保存 `.env` 文件

---

## 步骤 7: 安装依赖

### 7.1 激活 Conda 环境

在 PowerShell 中运行：

```powershell
cd "C:\Users\SeanTeng\Desktop\Anime Model Chatbot"
conda activate aniChatbot_final
```

### 7.2 安装 Python 依赖

```powershell
pip install -r requirements.txt
```

等待安装完成，你应该看到类似信息：

```
Successfully installed google-auth-2.23.0 google-auth-oauthlib-1.2.0 
google-auth-httplib2-0.2.0 google-api-python-client-2.108.0 
dateparser-1.2.0 python-dateutil-2.8.2
```

---

## 步骤 8: 测试设置

### 8.1 启动后端服务器

在 PowerShell 中：

```powershell
cd backend
python run.py
```

等待服务器启动，你应该看到：

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
📅 Google Calendar Service initialized
📁 Token directory: ...
```

### 8.2 测试服务器连接

打开新的 PowerShell 窗口，运行：

```powershell
curl http://localhost:8000/
```

应该返回：

```json
{
  "message": "Anime Model Chatbot Backend is running!",
  "ai_provider": "ollama",
  "status": "online"
}
```

### 8.3 测试事件解析

```powershell
curl -X POST http://localhost:8000/api/calendar/parse-event `
  -H "Content-Type: application/json" `
  -d '{\"text\": \"tomorrow I have a meeting at 8am\"}'
```

应该返回类似：

```json
{
  "success": true,
  "message": "Event information extracted",
  "event": {
    "title": "Meeting",
    "start_time": "2026-02-02T08:00:00",
    "end_time": "2026-02-02T09:00:00"
  }
}
```

✅ 如果看到这个结果，说明事件解析功能正常！

### 8.4 测试授权状态

```powershell
curl http://localhost:8000/api/calendar/status/test_user
```

应该返回：

```json
{
  "authorized": false,
  "authorization_url": "https://accounts.google.com/o/oauth2/auth?..."
}
```

✅ 正常！因为还没有授权。

---

## 步骤 9: 用户授权流程

### 9.1 获取授权 URL

方法 1：使用上一步的 `authorization_url`

方法 2：在浏览器中访问：
```
http://localhost:8000/api/calendar/status/YOUR_USER_ID
```

将返回的 JSON 中的 `authorization_url` 复制出来。

### 9.2 完成 Google 授权

1. **复制授权 URL** 到浏览器地址栏

2. **选择 Google 账号** 进行登录
   - 必须是在 OAuth consent screen 中添加为测试用户的账号

3. **看到警告页面**：
   ```
   Google hasn't verified this app
   ```
   
   这是正常的！因为应用还在测试阶段。
   
4. **点击 "Advanced" (高级)** 或 "继续"

5. **点击 "Go to Anime Model Chatbot (unsafe)"** 或 "继续访问 Anime Model Chatbot（不安全）"

6. **授权页面**：
   ```
   Anime Model Chatbot wants to access your Google Account
   
   This will allow Anime Model Chatbot to:
   • See, edit, share, and permanently delete all the calendars 
     you can access using Google Calendar
   ```

7. **点击 "Continue" (继续)** 或 "允许"

8. **授权成功**：
   - 页面会重定向到 `http://localhost:8000/api/calendar/oauth2callback?code=...`
   - 显示 "Authorization successful" 或类似消息

### 9.3 验证授权

在 PowerShell 中再次检查授权状态：

```powershell
curl http://localhost:8000/api/calendar/status/YOUR_USER_ID
```

现在应该返回：

```json
{
  "authorized": true,
  "authorization_url": null
}
```

✅ **完美！授权成功！**

---

## 步骤 10: 完整测试（聊天中创建事件）

### 10.1 启动前端

在新的 PowerShell 窗口：

```powershell
cd "C:\Users\SeanTeng\Desktop\Anime Model Chatbot\frontend"
npm run dev
```

打开浏览器访问：
```
http://localhost:5173
```

### 10.2 在聊天中测试

在聊天框中输入：

```
tomorrow I have a meeting at 8am
```

### 10.3 预期结果

✅ AI 应该回复类似：

```
I understand. I've also added 'Meeting' to your Google Calendar. 📅
```

✅ 后端日志应该显示：

```
📅 Event detected: Meeting at 2026-02-02T08:00:00
✅ Calendar event created: https://calendar.google.com/calendar/event?eid=...
```

✅ 在 Google Calendar 中检查：
- 打开 https://calendar.google.com
- 应该能看到明天 8am 的 "Meeting" 事件

---

## 🎉 完成！

你已经成功设置了 Google Calendar 集成！

### 测试其他自然语言格式：

```
✅ "remind me about dentist at 2pm today"
✅ "schedule a call next Monday at 10:30am"
✅ "team lunch on Friday at noon"
✅ "birthday party next Saturday at 7pm"
```

---

## ⚠️ 常见问题排查

### 问题 1: "Google hasn't verified this app"

**原因**: 应用在测试模式，未发布

**解决**: 
- 点击 "Advanced" > "Go to app (unsafe)"
- 或在 OAuth consent screen 中添加用户为测试用户

### 问题 2: "Redirect URI mismatch"

**原因**: Redirect URI 配置不匹配

**解决**:
1. 检查 Google Cloud Console 中的 Authorized redirect URIs
2. 确保完全匹配：`http://localhost:8000/api/calendar/oauth2callback`
3. 检查 `.env` 文件中的 `GOOGLE_REDIRECT_URI`

### 问题 3: 事件没有创建

**检查清单**:
- ✅ 用户已授权？运行 `/api/calendar/status/{user_id}` 检查
- ✅ 后端日志显示 "Event detected"？
- ✅ Client Secret 文件存在于 `backend/` 目录？
- ✅ `.env` 文件配置正确？

### 问题 4: "Access blocked: Authorization Error"

**原因**: 用户未添加为测试用户

**解决**:
1. 回到 Google Cloud Console
2. APIs & Services > OAuth consent screen
3. 在 "Test users" 部分添加用户邮箱

### 问题 5: Module import 错误

```powershell
# 重新安装依赖
pip install --upgrade -r requirements.txt
```

---

## 📞 获取帮助

如果遇到问题：

1. 检查后端日志（运行 `python run.py` 的终端）
2. 检查浏览器控制台（F12）
3. 查看 Google Cloud Console 的 Error Reporting
4. 参考 [GOOGLE_CALENDAR_SETUP.md](GOOGLE_CALENDAR_SETUP.md) 了解更多细节

---

## 🔐 安全提醒

**永远不要提交以下文件到 Git：**
- ✋ `client_secret_*.json` - OAuth 凭据文件
- ✋ `.env` - 环境变量（包含密钥）
- ✋ `calendar_tokens/` - 用户授权令牌

已经添加到 `.gitignore` 中，但请务必注意！

---

## 🎓 进阶配置

### 发布应用（移除测试模式警告）

要移除 "Google hasn't verified this app" 警告：

1. 完善 OAuth consent screen 信息
2. 准备隐私政策和服务条款页面
3. 提交应用进行 Google 验证
4. 等待审核（可能需要几周）

**目前测试阶段不需要！**

### 生产环境配置

部署到生产环境时：

1. 使用 HTTPS
2. 更新 Authorized redirect URIs 为生产域名
3. 使用环境变量管理密钥
4. 考虑使用数据库存储令牌

---

**🎊 恭喜！你已经完全掌握 Google Calendar API 的设置！**
