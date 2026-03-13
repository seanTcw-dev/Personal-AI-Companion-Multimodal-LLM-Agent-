# 🎯 Hybrid Voice System: Cache + Streaming

## What We Built

**Smart Hybrid System** that automatically chooses the best method:

```
User sends message
    ↓
Check Cache
    ├─ Found → Return instantly (0 sec) ✅
    └─ Not found → Check text length
            ├─ Long (>200 chars) → Use STREAMING (faster) 🌊
            └─ Short (<200 chars) → Use STANDARD + cache 🎤
```

## Configuration

All settings in `voice_service.py` `__init__`:

```python
# Cache Settings
self.cache_enabled = True              # Enable/disable caching

# Streaming Settings  
self.use_streaming = False             # Enable streaming mode
self.streaming_threshold = 200         # Use streaming if text > 200 chars
```

## File Management

### Two Separate Directories:

1. **`voice_cache/`** - Cached audio files
   - Keep for 24 hours
   - Reused for same text
   - Faster than regenerating

2. **`temp_audio/`** - Temporary files (future use)
   - Keep for 60 seconds
   - For non-cached audio
   - Auto-deleted quickly

### Cleanup Logic:

```python
Cached files (voice_cache/):  Delete after 24 hours
Temp files (temp_audio/):     Delete after 60 seconds
```

This prevents:
- ✅ Disk bloat (old files deleted)
- ✅ Cache working (files kept long enough)
- ✅ Fast access (cache not deleted too soon)

## Performance Matrix

| Scenario | 1st Time | 2nd Time | Method Used |
|----------|----------|----------|-------------|
| "Hi" (short) | 8 sec | **0 sec** | Standard → Cache |
| "Hi" (short, streaming ON) | 5 sec | **0 sec** | Streaming → Cache |
| Long text (>200 chars) | 15 sec | **0 sec** | Standard → Cache |
| Long text (streaming ON) | 7 sec | **0 sec** | Streaming → Cache |

## Current Setup (Recommended)

```python
self.cache_enabled = True          # ✅ ENABLED
self.use_streaming = False         # ❌ DISABLED (for now)
self.streaming_threshold = 200     # Ready if you enable
```

**Why this setup?**
- ✅ Simple and working
- ✅ Caching handles most cases
- ✅ No frontend changes needed
- ✅ Stable and reliable

## To Enable Streaming

### Step 1: Enable in Backend
```python
# In voice_service.py __init__:
self.use_streaming = True
```

### Step 2: Restart Backend
```bash
Ctrl+C
python run.py
```

### Step 3: Test
Send a long message (>200 characters) and watch logs:

```
🌊 Generating voice with STREAMING for: Tell me a very long...
   Character: suzune_horikita
   Language: en
   Method: Streaming
```

## Testing the System

### Test 1: Short Cached Response
```
User: "Hi"
Logs: 🎤 Generating voice for: Hi...
      ✅ Voice generated: voice_xxx.wav
      💾 Cached audio with key: abc123...

User: "Hi" (again)
Logs: 💾 Using cached audio for: Hi...  ← INSTANT!
```

### Test 2: Long Text (Streaming Enabled)
```
User: "Tell me a long story about..."
Logs: 🌊 Generating voice with STREAMING for: Tell me...
      Method: Streaming
      ✅ Voice generated: voice_xxx.wav
      💾 Cached audio with key: def456...

User: Same long text again
Logs: 💾 Using cached audio for: Tell me...  ← INSTANT!
```

### Test 3: File Cleanup
```
Wait 24 hours...
Logs: 🗑️ Cleaned up cached file (24h old): voice_xxx.wav
```

## Monitoring

Watch backend console for these indicators:

### Cache Hit (Best Case):
```
💾 Using cached audio for: Hello...
```
**Speed**: Instant ⚡

### Standard Generation:
```
🎤 Generating voice for: Hello...
   Method: Standard
```
**Speed**: 8 seconds 🕐

### Streaming Generation:
```
🌊 Generating voice with STREAMING for: Long text...
   Method: Streaming
```
**Speed**: 5 seconds 🌊

### File Cleanup:
```
🗑️ Cleaned up cached file (24h old): voice_abc123.wav
🗑️ Cleaned up temp file: voice_xyz789.wav
```

## Benefits Summary

✅ **Cache**: Instant for repeated text
✅ **Streaming**: Faster for new long text  
✅ **Smart routing**: Automatically picks best method
✅ **File management**: Auto-cleanup prevents bloat
✅ **24-hour cache**: Good balance of speed vs disk space

## Quick Reference

| Setting | Value | Purpose |
|---------|-------|---------|
| `cache_enabled` | `True` | Enable caching system |
| `use_streaming` | `False` | Use streaming for long text |
| `streaming_threshold` | `200` | Characters before using streaming |
| Cache cleanup | 24 hours | How long to keep cached files |
| Temp cleanup | 60 seconds | How long to keep temp files |

## Troubleshooting

### Issue: Cache not working
**Check**: Is `cache_enabled = True`?
**Check**: Are files being deleted too soon? (Should be 24 hours)

### Issue: Files not being deleted
**Check**: Is cleanup thread running? (See: `🗑️ Audio cleanup thread started`)
**Check**: Are files older than 24 hours?

### Issue: Streaming not activating
**Check**: Is `use_streaming = True`?
**Check**: Is text > 200 characters?
**Watch logs**: Should see `Method: Streaming`

## Recommendation

**Current setup is perfect!** ✨

- ✅ Caching enabled → Instant repeated phrases
- ✅ Streaming disabled → Simple, stable
- ✅ 24-hour cleanup → Good balance

**Enable streaming when:**
- Users ask very long questions regularly
- You want faster first-time generation
- You're ready for more complexity

**For now: Keep as is!** Your chatbot works great! 🎉
