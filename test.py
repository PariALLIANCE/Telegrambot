import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
import os
import re

# ================= CONFIG =================
BASE_URL = "https://www.espn.com/nhl/schedule/_/date/"
OUTPUT_FILE = "data/hockey/played_games_last_two_days.json"
HEADERS = {"User-Agent": "Mozilla/5.0"}

# ================= UTILS =================
def extract_team_from_href(href):
    """
    /nhl/team/_/name/bos/boston-bruins
    -> Boston Bruins, bos
    """
    parts = href.split("/")
    short = parts[-2]
    full_name = parts[-1].replace("-", " ").title()
    return full_name, short


def build_logo_url(short):
    return f"https://a.espncdn.com/i/teamlogos/nhl/500/{short}.png"


def is_played_match(text):
    """
    Détecte un score : 'MTL 4, BUF 2' ou 'TOR 3, VAN 2 (SO)'
    """
    return bool(re.search(r"\d+\s*,\s*\w+\s*\d+", text))


# ================= MAIN =================
def get_played_games_last_two_days():
    results = []
    today = datetime.utcnow().date()

    for delta in [1, 2]:
        day = today - timedelta(days=delta)
        date_str = day.strftime("%Y%m%d")
        url = BASE_URL + date_str

        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        rows = soup.select("tbody tr")

        for row in rows:
            score_link = row.select_one("td a[href*='/nhl/game/_/gameId']")
            if not score_link:
                continue

            score_text = score_link.get_text(strip=True)

            if not is_played_match(score_text):
                continue  # pas encore joué

            # Récupérer toutes les cellules <td> de la ligne
            cells = row.select("td")

            # La première cellule contient l'équipe à l'extérieur
            # La deuxième cellule contient l'équipe à domicile
            away_team_link = None
            home_team_link = None

            if len(cells) >= 2:
                # Équipe extérieure dans la première cellule
                away_team_link = cells[0].select_one("a[href*='/nhl/team/_/name/']")
                # Équipe domicile dans la deuxième cellule
                home_team_link = cells[1].select_one("a[href*='/nhl/team/_/name/']")

            if not away_team_link or not home_team_link:
                continue

            away_name, away_short = extract_team_from_href(away_team_link["href"])
            home_name, home_short = extract_team_from_href(home_team_link["href"])

            results.append({
                "date": day.isoformat(),
                "score": score_text,
                "away_team": {
                    "name": away_name,
                    "short": away_short,
                    "logo": build_logo_url(away_short)
                },
                "home_team": {
                    "name": home_name,
                    "short": home_short,
                    "logo": build_logo_url(home_short)
                }
            })

    return results


# ================= SAVE =================
def save_json(data):
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    games = get_played_games_last_two_days()
    save_json(games)
    print(f"{len(games)} matchs joués sauvegardés dans {OUTPUT_FILE}")