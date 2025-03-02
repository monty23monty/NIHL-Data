import json
import requests

# Load your original JSON data (assumed to be a list with one match record)
with open("merged.json", "r") as f:
    data = json.load(f)

match_id = data[0]["match_id"]

# Construct the API URL and fetch the game-info JSON
api_url = f"https://s3-eu-west-1.amazonaws.com/nihl.hokejovyzapis.cz/matches/{match_id}/game-info.json"
response = requests.get(api_url)
api_data = response.json()

# Map API teams to your JSON teams
home_team_name = data[0]["home_team"]      # e.g. "Telford Tigers"
visitor_team_name = data[0]["away_team"]     # e.g. "Swindon Wildcats"

# Helper function to check if a player (by jersey) exists in the list
def player_exists(team_players, jersey):
    return any(player.get("Shirt number #") == str(jersey) for player in team_players)

# Default template for a new player entry
def create_new_player(api_player):
    return {
        "Shirt number #": str(api_player["jersey"]),
        "Player": f"{api_player['name']} {api_player['surname']}",
        "Position POS": api_player["position"],
        "Time on ice TOI": "00:00",  # new player always starts with 00:00
        "Power play time PPT": "-",
        "Short-handed time SHT": "-",
        "Goals G": "-",
        "Assists A": "-",
        "Points P": "-",
        "Plus/Minus + / -": "-",
        "Shots on goal S+": "-",
        "Power play shots SPP": "-",
        "Scoring chances SC": "-",
        "Penalty time PEN": "-",
        "Faceoffs FO": "-",
        "Faceoffs won FO+": "-",
        "Hits H+": "-",
        "Hits against H-": "-",
        "Blocked shots SBL": "-",
        "Puck losses GA": "-",
        "Takeaways TA": "-",
        "": ""
    }

# Process home team players from API
for key, api_player in api_data["roster"]["home"].items():
    if not player_exists(data[0]["players"][home_team_name], api_player["jersey"]):
        data[0]["players"][home_team_name].append(create_new_player(api_player))

# Process visitor team players from API
for key, api_player in api_data["roster"]["visitor"].items():
    if not player_exists(data[0]["players"][visitor_team_name], api_player["jersey"]):
        data[0]["players"][visitor_team_name].append(create_new_player(api_player))

# (Optional) Save the updated JSON to a new file
with open("updated_data.json", "w") as f:
    json.dump(data, f, indent=2)

print("Data updated successfully!")
