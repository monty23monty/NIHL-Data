import streamlit as st
import json
import pandas as pd
import altair as alt

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
        # Filter for players with 00:00 time on ice
        if player.get("time on ice") == "00:00":
            # Exclude goaltenders if checkbox is selected
            if exclude_gk and player.get("position") == "GK":
                continue
            # Exclude players named "noname noname"
            if player.get("name", "").lower() == "noname noname":
                continue

            # Use the team name provided in the player data; fallback to the game's home_team if needed
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

# ----------------------------
# 1. Create a color-coded bar chart of player counts per team
st.subheader("Number of Players per Team with 00:00 Time on Ice")
if not df.empty:
    # Count the number of players per team
    team_counts = df["team"].value_counts().reset_index()
    team_counts.columns = ["Team", "Count"]

    # Create an Altair bar chart with color coding for each team
    chart = alt.Chart(team_counts).mark_bar().encode(
        x=alt.X("Team:N", sort='-y'),
        y="Count:Q",
        color="Team:N"
    ).properties(
        width=600,
        height=400
    )
    st.altair_chart(chart, use_container_width=True)
else:
    st.write("No data available to plot.")

# ----------------------------
# 2. Create a frequency table for each team showing how many times each player has 00:00
st.subheader("Frequency of 00:00 Time on Ice by Player per Team")
if not df.empty:
    # Group by team and player name and count occurrences
    frequency_df = df.groupby(["team", "name"]).size().reset_index(name="Frequency")

    # Display a separate table for each team
    teams = frequency_df["team"].unique()
    for team in teams:
        st.write(f"### {team}")
        team_df = frequency_df[frequency_df["team"] == team].sort_values(by="Frequency", ascending=False)
        st.table(team_df.reset_index(drop=True))
else:
    st.write("No data available for frequency list.")
