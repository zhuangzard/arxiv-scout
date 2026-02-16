# 豆包免费播客生成 — 完整自动化流程

## 概述
通过豆包(doubao.com)网页版AI播客功能，免费将论文PDF生成29分钟双人对话播客。

## 前置条件
- openclaw browser (profile=openclaw) 已登录豆包账号
- Cookie session有效（需定期检查/重新登录）

## 完整流程

### Step 1: 打开豆包新对话
```
browser navigate → https://www.doubao.com/chat/
```

### Step 2: 点击"AI 播客"按钮
```
browser snapshot → 找到 button "AI 播客" → click
```
页面底部出现: `AI 播客 ×` | `上传文件` | `网页链接`

### Step 3: 输入论文PDF直链
在输入框输入 `https://arxiv.org/pdf/{arxiv_id}` 然后回车
```
browser type → textbox → "https://arxiv.org/pdf/2602.09021"
browser press → Enter
```
⚠️ 必须用 `/pdf/` 链接，不是 `/abs/` 链接！
- ✅ `https://arxiv.org/pdf/2602.09021` → 读全文，生成28-29分钟播客
- ❌ `https://arxiv.org/abs/2602.09021` → 只读abstract，生成3分钟

### Step 4: 等待生成完成 (约3-5分钟)
轮询检查时长是否从 `--:--` 变成具体数字（如 `29:15`）
```javascript
// 在browser中执行evaluate，检查页面是否包含具体时长
document.body.innerText.match(/\d{2}:\d{2}\s*\|\s*\d{2}:\d{2}/)
```
或者检查播放按钮和"..."加载指示器消失

### Step 5: 获取 episode_id
通过拦截JSON.stringify捕获下载按钮的episode_id：
```javascript
// 设置拦截器
window.__payloads = [];
const origStringify = JSON.stringify;
JSON.stringify = function(...args) {
  const result = origStringify.apply(this, args);
  if(typeof result === 'string' && result.includes('episode_id')) {
    window.__payloads.push(result);
  }
  return result;
};

// 然后点击下载按钮（class: actionBtn-s0rB0o 或 snapshot中的下载img）
// 读取: window.__payloads → 提取 episode_id
```

### Step 6: 调用API获取签名下载URL
```javascript
const resp = await fetch('/api/doubao/do_action_v2?version_code=20800&language=zh&device_platform=web&aid=497858&real_aid=497858&pkg_type=release_version&samantha_web=1&use-olympus-account=1', {
  method: 'POST',
  credentials: 'include',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    scene: 'FPA_Podcast',
    payload: JSON.stringify({
      api_name: 'GetGenPodcastVideoUrl',
      params: JSON.stringify({episode_id: 'YOUR_EPISODE_ID'})
    })
  })
});
const data = await resp.json();
// data.data.resp → JSON string containing video_url
const videoUrl = JSON.parse(data.data.resp).video_url;
```

### Step 7: 下载WAV文件
```bash
curl -L -o /tmp/podcast.wav "$VIDEO_URL"
# 文件约80MB WAV, 24000Hz, 16bit mono
```

### Step 8: 转换为MP3
```bash
# 高质量版 (~27MB)
ffmpeg -i /tmp/podcast.wav -codec:a libmp3lame -b:a 128k /tmp/podcast_128k.mp3 -y

# Telegram友好版 (<16MB)
ffmpeg -i /tmp/podcast.wav -codec:a libmp3lame -b:a 64k /tmp/podcast_64k.mp3 -y
```

## 关键参数
- **API endpoint**: `POST /api/doubao/do_action_v2`
- **scene**: `FPA_Podcast`
- **api_name**: `GetGenPodcastVideoUrl`
- **下载域名**: `p11-flow-download-sign.byteimg.com`
- **签名URL有效期**: x-expires参数（通常几小时）
- **音频格式**: WAV 24000Hz 16bit mono → 转MP3

## 注意事项
- Cookie session可能过期，需定期检查登录状态
- 签名URL有过期时间，获取后需尽快下载
- 单个conversation只生成一次播客，重新生成需新建对话
- PDF链接必须用arxiv.org/pdf/格式
- Telegram有16MB限制，需用64kbps或更低码率

## 成本
- **完全免费** — 豆包AI播客不消耗token
- 生成时长约3-5分钟/篇
- 输出约28-30分钟双人对话播客

## 验证记录
- 2026-02-16 03:00 — χ₀论文(2602.09021) 成功: 29:15, 80MB WAV → 27MB/13MB MP3
