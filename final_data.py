import json
import requests

def fetch_api_data(match_id):
    """
    Fetches game data from the API for the given match_id.
    """
    url = f"https://s3-eu-west-1.amazonaws.com/nihl.hokejovyzapis.cz/matches/{match_id}/game-info.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching data for match {match_id}: {e}")
        return None

def process_game(game):
    """
    For a given game object from the original file, fetch the API data, compare the player rosters,
    and return a new game object with players reduced to only the TOI and a 'zero' flag.
    """
    match_id = game.get("match_id")
    api_data = fetch_api_data(match_id)
    if not api_data:
        return None

    # The API data should have "gameInfo" with team info and a "roster" with two teams: "home" and "visitor".
    team_info = api_data.get("gameInfo", {}).get("teamInfo", {})
    api_roster = api_data.get("roster", {})

    # Create a mapping from team name to the corresponding API roster
    team_to_api = {}
    if "home" in team_info and "name" in team_info["home"]:
        team_to_api[ team_info["home"]["name"] ] = api_roster.get("home", {})
    if "visitor" in team_info and "name" in team_info["visitor"]:
        team_to_api[ team_info["visitor"]["name"] ] = api_roster.get("visitor", {})

    # The original file's players key is a dict mapping team names to lists of players.
    original_players = game.get("players", {})
    new_players = {}

    # Loop over each team in the original game.
    for team_name, players in original_players.items():
        # Get the matching API team roster using the team name.
        api_team = team_to_api.get(team_name)
        if not api_team:
            continue  # Skip if the team isn’t found in the API data.

        # Build a set of jersey numbers from the API roster (convert to string for comparison)
        api_jerseys = { str(player_data.get("jersey")) for player_data in api_team.values() if player_data.get("jersey") is not None }

        # Process each player from the original list if they match an API jersey.
        new_team_players = []
        for player in players:
            jersey = player.get("Shirt number #")
            if jersey and str(jersey) in api_jerseys:
                toi = player.get("Time on ice TOI", "00:00")
                new_team_players.append({
                    "Player": player.get("Player"),
                    "TOI": toi,
                    "zero": (toi == "00:00")
                })
        new_players[team_name] = new_team_players

    # Build the new game object
    new_game = {
        "match_id": match_id,
        "game_date": game.get("game_date"),
        "home_team": game.get("home_team"),
        "away_team": game.get("away_team"),
        "players": new_players
    }
    return new_game

def main():
    # Load the original JSON file
    with open("merged.json", "r") as infile:
        games = json.load(infile)

    output_games = []
    for game in games:
        processed = process_game(game)
        if processed:
            output_games.append(processed)
        else:
            print(f"Skipping match_id {game.get('match_id')} due to API issues.")

    # Write the new JSON structure to a file
    with open("output.json", "w") as outfile:
        json.dump(output_games, outfile, indent=2)

    print("New JSON file created: output.json")

if __name__ == "__main__":
    main()
