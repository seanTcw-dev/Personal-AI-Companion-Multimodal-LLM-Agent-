# 🎤 自定义声音上传功能使用指南

## ✨ 功能概述

现在你可以让用户上传自己的音频文件，并用它来克隆声音！用户可以：
1. 📤 上传自定义音频文件（MP3, WAV, OGG, FLAC）
2. 🧪 测试自定义声音（输入文本生成语音）
3. ✅ 应用到角色（替换默认的Suzune声音）

---

## 🎯 使用流程

### 1. 进入Voice Settings
```
前端: http://localhost:5173
点击侧边栏 → Voice Settings
```

### 2. 上传音频文件

**步骤：**
1. 点击上传区域
2. 选择音频文件（MP3, WAV, OGG, FLAC）
3. 等待上传完成（会显示 ✅ 成功消息）

**推荐的音频要求：**
- ✅ 清晰、无背景噪音
- ✅ 3-10秒长度
- ✅ 单个说话人
- ✅ 文件大小 < 10MB
- ✅ 包含完整句子（不要只有单词）

**示例好的音频：**
```
"Hello, my name is Alice. I'm happy to help you today!"
```

**示例不好的音频：**
```
"Hi" (太短)
"呃... 嗯... 那个..." (太多填充词)
(有背景音乐或噪音)
```

### 3. 测试声音

**步骤：**
1. 在文本框输入测试文本
2. 点击 "Test Voice"
3. 等待生成（5-15秒）
4. 听播放效果

**测试文本建议：**
```
短句: "Hello! How are you today?"
长句: "I can help you with many different tasks. Just let me know what you need!"
特殊: "你好！我是你的AI助手。"（测试中文）
```

### 4. 应用到角色

**步骤：**
1. 满意测试效果后，点击 "Apply Voice to 3D Model"
2. 确认对话框
3. ✅ 应用成功！

**效果：**
- 之后所有AI对话都会使用这个自定义声音
- 替换原来的Suzune Horikita声音
- 立即生效，无需重启

---

## 🔧 技术细节

### API Endpoints

#### 1. 上传音频
```http
POST /api/voice/upload
Content-Type: multipart/form-data

Body: file (audio file)

Response:
{
  "status": "success",
  "character_id": "custom_abc12345",
  "filename": "my_voice.mp3"
}
```

#### 2. 测试声音
```http
POST /api/voice/test-custom
Content-Type: multipart/form-data

Body:
  character_id: "custom_abc12345"
  text: "Hello world"

Response:
{
  "status": "success",
  "audio_url": "/api/voice/audio/voice_xyz.wav"
}
```

#### 3. 应用声音
```http
POST /api/voice/apply-custom
Content-Type: multipart/form-data

Body:
  character_id: "custom_abc12345"

Response:
{
  "status": "success",
  "message": "Custom voice applied successfully"
}
```

---

## 📁 文件存储

### 目录结构
```
backend/app/static/
├── voices/
│   ├── suzune_horikita.mp3      # 原始默认声音
│   ├── custom_abc12345.mp3      # 用户1的声音
│   ├── custom_def67890.wav      # 用户2的声音
│   └── ...
├── voice_cache/                  # 生成的音频缓存
└── temp_audio/                   # 临时音频文件
```

### 文件命名
```python
character_id = f"custom_{uuid.uuid4().hex[:8]}"
# 示例: custom_a1b2c3d4

voice_filename = f"{character_id}.mp3"
# 示例: custom_a1b2c3d4.mp3
```

---

## 🎭 工作原理

### 上传流程
```
用户选择文件
    ↓
前端上传到 /api/voice/upload
    ↓
保存到 backend/app/static/voices/
    ↓
生成 character_id
    ↓
添加到 voice_service.characters 字典
    ↓
返回 character_id 给前端
```

### 测试流程
```
用户输入测试文本
    ↓
前端调用 /api/voice/test-custom
    ↓
voice_service 使用 character_id
    ↓
首次使用: 计算 embeddings (2-5秒)
    ↓
生成测试音频 (5-10秒)
    ↓
返回音频 URL
    ↓
前端自动播放
```

### 应用流程
```
用户点击 Apply
    ↓
前端调用 /api/voice/apply-custom
    ↓
voice_service.set_active_custom_voice()
    ↓
设置 active_custom_character = character_id
    ↓
后续所有对话使用此声音
```

### 缓存机制
```
首次使用自定义声音:
  - 读取音频文件
  - 计算 gpt_cond_latent + speaker_embedding
  - 缓存到内存

后续使用:
  - 直接使用缓存的 embeddings
  - 不再读取音频文件
  - 瞬间完成!
```

