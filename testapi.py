import requests
import json
import os
import time
from pathlib import Path

# ── Cấu hình ──────────────────────────────────────────────────────────────────
API_KEY = "Your_API_Key_Here"
GENERATE_URL = "https://gateway.pixazo.ai/sora-video/v1/video/generate"
RESULT_URL   = "https://gateway.pixazo.ai/sora-video/v1/video/result"   # POST {video_id: ...}

HEADERS = {
    "Content-Type": "application/json",
    "Cache-Control": "no-cache",
    "Ocp-Apim-Subscription-Key": API_KEY,
}

# ── Prompt marketing tai nghe không dây (tiếng Việt + người đóng) ─────────────
PROMPT = """
Create a short vertical viral video (30–45 seconds) optimized for Facebook Reels/TikTok.

Concept:
A highly engaging, real-life style video with a strong emotional or surprising hook, designed to keep viewers watching until the end.

Structure:

1. Hook (0–3s):
Start with an attention-grabbing moment that creates curiosity or tension.
Use close-up framing and a dynamic camera movement.

2. Build-up (3–15s):
Show the situation developing.
Introduce the character and context quickly.
Use fast cuts and subtle zoom-ins to maintain engagement.

3. Main moment (15–30s):
Deliver the key action, emotional peak, or unexpected twist.
Make it visually clear and impactful.

4. Ending (30–45s):
Provide a satisfying payoff or a twist ending.
Optionally create a loop so the ending connects naturally back to the beginning.

Visual Style:
- Vertical 9:16 format
- Realistic, natural lighting
- Handheld camera feel for authenticity
- Close-ups for emotional emphasis
- Slight motion blur for dynamic movement

Editing Style:
- Fast-paced cuts every 1–3 seconds
- Zoom-in transitions and jump cuts
- Add subtle camera shake for realism

Audio:
- Background music: trending, emotional or suspenseful
- Add sound effects (whoosh, impact, ambient sounds)
- Optional voice-over or natural dialogue

Text Overlay:
- Bold captions synced with speech
- Highlight key phrases for engagement
- Use large, readable fonts

Tone:
- Relatable, emotional, or surprising
- Designed to maximize retention and shares

Goal:
Create a scroll-stopping, high-retention viral video that feels authentic and engaging.
"""

DATA = {
    "prompt": PROMPT,
    "size": "1280x720",
    "seconds": 12,
}

# ── Thư mục lưu trữ ───────────────────────────────────────────────────────────
VIDEO_DIR = Path("video")
VIDEO_DIR.mkdir(exist_ok=True)
URL_LOG   = VIDEO_DIR / "video_urls.txt"

# ── Gửi yêu cầu tạo video ─────────────────────────────────────────────────────
print("⏳ Đang gửi yêu cầu tạo video...")
response = requests.post(GENERATE_URL, headers=HEADERS, data=json.dumps(DATA), timeout=30)
result   = response.json()
print("Phản hồi ban đầu:", json.dumps(result, indent=2, ensure_ascii=False))

# ── Lấy job_id (tuỳ cấu trúc response của Pixazo) ────────────────────────────
job_id    = result.get("job_id") or result.get("id") or result.get("requestId")
video_url = result.get("video_url") or result.get("url") or result.get("output")

# ── Nếu cần polling trạng thái ────────────────────────────────────────────────
if job_id and not video_url:
    POLL_INTERVAL = 30          # giây giữa mỗi lần poll
    MAX_ATTEMPTS  = 180         # 180 x 30s = 90 phút
    print(f"🔄 Job ID: {job_id}")
    print(f"   Polling: POST {RESULT_URL}")
    print(f"   Tần suất: mỗi {POLL_INTERVAL}s, tối đa {MAX_ATTEMPTS * POLL_INTERVAL // 60} phút\n")
    prev_state = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        time.sleep(POLL_INTERVAL)
        try:
            status_resp = requests.post(
                RESULT_URL,
                headers=HEADERS,
                data=json.dumps({"video_id": job_id}),
                timeout=20,
            )
            status_data = status_resp.json()
        except Exception as e:
            print(f"  [{attempt:03d}] Lỗi kết nối: {e}")
            continue

        # In raw response lần đầu để debug
        if attempt == 1:
            print(f"  [DEBUG] HTTP {status_resp.status_code}")
            print(f"  [DEBUG] Raw:\n{json.dumps(status_data, indent=4, ensure_ascii=False)}\n")

        state     = (status_data.get("status") or "").lower()
        video_url = status_data.get("video_url")

        if state != prev_state or attempt % 10 == 0:
            elapsed = attempt * POLL_INTERVAL // 60
            print(f"  [{attempt:03d}] ~{elapsed:2d} phút | HTTP {status_resp.status_code} | status={state or '?'} | video={'✓' if video_url else '✗'}")
            prev_state = state

        if video_url or state in ("completed", "succeeded", "done", "success", "finished"):
            print("✅ Video đã sẵn sàng!")
            break
    else:
        print(f"⚠️  Hết thời gian chờ ({MAX_ATTEMPTS * POLL_INTERVAL // 60} phút). Kiểm tra lại sau.")
        print(f"   Poll thủ công: python check_status.py {job_id}")

# ── Lưu URL vào file log ──────────────────────────────────────────────────────
if video_url:
    print(f"\n🔗 URL video: {video_url}")
    with open(URL_LOG, "a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} | {video_url}\n")
    print(f"📝 Đã lưu URL vào: {URL_LOG}")

    # ── Tải video về máy ─────────────────────────────────────────────────────
    filename  = VIDEO_DIR / f"headphone_marketing_{int(time.time())}.mp4"
    print(f"⬇️  Đang tải video về: {filename} ...")
    dl = requests.get(video_url, stream=True, timeout=120)
    with open(filename, "wb") as vf:
        for chunk in dl.iter_content(chunk_size=8192):
            vf.write(chunk)
    print(f"🎬 Đã lưu video: {filename}")
else:
    print("❌ Không lấy được URL video. Kiểm tra lại response ở trên.")
    print("Response đầy đủ:", json.dumps(result, indent=2, ensure_ascii=False))
