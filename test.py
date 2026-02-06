name: NHL Games Scraper

on:
  schedule:
    # Exécute tous les jours à 6h UTC (après les matchs de la veille)
    - cron: '0 6 * * *'
  workflow_dispatch: # Permet l'exécution manuelle
  push:
    branches:
      - main
    paths:
      - 'test.py'
      - '.github/workflows/nhl-scraper.yml'

jobs:
  scrape-games:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install requests beautifulsoup4
      
      - name: Run scraper
        run: python test.py
      
      - name: Commit and push changes
        run: |
          git config --local user.email "github-actions[bot]@users.noreply.github.com"
          git config --local user.name "github-actions[bot]"
          git add data/hockey/played_games_last_two_days.json
          git diff --staged --quiet || git commit -m "Update NHL games data - $(date +'%Y-%m-%d %H:%M:%S')"
          git push
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
Sauvegardez ce fichier sous : .github/workflows/nhl-scraper.yml
Configuration supplémentaire
Si vous utilisez un fichier requirements.txt, créez-le :
requests==2.31.0
beautifulsoup4==4.12.3
Et modifiez l'étape d'installation :
- name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