---

## 🔄 切换声音

### 使用默认声音
```python
# 在后端手动切换
voice_service.active_custom_character = None
# 现在使用 suzune_horikita
```

### 使用自定义声音
```python
# 通过 /api/voice/apply-custom 自动设置
voice_service.active_custom_character = "custom_abc12345"
```

### 检查当前声音
```python
active = voice_service.get_active_character()
# 返回: "custom_abc12345" 或 "suzune_horikita"
```

---

## 🐛 故障排除

### 上传失败

**问题: "Invalid file type"**
- 检查文件格式：只支持 MP3, WAV, OGG, FLAC
- 确保文件扩展名正确

**问题: "File too large"**
- 文件最大 10MB
- 压缩音频或裁剪长度

**问题: "Upload error"**
- 检查后端是否运行
- 检查 `backend/app/static/voices/` 目录权限

### 测试失败

**问题: "Voice generation failed"**
- 检查 XTTS 模型是否加载
- 查看后端控制台错误
- 确保音频文件质量良好

**问题: "Audio won't play"**
- 检查浏览器控制台
- 确认后端返回了 audio_url
- 尝试直接访问音频 URL

### 应用失败

**问题: "Character not found"**
- character_id 不存在
- 重新上传音频文件

---

## 💡 最佳实践

### 音频录制建议

1. **使用好的麦克风**
   - 清晰度很重要
   - 避免手机内置麦克风

2. **安静环境**
   - 无背景噪音
   - 关闭风扇、空调

3. **自然语调**
   - 正常说话速度
   - 清晰发音
   - 表达情感

4. **多样化内容**
   - 包含不同音调
   - 长句和短句
   - 示例："Hello! I'm very excited to help you today. What would you like to know?"

### 测试建议

1. **测试不同文本**
   ```
   短句: "Hello!"
   长句: "This is a longer sentence to test the quality."
   中文: "你好，我是AI助手。"
   问句: "How are you doing today?"
   感叹: "That's amazing!"
   ```

2. **听完整段落**
   - 确保声音一致性
   - 检查音调自然度
   - 确认情感表达

3. **与原声对比**
   - 先测试原 Suzune 声音
   - 再测试自定义声音
   - 对比质量

---

## 📊 性能

### 时间成本

| 操作 | GPU | CPU | 说明 |
|------|-----|-----|------|
| 上传 | 1-2秒 | 1-2秒 | 网络传输 |
| 首次embeddings | 2-5秒 | 5-10秒 | 只一次 |
| 首次生成 | 3-5秒 | 10-15秒 | 包含embeddings |
| 后续生成 | 2-3秒 | 8-12秒 | 使用缓存embeddings |

### 存储成本

| 项目 | 大小 | 说明 |
|------|------|------|
| 原始音频 | 500KB - 5MB | 用户上传 |
| 生成音频 | 200KB - 1MB | 每条对话 |
| Embeddings | ~10MB | 内存中 |

---

## 🎉 使用示例

### 完整演示

```
用户操作流程:

1. 打开 Voice Settings
   
2. 上传 alice_voice.mp3 (5秒, 清晰女声)
   → ✅ "Voice uploaded successfully!"
   → character_id: custom_a1b2c3d4

3. 输入测试文本: "Hello! I'm Alice, your AI assistant."
   → 点击 "Test Voice"
   → 生成中... (8秒)
   → 🔊 播放测试音频
   → 满意效果！

4. 点击 "Apply Voice to 3D Model"
   → 确认对话框
   → ✅ "Voice applied successfully!"

5. 返回 Chat
   → 发送: "Hi"
   → AI回复: "Hello! How can I help you?"
   → 🔊 使用 Alice 的声音!

后续所有对话都用 Alice 的声音 ✨
```

---

## 🚀 未来改进

可能的扩展功能：

1. **多角色管理**
   - 保存多个自定义声音
   - 随时切换不同角色
   - 角色库管理

2. **声音预览**
   - 上传前试听原始音频
   - 显示音频波形
   - 音质分析

3. **批量测试**
   - 一次测试多个文本
   - 对比不同效果
   - 导出测试音频

4. **声音调整**
   - 音调调整 (pitch)
   - 语速调整 (speed)
   - 音量控制

5. **云端存储**
   - 上传到云端
   - 跨设备同步
   - 分享声音配置

---

**功能已完成，可以开始使用！🎉**
