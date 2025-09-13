import os, json, requests
from datetime import datetime
import sys

# APIキーはGitHub Actionsのsecretsから取得
API_KEY = os.environ["YOUTUBE_API_KEY"]

# 取得したい動画IDのリスト
VIDEO_IDS = [
    "g-l9h0Lg948", # Haegeum (修正済み)
    "uVD-YgzDzyY", # People Pt.2
    "IX1dkYoLHVs", # AMYGDALA
    "qGjAWJ2zWWI", # Daechwita
    "_Zgc12yL5ss", # Give It To Me
    "3Y_Eiyg4bfk", # Agust D
    "PV1gCvzpSy0", # Interlude : Shadow
]

# データファイル名
DATA_FILE = "data.json"

def load_old_data():
    try:
        url = f"https://jampbts.github.io/count/{DATA_FILE}"
        r = requests.get(url)
        r.raise_for_status()
        return r.json()
    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
        print(f"Error loading old data: {e}", file=sys.stderr)
        return {}

def get_stats(video_ids):
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {"part": "statistics,snippet", "id": ",".join(video_ids), "key": API_KEY}
    try:
        r = requests.get(url, params=params)
        r.raise_for_status()
        data = r.json()
        results = {}
        for it in data.get("items", []):
            vid = it["id"]
            title = it["snippet"]["title"]
            views = int(it["statistics"]["viewCount"])
            results[vid] = {"title": title, "views": views}
        return results
    except requests.exceptions.RequestException as e:
        print(f"Error getting YouTube stats: {e}", file=sys.stderr)
        sys.exit(1)

def save_new_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    old = load_old_data()
    new = get_stats(VIDEO_IDS)
    
    # 週間再生回数を計算し、新しいデータ構造を作成
    weekly_stats = {
        "date": datetime.utcnow().strftime("%Y-%m-%d"),
        "videos": []
    }
    
    for vid, info in new.items():
        old_views = old.get(vid, {}).get("views", 0)
        diff = info["views"] - old_views
        weekly_stats["videos"].append({
            "title": info["title"],
            "views_this_week": diff,
            "views_total": info["views"]
        })
    
    save_new_data(weekly_stats)
