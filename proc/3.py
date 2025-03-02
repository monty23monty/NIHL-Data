import json
from datetime import datetime

import requests

# Load your JSON files
with open('all_games.json') as f:
    games_data = json.load(f)

matches_data = requests.get("https://s3-eu-west-1.amazonaws.com/nihl.hokejovyzapis.cz/league-matches/2024/1.json").json()

# Define the date formats for each JSON
game_date_format = "%d.%m.%Y"         # e.g., "13.09.2024"
match_date_format = "%Y-%m-%d %H:%M:%S" # e.g., "2024-09-13 19:30:00"

# Process each game to find a matching match (by date and teams)
for game in games_data:
    try:
        game_date = datetime.strptime(game["game_date"], game_date_format).date()
    except Exception as e:
        print(f"Error parsing game_date {game['game_date']}: {e}")
        continue

    # Normalize team names to lower case and strip extra spaces
    game_teams = sorted([game["home_team"].strip().lower(), game["away_team"].strip().lower()])

    # Search through the matches to find one that matches both date and teams
    for match in matches_data["matches"]:
        try:
            match_datetime = datetime.strptime(match["start_date"], match_date_format)
            match_date = match_datetime.date()
        except Exception as e:
            print(f"Error parsing match start_date {match['start_date']}: {e}")
            continue

        # Normalize the match team names
        match_teams = sorted([
            match["home"]["name"].strip().lower(),
            match["guest"]["name"].strip().lower()
        ])

        # Check if both the date and the teams match
        if game_date == match_date and game_teams == match_teams:
            game["match_id"] = match["id"]
            break  # Stop searching after finding the first matching match

# Print the updated games data
print(json.dumps(games_data, indent=2))

# Optionally, write the merged data to a new JSON file
with open('merged.json', 'w') as f:
    json.dump(games_data, f, indent=2)
