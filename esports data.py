import json
import requests


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


def process_games(input_file, output_file):
    # Load the processed games JSON data
    with open(input_file, 'r') as f:
        games = json.load(f)

    all_game_info = []

    # Loop through each game entry in the processed file
    for game in games:
        match_id = game.get("match_id")
        if match_id:
            print(f"Fetching game info for match id: {match_id}")
            game_info = fetch_game_info(match_id)
            if game_info:
                # Append a new dictionary containing the match_id and fetched game info
                all_game_info.append({
                    "match_id": match_id,
                    "game_info": game_info
                })

    # Write all the fetched game info into the new JSON file
    with open(output_file, 'w') as f:
        json.dump(all_game_info, f, indent=2)

    print(f"All game info data has been saved to {output_file}")


if __name__ == "__main__":
    # Replace these file names if necessary
    input_file = 'processed_data.json'
    output_file = 'games_info.json'
    process_games(input_file, output_file)
