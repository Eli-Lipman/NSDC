import json
import pandas as pd

# Title: explore.py
# Purpose: script which explores one of the json files to get a sense of how
#          the data is structured. 


# Load one game
with open('data/extracted/0021500001.json') as f:
    data = json.load(f)

print(f"Game ID: {data['gameid']}")
print(f"Game Date: {data['gamedate']}")
print(f"Number of events: {len(data['events'])}")

# Parse moments from first event
event = data['events'][0]
moments = event['moments']

# Flatten moments into rows
rows = []
for moment in moments:
    quarter     = moment[0]
    timestamp   = moment[1]
    game_clock  = moment[2]
    shot_clock  = moment[3]
    
    for player in moment[5]:
        rows.append({
            'quarter':    quarter,
            'timestamp':  timestamp,
            'game_clock': game_clock,
            'shot_clock': shot_clock,
            'team_id':    player[0],
            'player_id':  player[1],
            'x':          player[2],
            'y':          player[3],
            'radius':     player[4]
        })

df = pd.DataFrame(rows)

# Label ball vs players
df['is_ball'] = df['player_id'] == -1

print("\nDataFrame shape:", df.shape)
print("\nFirst few rows:")
print(df.head(10))
print("\nBall tracking sample:")
print(df[df['is_ball']].head(5))