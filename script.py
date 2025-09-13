import os, json, requests
from datetime import datetime

API_KEY = os.environ["YOUTUBE_API_KEY"]

VIDEO_IDS = [
    "y9qZR_OGa0",  # Haegeum
    "uVD-YgzDzyY", # People Pt.2
    "IX1dkYoLHVs", # AMYGDALA
    "qGjAWJ2zWWI", # Daechwita
    "_Zgc12yL5ss", # Give It To Me
    "3Y_Eiyg4bfk", # Agust D
    "PV1gCvzpSy0", # Interlude : Shadow
]

DATA_FILE = "data.json"

def get_stats(video_ids):
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {"part": "statistics,snippet", "id": ",".join(video_ids), "key": API_KEY}
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

def load_old_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_new_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def make_html(old, new):
    today = datetime.utcnow().strftime("%Y-%m-%d")
    html = f"<html><head><meta charset='utf-8'><title>AgustD Weekly Stats</title></head><body>"
    html += f"<h1>AgustD Weekly Stats ({today})</h1>"
    html += "<table border='1' cellpadding='5'><tr><th>Title</th><th>This Week</th><th>Total</th></tr>"
    total_week = 0
    total_all = 0
    for vid, info in new.items():
        old_views = old.get(vid, {}).get("views", 0)
        diff = info["views"] - old_views
        total_week += diff
        total_all += info["views"]
        html += f"<tr><td>{info['title']}</td><td>{diff:,}</td><td>{info['views']:,}</td></tr>"
    html += f"</table><h2>This Week Total: {total_week:,}</h2><h2>All Time Total: {total_all:,}</h2>"
    html += "</body></html>"
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    old = load_old_data()
    new = get_stats(VIDEO_IDS)
    make_html(old, new)
