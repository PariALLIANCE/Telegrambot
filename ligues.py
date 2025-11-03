import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta, timezone
import re
import os
import subprocess

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0"
}

# === Compétitions ciblées ===
LEAGUES = {
    "UEFA Champions League": {
        "code": "uefa.champions",
        "json": "UEFA_Champions_League.json",
        "start": datetime(2023, 6, 27, tzinfo=timezone.utc)
    },
    "UEFA Europa League": {
        "code": "uefa.europa",
        "json": "UEFA_Europa_League.json",
        "start": datetime(2023, 8, 10, tzinfo=timezone.utc)
    },
    "FIFA Club World Cup": {
        "code": "fifa.cwc",
        "json": "FIFA_Club_World_Cup.json",
        "start": datetime(2023, 12, 12, tzinfo=timezone.utc)
    }
}

# === Date de fin pour tous ===
END_DATE = datetime.now(timezone.utc)


def safe_load_json(json_path: str):
    """Charge un fichier JSON même vide ou corrompu."""
    if not os.path.exists(json_path) or os.path.getsize(json_path) == 0:
        return {}
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return {m["gameId"]: m for m in data if "gameId" in m}
            elif isinstance(data, dict):
                return data
            else:
                return {}
    except (json.JSONDecodeError, ValueError):
        print(f"⚠️ Fichier {json_path} vide ou invalide, recréé.")
        return {}


# === Boucle principale ===
for league_name, league_info in LEAGUES.items():
    BASE_URL = f"https://www.espn.com/soccer/schedule/_/date/{{date}}/league/{league_info['code']}"
    JSON_FILE = league_info["json"]

    existing_matches = safe_load_json(JSON_FILE)
    total_new = 0

    start_date = league_info["start"]
    end_date = END_DATE

    print(f"\n========== {league_name} ==========")
    print(f"🗓️  Du {start_date.date()} au {end_date.date()}")

    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%Y%m%d")

        try:
            res = requests.get(BASE_URL.format(date=date_str), headers=HEADERS, timeout=15)
            if res.status_code != 200:
                current_date += timedelta(days=1)
                continue
            soup = BeautifulSoup(res.content, "html.parser")
        except Exception as e:
            print(f"⚠️ Erreur réseau {league_name} ({date_str}): {e}")
            current_date += timedelta(days=1)
            continue

        tables = soup.select("div.ResponsiveTable")
        new_matches = {}

        for table in tables:
            date_title_tag = table.select_one("div.Table__Title")
            date_text = date_title_tag.text.strip() if date_title_tag else date_str

            rows = table.select("tbody > tr.Table__TR")
            for row in rows:
                try:
                    teams = row.select("span.Table__Team a.AnchorLink:last-child")
                    score_tag = row.select_one("a.AnchorLink.at")

                    if len(teams) != 2 or not score_tag:
                        continue

                    team1 = teams[0].text.strip()
                    team2 = teams[1].text.strip()
                    score = score_tag.text.strip()

                    if score.lower() == "v":
                        continue

                    match_url = score_tag["href"]
                    match_id_match = re.search(r"gameId/(\d+)", match_url)
                    if not match_id_match:
                        continue

                    game_id = match_id_match.group(1)
                    if game_id in existing_matches:
                        continue

                    match_data = {
                        "gameId": game_id,
                        "date": date_text,
                        "team1": team1,
                        "score": score,
                        "team2": team2,
                        "title": f"{team1} VS {team2}",
                        "match_url": "https://www.espn.com" + match_url
                    }

                    new_matches[game_id] = match_data
                    existing_matches[game_id] = match_data

                except Exception as e:
                    print(f"⚠️ Parsing {league_name} ({date_str}): {e}")
                    continue

        if new_matches:
            total_new += len(new_matches)
            print(f"✅ {date_str} : {len(new_matches)} nouveaux matchs.")

        current_date += timedelta(days=1)

    try:
        with open(JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(list(existing_matches.values()), f, indent=2, ensure_ascii=False)
        print(f"💾 {league_name} : {len(existing_matches)} matchs sauvegardés (+{total_new} nouveaux).")
    except Exception as e:
        print(f"⚠️ Erreur d’écriture dans {JSON_FILE}: {e}")

# === Push automatique sur GitHub (optionnel, complète ton token et repo) ===
try:
    GIT_REPO_PATH = "."  # chemin du dépôt local
    subprocess.run(["git", "-C", GIT_REPO_PATH, "add", "."], check=True)
    subprocess.run(["git", "-C", GIT_REPO_PATH, "commit", "-m", "Mise à jour des matchs UEFA & CWC"], check=False)
    subprocess.run(["git", "-C", GIT_REPO_PATH, "push"], check=False)
    print("🚀 Données poussées sur le dépôt GitHub.")
except Exception as e:
    print(f"⚠️ Push GitHub échoué: {e}")
