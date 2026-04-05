import json
import pandas as pd

def parse_game_events(game_json_path):
    """
    For each event in a game, creates a DataFrame where:
    - Rows = each player's x/y position + ball x/y
    - Columns = each frame in the event
    
    Returns a dict: {event_id: DataFrame}
    """

    with open(game_json_path) as f:
        data = json.load(f)

    game_id = data['gameid']
    event_dfs = {}

    for event in data['events']:
        event_id = event['eventId']
        moments = event['moments']

        if not moments:
            continue

        # Build player lookup for this event {player_id: name_string}
        player_lookup = {}
        for team in [event['home'], event['visitor']]:
            for p in team['players']:
                pid = p['playerid']
                player_lookup[pid] = f"{p['firstname'][0]}_{p['lastname']}"

        # Collect all rows across frames
        # We'll build a dict: {row_label: [val_frame0, val_frame1, ...]}
        rows = {}

        for frame_idx, moment in enumerate(moments):
            for player in moment[5]:
                pid = player[1]
                x   = player[2]
                y   = player[3]

                if pid == -1:
                    # Ball
                    x_key = 'ball_x'
                    y_key = 'ball_y'
                else:
                    name  = player_lookup.get(pid, str(pid))
                    x_key = f"{name}_{pid}_x"
                    y_key = f"{name}_{pid}_y"

                # Initialize lists on first appearance
                if x_key not in rows:
                    rows[x_key] = [None] * frame_idx
                if y_key not in rows:
                    rows[y_key] = [None] * frame_idx

                rows[x_key].append(x)
                rows[y_key].append(y)

            # Pad any missing players in this frame
            for key in rows:
                if len(rows[key]) < frame_idx + 1:
                    rows[key].append(None)

        # Build DataFrame — rows=players/coords, columns=frames
        df = pd.DataFrame(rows).T
        df.columns = [f"frame_{i}" for i in range(df.shape[1])]

        event_dfs[event_id] = df
        print(f"Event {event_id}: {df.shape[1]} frames, {df.shape[0]} rows")

    return game_id, event_dfs


if __name__ == "__main__":
    game_id, event_dfs = parse_game_events('data/extracted/0021500001.json')

    # Preview first 3 events
    for event_id, df in list(event_dfs.items())[:3]:
        print(f"\n--- Event {event_id} ---")
        print(df)


import pickle
import os

def save_game_events(game_json_path, output_dir='data/parsed'):
    os.makedirs(output_dir, exist_ok=True)
    game_id, event_dfs = parse_game_events(game_json_path)
    
    # Convert to Series
    event_series = pd.Series(event_dfs)
    
    # Save as pickle
    out_path = f"{output_dir}/{game_id}.pkl"
    event_series.to_pickle(out_path)
    print(f"Saved {game_id} → {out_path}")

if __name__ == "__main__":
    save_game_events('data/extracted/0021500001.json')