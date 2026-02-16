#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
volcengine-podcast.py v3 - 火山引擎豆包·播客语音合成
基于官方SDK协议库，保证二进制帧正确性

用法:
  python3 volcengine-podcast.py --text script.txt -o output.mp3
  python3 volcengine-podcast.py --topic "火山引擎" -o output.mp3
  python3 volcengine-podcast.py --url "https://arxiv.org/abs/..." -o output.mp3
  python3 volcengine-podcast.py --raw report.md -o output.mp3

环境变量: VOLC_APP_ID, VOLC_ACCESS_KEY
依赖: pip3 install websockets
"""

import asyncio, json, sys, os, re, uuid, argparse, time, logging

try:
    import websockets
except ImportError:
    print("❌ pip3 install websockets"); sys.exit(1)

# Import official protocol library (same directory)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from volc_protocols import (
    EventType, MsgType, Message, MsgTypeFlagBits,
    start_connection, finish_connection,
    start_session, finish_session,
    receive_message, wait_for_event,
)

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("podcast")

# ── 常量 ──
WS_URL = "wss://openspeech.bytedance.com/api/v3/sami/podcasttts"
RESOURCE_ID = "volc.service_type.10050"
APP_KEY = "aGjiRDfUWi"

# 发音人
SPEAKERS = {
    'dayi': {
        'name': '黑猫侦探社(大意先生+咪仔同学)',
        'a': 'zh_male_dayixiansheng_v2_saturn_bigtts',
        'b': 'zh_female_mizaitongxue_v2_saturn_bigtts',
    },
    'liufei': {
        'name': '刘飞+潇磊',
        'a': 'zh_male_liufei_v2_saturn_bigtts',
        'b': 'zh_male_xiaolei_v2_saturn_bigtts',
    },
}


# ════════════════════════════════════════
# 对话文稿解析
# ════════════════════════════════════════

def parse_podcast_script(text, speaker_a, speaker_b):
    """解析A:/B:格式的播客文稿为nlp_texts格式"""
    turns = []
    speaker_map = {}
    
    pattern = re.compile(
        r'^(?:([AB])\s*[:：]|【([^】]+)】|(\*\*[^*]+\*\*)\s*[:：]|([^\s:：]{1,10})\s*[:：])\s*(.*)',
    )
    
    lines = text.strip().split('\n')
    current_speaker = None
    current_text = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        m = pattern.match(line)
        if m:
            if current_speaker and current_text:
                turns.append({'speaker': current_speaker, 'text': ''.join(current_text)})
            
            raw = (m.group(1) or m.group(2) or m.group(3) or m.group(4)).strip('* ')
            if raw.upper() in ('A', '主持人A', '甲'):
                current_speaker = speaker_a
            elif raw.upper() in ('B', '主持人B', '乙'):
                current_speaker = speaker_b
            else:
                if raw not in speaker_map:
                    speaker_map[raw] = speaker_a if len(speaker_map) == 0 else speaker_b
                current_speaker = speaker_map[raw]
            
            content = (m.group(5) or '').strip()
            current_text = [content] if content else []
        else:
            if current_speaker:
                current_text.append(line)
    
    if current_speaker and current_text:
        turns.append({'speaker': current_speaker, 'text': ''.join(current_text)})
    
    return turns


def build_nlp_texts(turns):
    """转换为API nlp_texts格式，单轮≤300字，总计≤10000字"""
    nlp_texts = []
    for turn in turns:
        text = turn['text'].strip()
        if not text:
            continue
        speaker = turn['speaker']
        
        if len(text) <= 300:
            nlp_texts.append({'text': text, 'speaker': speaker})
        else:
            for chunk in _split_text(text, 280):
                nlp_texts.append({'text': chunk, 'speaker': speaker})
    
    total = sum(len(t['text']) for t in nlp_texts)
    if total > 10000:
        print(f"⚠️  {total}字→截断到10000字")
        trimmed, running = [], 0
        for t in nlp_texts:
            if running + len(t['text']) > 9800:
                break
            trimmed.append(t)
            running += len(t['text'])
        nlp_texts = trimmed
    
    return nlp_texts


def _split_text(text, max_len):
    """按句子拆分"""
    chunks, chunk = [], ''
    for piece in re.split(r'([。！？!?\n])', text):
        if len(chunk) + len(piece) > max_len and chunk:
            chunks.append(chunk)
            chunk = piece
        else:
            chunk += piece
    if chunk:
        chunks.append(chunk)
    return chunks


# ════════════════════════════════════════
# 播客生成（基于官方SDK协议）
# ════════════════════════════════════════

async def generate_podcast(req_params, app_id, access_key, output_path, verbose=False):
    """
    完整流程 (参照官方demo):
    1. Connect → StartConnection → ConnectionStarted
    2. StartSession(payload) → SessionStarted
    3. FinishSession (立刻发!)
    4. 循环接收: RoundStart → RoundResponse(audio) → RoundEnd
    5. PodcastEnd → SessionFinished
    6. FinishConnection → ConnectionFinished
    支持断点续传 (retry)
    """
    
    headers = {
        "X-Api-App-Id": app_id,
        "X-Api-App-Key": APP_KEY,
        "X-Api-Access-Key": access_key,
        "X-Api-Resource-Id": RESOURCE_ID,
        "X-Api-Connect-Id": str(uuid.uuid4()),
    }
    
    podcast_audio = bytearray()
    round_count = 0
    current_round = 0
    last_round_id = -1
    task_id = ""
    is_round_end = True
    retry_num = 5
    start_time = time.time()
    
    print(f"🔗 连接火山引擎播客TTS...")
    
    try:
        while retry_num > 0:
            ws = await websockets.connect(WS_URL, additional_headers=headers)
            
            # 断点续传
            if not is_round_end and task_id:
                req_params["retry_info"] = {
                    "retry_task_id": task_id,
                    "last_finished_round_id": last_round_id
                }
                print(f"   🔄 断点续传: 从轮次{last_round_id}继续")
            
            # 1. StartConnection → ConnectionStarted
            await start_connection(ws)
            await wait_for_event(ws, MsgType.FullServerResponse, EventType.ConnectionStarted)
            print(f"   ✅ 连接建立")
            
            # 2. StartSession → SessionStarted
            session_id = str(uuid.uuid4())
            if not task_id:
                task_id = session_id
            
            await start_session(ws, json.dumps(req_params).encode(), session_id)
            await wait_for_event(ws, MsgType.FullServerResponse, EventType.SessionStarted)
            print(f"   ✅ 会话开始 (session: {session_id[:8]}...)")
            
            # 3. 立刻发FinishSession (官方demo的关键步骤!)
            await finish_session(ws, session_id)
            if verbose:
                print(f"   📤 FinishSession sent")
            
            # 4. 循环接收音频
            round_audio = bytearray()
            current_voice = ""
            
            while True:
                msg = await receive_message(ws)
                
                # 音频数据
                if msg.type == MsgType.AudioOnlyServer and msg.event == EventType.PodcastRoundResponse:
                    round_audio.extend(msg.payload)
                    total = len(podcast_audio) + len(round_audio)
                    if verbose:
                        print(f"   🔊 +{len(msg.payload)}B (累计{total/1024:.0f}KB)")
                    elif total % (200 * 1024) < len(msg.payload):
                        elapsed = time.time() - start_time
                        print(f"   🔊 {total/1024:.0f}KB | R{current_round} | {elapsed:.0f}s")
                
                # 错误
                elif msg.type == MsgType.Error:
                    error_msg = msg.payload.decode('utf-8', 'ignore')
                    print(f"❌ 服务端错误: {error_msg}")
                    return False
                
                elif msg.type == MsgType.FullServerResponse:
                    
                    if msg.event == EventType.PodcastRoundStart:
                        data = json.loads(msg.payload.decode())
                        current_round = data.get('round_id', 0)
                        current_voice = data.get('speaker', '')
                        text_preview = data.get('text', '')[:50]
                        round_count += 1
                        is_round_end = False
                        
                        if current_round == -1:
                            print(f"   🎵 开头音乐")
                        elif current_round == 9999:
                            print(f"   🎵 结尾音乐")
                        else:
                            voice_short = current_voice.split('_')[2] if '_' in current_voice else current_voice[:8]
                            print(f"   🎙️  R{current_round} [{voice_short}] {text_preview}")
                    
                    elif msg.event == EventType.PodcastRoundEnd:
                        data = json.loads(msg.payload.decode())
                        
                        if data.get('is_error'):
                            print(f"   ⚠️  轮次{current_round}错误: {data.get('error_msg', '?')}")
                            break  # 触发断点续传
                        
                        is_round_end = True
                        last_round_id = current_round
                        duration = data.get('audio_duration', 0)
                        
                        if round_audio:
                            podcast_audio.extend(round_audio)
                            if verbose:
                                print(f"   ⏱️  R{current_round}: {duration:.1f}s ({len(round_audio)/1024:.0f}KB)")
                            round_audio.clear()
                    
                    elif msg.event == EventType.PodcastEnd:
                        data = json.loads(msg.payload.decode())
                        meta = data.get('meta_info', {})
                        metrics = meta.get('input_metrics', {})
                        audio_url = meta.get('audio_url', '')
                        
                        print(f"   🎉 播客完成! ({round_count}轮)")
                        if metrics:
                            orig = metrics.get('origin_input_text_length', '?')
                            proc = metrics.get('input_text_length', '?')
                            trunc = metrics.get('input_text_truncated', False)
                            print(f"   📊 输入{orig}字 → 处理{proc}字{' (截断)' if trunc else ''}")
                        if audio_url and verbose:
                            print(f"   🔗 {audio_url[:80]}...")
                    
                    elif msg.event == EventType.UsageResponse:
                        data = json.loads(msg.payload.decode())
                        usage = data.get('usage', {})
                        inp = usage.get('input_text_tokens', 0)
                        out = usage.get('output_audio_tokens', 0)
                        if inp or out:
                            print(f"   💰 Token: 输入{inp} / 输出{out}")
                
                # 会话结束
                if msg.event == EventType.SessionFinished:
                    if verbose:
                        print(f"   ✅ SessionFinished")
                    break
            
            # 5. FinishConnection → ConnectionFinished
            await finish_connection(ws)
            await wait_for_event(ws, MsgType.FullServerResponse, EventType.ConnectionFinished)
            if verbose:
                print(f"   ✅ ConnectionFinished")
            
            await ws.close()
            
            # 检查是否完整
            if is_round_end:
                break  # 成功!
            else:
                print(f"   🔄 未完整结束，重试... (剩余{retry_num-1}次)")
                retry_num -= 1
                await asyncio.sleep(1)
    
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback; traceback.print_exc()
        return False
    
    # 保存
    elapsed = time.time() - start_time
    if podcast_audio:
        with open(output_path, 'wb') as f:
            f.write(podcast_audio)
        fsize = os.path.getsize(output_path) / (1024 * 1024)
        print(f"\n✅ 播客已保存: {output_path}")
        print(f"   📄 {round_count}轮 | 💾 {fsize:.2f}MB | ⏱️ {elapsed:.0f}s")
        return True
    else:
        print("❌ 未收到音频")
        return False


# ════════════════════════════════════════
# 主程序
# ════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description='火山引擎豆包·播客语音合成')
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--text', help='播客对话文稿(A:/B:格式)')
    group.add_argument('--topic', help='主题(API自动展开)')
    group.add_argument('--url', help='网页/PDF链接')
    group.add_argument('--raw', help='长文本文件')
    
    parser.add_argument('-o', '--output', required=True, help='输出音频路径')
    parser.add_argument('--format', default='mp3', choices=['mp3', 'ogg_opus', 'pcm', 'aac'])
    parser.add_argument('--sample-rate', type=int, default=24000, choices=[16000, 24000, 48000])
    parser.add_argument('--speed', type=int, default=0, help='语速[-50,100]')
    parser.add_argument('--speakers', default='dayi', choices=list(SPEAKERS.keys()))
    parser.add_argument('--no-head-music', action='store_true')
    parser.add_argument('--tail-music', action='store_true')
    parser.add_argument('--app-id', help='App ID (或 VOLC_APP_ID)')
    parser.add_argument('--access-key', help='Access Key (或 VOLC_ACCESS_KEY)')
    parser.add_argument('-v', '--verbose', action='store_true')
    
    args = parser.parse_args()
    
    app_id = args.app_id or os.environ.get('VOLC_APP_ID', '')
    access_key = args.access_key or os.environ.get('VOLC_ACCESS_KEY', '')
    
    if not app_id or not access_key:
        print("❌ 需要凭证: --app-id + --access-key 或环境变量 VOLC_APP_ID + VOLC_ACCESS_KEY")
        sys.exit(1)
    
    spk = SPEAKERS[args.speakers]
    
    # 构建请求参数
    req_params = {
        'input_id': str(uuid.uuid4())[:8],
        'action': 0,
        'use_head_music': not args.no_head_music,
        'use_tail_music': args.tail_music,
        'audio_config': {
            'format': args.format,
            'sample_rate': args.sample_rate,
            'speech_rate': args.speed,
        },
        'speaker_info': {
            'random_order': False,
            'speakers': [spk['a'], spk['b']]
        },
        'input_info': {},
    }
    
    if args.text:
        if not os.path.exists(args.text):
            print(f"❌ 文件不存在: {args.text}"); sys.exit(1)
        with open(args.text, 'r', encoding='utf-8') as f:
            script = f.read()
        turns = parse_podcast_script(script, spk['a'], spk['b'])
        if not turns:
            print("❌ 无法解析对话(需要A:/B:格式)"); sys.exit(1)
        nlp_texts = build_nlp_texts(turns)
        req_params['action'] = 3
        req_params['nlp_texts'] = nlp_texts
        total = sum(len(t['text']) for t in nlp_texts)
        print(f"📝 {len(turns)}轮对话 → {len(nlp_texts)}段 ({total}字)")
    
    elif args.topic:
        req_params['action'] = 4
        req_params['prompt_text'] = args.topic
        print(f"📝 主题: {args.topic}")
    
    elif args.url:
        req_params['action'] = 0
        req_params['input_info']['input_url'] = args.url
        print(f"🔗 URL: {args.url}")
    
    elif args.raw:
        if not os.path.exists(args.raw):
            print(f"❌ 文件不存在: {args.raw}"); sys.exit(1)
        with open(args.raw, 'r', encoding='utf-8') as f:
            raw_text = f.read()
        req_params['action'] = 0
        req_params['input_text'] = raw_text[:32000]
        req_params['input_info']['input_text_max_length'] = 12000
        print(f"📝 原文: {len(raw_text)}字")
    
    print(f"🎙️  发音人: {spk['name']}")
    print(f"🎵 {args.format} @ {args.sample_rate}Hz | 语速: {args.speed}")
    print()
    
    ok = asyncio.run(generate_podcast(req_params, app_id, access_key, args.output, args.verbose))
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
