import os, json, requests
from datetime import datetime
from googleapiclient.discovery import build

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
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    request = youtube.videos().list(
        part='statistics,snippet',
        id=','.join(video_ids)
    )
    response = request.execute()
    
    results = {}
    for item in response.get("items", []):
        vid = item["id"]
        title = item["snippet"]["title"]
        views = int(item["statistics"]["viewCount"])
        results[vid] = {"title": title, "views": views}
    return results

def load_old_data():
    try:
        # Try to download the old data from gh-pages branch
        url = f"https://raw.githubusercontent.com/{os.environ['GITHUB_REPOSITORY']}/gh-pages/{DATA_FILE}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Failed to load old data: {e}")
    return {}

def save_new_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def make_html(old, new):
    today = datetime.utcnow().strftime("%Y-%m-%d")
    html = f"""
    <html>
    <head>
        <meta charset='utf-8'>
        <title>AgustD Weekly Stats</title>
        <style>
            body {{ font-family: sans-serif; margin: 2rem; }}
            h1, h2 {{ color: #333; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; }}
            th, td {{ padding: 12px; border: 1px solid #ddd; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            tr:nth-child(even) {{ background-color: #f9f9f9; }}
            .container {{ max-width: 800px; margin: auto; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>AgustD Weekly Stats ({today})</h1>
            <p>※週間再生回数は前週比</p>
            <table>
                <tr>
                    <th>タイトル</th>
                    <th>今週の再生回数</th>
                    <th>累計再生回数</th>
                </tr>
    """
    total_week_increase = 0
    
    for vid, info in new.items():
        old_views = old.get(vid, {}).get("views", 0)
        weekly_increase = info["views"] - old_views
        total_week_increase += weekly_increase
        html += f"<tr><td>{info['title']}</td><td>{weekly_increase:,}</td><td>{info['views']:,}</td></tr>"

    html += f"""
            </table>
            <h2>今週の合計再生回数: {total_week_increase:,}</h2>
            <h2>全ての累計再生回数: {sum(v['views'] for v in new.values()):,}</h2>
        </div>
    </body>
    </html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    old_data = load_old_data()
    new_data = get_stats(VIDEO_IDS)
    make_html(old_data, new_data)
    save_new_data(new_data)
