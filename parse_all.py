import os
import json
import pprint
from bs4 import BeautifulSoup


def parse_game_file(file_path):
    print("Parsing file:", file_path)
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    # Extract game-level info
    date_elem = soup.find("div", class_="styled__DateWrapper-sc-17e25jw-0")
    game_date = date_elem.get_text(strip=True) if date_elem else "Unknown Date"
    print("Game date:", game_date)

    home_elem = soup.find("span", class_="styled__MatchHeaderHome-sc-17e25jw-6")
    home_team = home_elem.find("a").get_text(strip=True) if home_elem and home_elem.find("a") else "Unknown Home"
    print("Home team:", home_team)

    away_elem = soup.find("span", class_="styled__MatchHeaderAway-sc-17e25jw-7")
    away_team = away_elem.find("a").get_text(strip=True) if away_elem and away_elem.find("a") else "Unknown Away"
    print("Away team:", away_team)

    # Initialize players dictionary
    players = {home_team: [], away_team: []}

    # Locate the wide block that contains player tables
    wide_block = soup.find("div", class_="OverviewBlocks__WideBlock-sc-ltm3ri-4")
    if not wide_block:
        print("Wide block with player tables not found.")
        return None

    # Find all tables (divs with role="table") inside the wide block
    tables = wide_block.find_all("div", {"role": "table"})
    print(f"Found {len(tables)} tables in wide block.")

    for idx, table in enumerate(tables, start=1):
        print("\n--- Table", idx, "---")
        # Get the team name for this table from the preceding header element
        team_header = table.find_previous("div", class_="styled__TableHeaderName-sc-g8pcp-3")
        team_name = team_header.get_text(strip=True) if team_header else "Unknown Team"
        print("Table team header:", team_name)

        # Extract header row from the table (look for a div with role="row" that contains columnheaders)
        header_row = table.find("div", role="row", class_=lambda c: c and "Table__TableHeaderRow" in c)
        if not header_row:
            print("No header row found in this table; skipping.")
            continue
        header_cells = header_row.find_all("div", role="columnheader")
        columns = [cell.get_text(" ", strip=True) for cell in header_cells]
        print("Extracted columns:", columns)

        # Skip table if there are fewer than 5 columns (assuming player stats table should have many columns)
        if len(columns) < 5:
            print("Table skipped due to insufficient columns.")
            continue

        # Instead of using find("div", {"role": "rowgroup"}), get all rowgroups and choose the second one as the body.
        rowgroups = table.find_all("div", {"role": "rowgroup"})
        if len(rowgroups) < 2:
            print("No separate body rowgroup found; skipping table.")
            continue
        else:
            body_group = rowgroups[1]

        data_rows = body_group.find_all("div", role="row")
        print(f"Found {len(data_rows)} data rows in table.")
        team_players = []
        for row_idx, row in enumerate(data_rows, start=1):
            cells = row.find_all("div", role="cell")
            if len(cells) != len(columns):
                print(
                    f"Row {row_idx}: number of cells ({len(cells)}) does not match number of columns ({len(columns)}); skipping row.")
                continue
            player_data = {}
            for col, cell in zip(columns, cells):
                text = cell.get_text(" ", strip=True)
                player_data[col] = text
            print(f"Row {row_idx} data:", player_data)
            team_players.append(player_data)

        # Place the parsed player stats under the proper team key.
        if team_name == home_team:
            players[home_team].extend(team_players)
        elif team_name == away_team:
            players[away_team].extend(team_players)
        else:
            print(f"Table team '{team_name}' does not match home or away teams; adding under its own key.")
            players.setdefault(team_name, []).extend(team_players)

    game_data = {
        "game_date": game_date,
        "home_team": home_team,
        "away_team": away_team,
        "players": players
    }
    return game_data


# Folder containing the HTML game files
games_folder = "games_html"
all_games = []

# Loop through all .html files in the folder
for filename in os.listdir(games_folder):
    if filename.endswith(".html"):
        file_path = os.path.join(games_folder, filename)
        game_data = parse_game_file(file_path)
        if game_data:
            all_games.append(game_data)

# Write the collected games to a JSON file
output_file = "all_games.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(all_games, f, indent=2)

print(f"Parsed {len(all_games)} games. Data written to {output_file}")
