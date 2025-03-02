import streamlit as st
import json
import pandas as pd

# Load JSON data from file (updated with team names)
with open("final_games.json", "r") as f:
    games = json.load(f)

# Sidebar filter: if toggled, exclude goaltenders (GK)
exclude_gk = st.sidebar.checkbox("Exclude goaltenders (GK)", value=False)

# List to hold the filtered players
filtered_players = []

# Loop through each game and each player
for game in games:
    for player in game.get("players", []):
        # Filter to players with 00:00 time on ice
        if player.get("time on ice") == "00:00":
            # Exclude goaltenders if checkbox is selected
            if exclude_gk and player.get("position") == "GK":
                continue
            # Exclude players named "noname noname"
            if player.get("name", "").lower() == "noname noname":
                continue

            # Use the team name provided in the player data; fallback if needed
            team = player.get("team", game.get("home_team"))

            filtered_players.append({
                "date": game.get("date"),
                "home_team": game.get("home_team"),
                "away_team": game.get("away_team"),
                "team": team,
                "number": player.get("number"),
                "name": player.get("name"),
                "position": player.get("position"),
                "time on ice": player.get("time on ice"),
                "source": player.get("source", "N/A"),
                "present_in_both": player.get("present_in_both", False)
            })

# Convert the list to a DataFrame for display
df = pd.DataFrame(filtered_players)

st.title("Players with 00:00 Time on Ice")
if exclude_gk:
    st.write("Displaying players with 00:00 time on ice (excluding goaltenders):")
else:
    st.write("Displaying all players with 00:00 time on ice:")

st.dataframe(df)

# Create a bar chart for the number of players per team with 00:00 time on ice
st.subheader("Number of Players per Team with 00:00 Time on Ice")
if not df.empty:
    team_counts = df["team"].value_counts().reset_index()
    team_counts.columns = ["Team", "Count"]
    st.bar_chart(team_counts.set_index("Team"))
else:
    st.write("No data available to plot.")
