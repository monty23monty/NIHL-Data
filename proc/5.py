import json


def filter_player_info(player):
    # Create a new dictionary with only the desired keys
    return {
        "number": player.get("Shirt number #"),
        "name": player.get("Player"),
        "position": player.get("Position POS"),
        "time on ice": player.get("Time on ice TOI")
    }


def process_json(input_file, output_file):
    # Load the JSON data from the input file
    with open(input_file, 'r') as f:
        data = json.load(f)

    # Iterate over each game entry
    for game in data:
        if "players" in game:
            # For each team within the players section, filter each player's info
            for team, players in game["players"].items():
                game["players"][team] = [filter_player_info(player) for player in players]

    # Write the filtered data to the output file with indentation for readability
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"Processed data has been saved to {output_file}")


if __name__ == "__main__":
    input_file = 'updated_data.json'  # Replace with your JSON file name if different
    output_file = 'processed_data.json'  # The file where the output will be saved
    process_json(input_file, output_file)
