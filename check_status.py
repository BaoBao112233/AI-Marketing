"""
Script kiểm tra trạng thái một job video đã tạo trước đó.
Dùng khi muốn debug hoặc lấy lại URL video mà không tốn credit tạo mới.

Usage:
    python check_status.py <job_id>
    python check_status.py video_69c74d3107948190a5f7d138c9788f7f025210001858741f
"""
import requests
import json
import sys
import time
from pathlib import Path

API_KEY    = "063860b06a9e463a922f0ceb92bf88ab"
RESULT_URL = "https://gateway.pixazo.ai/sora-video/v1/video/result"  # POST {video_id: ...}
HEADERS    = {
    "Content-Type": "application/json",
    "Cache-Control": "no-cache",
    "Ocp-Apim-Subscription-Key": API_KEY,
}
VIDEO_DIR  = Path("video")
VIDEO_DIR.mkdir(exist_ok=True)
URL_LOG    = VIDEO_DIR / "video_urls.txt"

job_id = sys.argv[1] if len(sys.argv) > 1 else \
         "video_69c74d3107948190a5f7d138c9788f7f025210001858741f"

print(f"🔍 Polling job: {job_id}")
print(f"   POST {RESULT_URL}\n")

for attempt in range(1, 181):  # 180 x 10s = 30 phút
    resp = requests.post(
        RESULT_URL,
        headers=HEADERS,
        data=json.dumps({"video_id": job_id}),
        timeout=20,
    )
    data = resp.json()

    if attempt == 1:
        print(f"[DEBUG] HTTP {resp.status_code}")
        print(f"[DEBUG] Full response:\n{json.dumps(data, indent=2, ensure_ascii=False)}\n")

    state     = (data.get("status") or "").lower()
    video_url = data.get("video_url")

    print(f"  [{attempt:02d}] HTTP {resp.status_code} | status={state or '?'} | url={'✓' if video_url else '✗'}")

    if video_url or state in ("completed", "succeeded", "done", "success", "finished"):
        print(f"\n✅ Video sẵn sàng!")
        print(f"🔗 URL: {video_url}")

        with open(URL_LOG, "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} | {job_id} | {video_url}\n")
        print(f"📝 Đã lưu URL: {URL_LOG}")

        filename = VIDEO_DIR / f"headphone_marketing_{int(time.time())}.mp4"
        print(f"⬇️  Đang tải video: {filename} ...")
        dl = requests.get(video_url, stream=True, timeout=120)
        with open(filename, "wb") as vf:
            for chunk in dl.iter_content(chunk_size=8192):
                vf.write(chunk)
        print(f"🎬 Đã lưu: {filename}")
        break

    time.sleep(10)
else:
    print("\n⚠️  Hết thời gian (30 phút). Job vẫn chưa xong.")
    print(f"   Full response cuối: {json.dumps(data, indent=2, ensure_ascii=False)}")
