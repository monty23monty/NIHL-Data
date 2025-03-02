import json
import requests


def load_json(filename):
    with open(filename, 'r') as f:
        return json.load(f)


def union_players(processed_players, roster_players):
    """
    processed_players: list of dicts with keys "number", "name", "position", "time on ice"
    roster_players: dict of players from game info (keys arbitrary) with keys "jersey", "name", "surname", "position", etc.

    Returns a list of players that is the union of the two sources. For each player:
      - If present in both sources, 'present_in_both' is True and time on ice is taken from processed data.
      - Otherwise, 'present_in_both' is False, time on ice is set to "00:00", and a new key "source" indicates which file they came from:
          * "instat" if they were only in the processed data.
          * "esports" if they were only in the API data.
    Matching is done using the jersey/number.
    """
    # Convert game info roster into a dict keyed by jersey number (as string)
    roster_dict = {}
    for key, player in roster_players.items():
        jersey_str = str(player.get("jersey"))
        full_name = f"{player.get('name', '')} {player.get('surname', '')}".strip()
        roster_dict[jersey_str] = {
            "number": jersey_str,
            "name": full_name,
            "position": player.get("position")
        }

    # Convert processed players into a dict keyed by their number
    processed_dict = {}
    for player in processed_players:
        num = player.get("number")
        processed_dict[num] = {
            "number": num,
            "name": player.get("name"),
            "position": player.get("position"),
            "time on ice": player.get("time on ice")
        }

    # Build union on keys (jersey numbers)
    all_numbers = set(processed_dict.keys()).union(set(roster_dict.keys()))
    union_list = []
    for number in all_numbers:
        in_processed = number in processed_dict
        in_roster = number in roster_dict

        if in_processed and in_roster:
            # Present in both sources.
            time_on_ice = processed_dict[number].get("time on ice")
            present = True
        else:
            time_on_ice = "00:00"
            present = False

        # Determine source if not in both:
        source = None
        if not present:
            if in_processed and not in_roster:
                source = "instat"
            elif in_roster and not in_processed:
                source = "esports"

        # Prefer name and position from the processed data if available.
        if in_processed:
            name = processed_dict[number].get("name")
            position = processed_dict[number].get("position")
        else:
            name = roster_dict[number].get("name")
            position = roster_dict[number].get("position")

        player_entry = {
            "number": number,
            "name": name,
            "position": position,
            "time on ice": time_on_ice,
            "present_in_both": present
        }
        if not present:
            player_entry["source"] = source

        union_list.append(player_entry)
    return union_list


def fetch_game_info(match_id):
    # Construct the URL using the match_id
    url = f"https://s3-eu-west-1.amazonaws.com/nihl.hokejovyzapis.cz/matches/{match_id}/game-info.json"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching data for match id {match_id}: {e}")
        return None


def process_games(processed_file, games_info_file):
    # Load the processed games JSON data
    with open(processed_file, 'r') as f:
        games = json.load(f)

    all_game_info = []

    # Loop through each game entry in the processed file to fetch API data.
    for game in games:
        match_id = game.get("match_id")
        # Check if the instat game exists (has a match_id).
        if not match_id:
            print("Skipping a game from processed_data.json as it has no match_id (instat game missing).")
            continue

        print(f"Fetching game info for match id: {match_id}")
        game_info = fetch_game_info(match_id)
        if game_info:
            all_game_info.append({
                "match_id": match_id,
                "game_info": game_info
            })

    # Save the fetched game info data to the games_info_file.
    with open(games_info_file, 'w') as f:
        json.dump(all_game_info, f, indent=2)

    print(f"Fetched game info data has been saved to {games_info_file}")


def process_final_data(processed_file, games_info_file, final_output_file):
    # Load the two JSON files.
    processed_games = load_json(processed_file)
    games_info_list = load_json(games_info_file)

    # Create a lookup dictionary for game info data keyed by match_id.
    game_info_dict = {}
    for item in games_info_list:
        match_id = item.get("match_id")
        game_info_dict[match_id] = item.get("game_info", {})

    final_games = []
    for game in processed_games:
        match_id = game.get("match_id")
        if not match_id:
            print("Skipping final processing for a game with missing match_id (instat game missing).")
            continue

        # Optional: Skip games that didn't have corresponding API data.
        if match_id not in game_info_dict:
            print(f"Skipping game with match id {match_id} as it has no corresponding API data.")
            continue

        game_info = game_info_dict.get(match_id, {})

        final_game = {
            "date": game.get("game_date"),
            "home_team": game.get("home_team"),
            "away_team": game.get("away_team"),
            "players": []
        }

        # Process players from processed data.
        # In processed file, players are grouped by team using the team names.
        home_team_name = game.get("home_team")
        away_team_name = game.get("away_team")
        processed_home = game.get("players", {}).get(home_team_name, [])
        processed_away = game.get("players", {}).get(away_team_name, [])

        # In the game info, the rosters are under "roster" with keys "home" and "visitor".
        roster_home = {}
        roster_away = {}
        if game_info:
            roster = game_info.get("roster", {})
            roster_home = roster.get("home", {})
            roster_away = roster.get("visitor", {})

        # Get union of players for each team.
        final_home_players = union_players(processed_home, roster_home)
        final_away_players = union_players(processed_away, roster_away)

        # Add team attribute to each player.
        for player in final_home_players:
            player["team"] = home_team_name
        for player in final_away_players:
            player["team"] = away_team_name

        # Combine players from both teams.
        final_game["players"] = final_home_players + final_away_players
        final_games.append(final_game)

    # Save the final JSON file.
    with open(final_output_file, 'w') as f:
        json.dump(final_games, f, indent=2)

    print(f"Final JSON saved to {final_output_file}")



if __name__ == "__main__":
    # Define file names for the input and output JSON files.
    processed_file = 'processed_data.json'
    games_info_file = 'games_info.json'
    final_output_file = 'final_games.json'

    # First, fetch game info data for each game.
    process_games(processed_file, games_info_file)

    # Then, process the final data combining both JSON files.
    process_final_data(processed_file, games_info_file, final_output_file)
