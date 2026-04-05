import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Circle, Rectangle, Arc

def draw_court(ax):
    """Draw an NBA court on a matplotlib axes."""
    
    # Court boundaries
    ax.set_xlim(0, 94)
    ax.set_ylim(0, 50)
    ax.set_aspect('equal')
    ax.set_facecolor('#dfbb85')  # hardwood color
    
    court_color = 'black'
    lw = 1.5

    # Outer boundary
    ax.plot([0, 94], [0, 0], color=court_color, lw=lw)
    ax.plot([0, 94], [50, 50], color=court_color, lw=lw)
    ax.plot([0, 0], [0, 50], color=court_color, lw=lw)
    ax.plot([94, 94], [0, 50], color=court_color, lw=lw)

    # Half court line
    ax.plot([47, 47], [0, 50], color=court_color, lw=lw)

    # Center circle
    center_circle = Circle((47, 25), 6, color=court_color, fill=False, lw=lw)
    ax.add_patch(center_circle)

    # --- Left side ---
    # Paint / key
    ax.add_patch(Rectangle((0, 17), 19, 16, fill=False, color=court_color, lw=lw))
    # Free throw circle
    ax.add_patch(Arc((19, 25), 12, 12, angle=0, theta1=270, theta2=90, color=court_color, lw=lw))
    ax.add_patch(Arc((19, 25), 12, 12, angle=0, theta1=90, theta2=270, color=court_color, lw=lw, linestyle='dashed'))
    # Backboard
    ax.plot([4, 4], [22, 28], color=court_color, lw=lw)
    # Basket
    ax.add_patch(Circle((5.25, 25), 0.75, color=court_color, fill=False, lw=lw))
    # Restricted area
    ax.add_patch(Arc((5.25, 25), 8, 8, angle=0, theta1=270, theta2=90, color=court_color, lw=lw))
    # Three point line
    ax.plot([0, 14], [3, 3], color=court_color, lw=lw)
    ax.plot([0, 14], [47, 47], color=court_color, lw=lw)
    ax.add_patch(Arc((5.25, 25), 47.5, 47.5, angle=0, theta1=292, theta2=68, color=court_color, lw=lw))

    # --- Right side ---
    # Paint / key
    ax.add_patch(Rectangle((75, 17), 19, 16, fill=False, color=court_color, lw=lw))
    # Free throw circle
    ax.add_patch(Arc((75, 25), 12, 12, angle=0, theta1=90, theta2=270, color=court_color, lw=lw))
    ax.add_patch(Arc((75, 25), 12, 12, angle=0, theta1=270, theta2=90, color=court_color, lw=lw, linestyle='dashed'))
    # Backboard
    ax.plot([90, 90], [22, 28], color=court_color, lw=lw)
    # Basket
    ax.add_patch(Circle((88.75, 25), 0.75, color=court_color, fill=False, lw=lw))
    # Restricted area
    ax.add_patch(Arc((88.75, 25), 8, 8, angle=0, theta1=90, theta2=270, color=court_color, lw=lw))
    # Three point line
    ax.plot([94, 80], [3, 3], color=court_color, lw=lw)
    ax.plot([94, 80], [47, 47], color=court_color, lw=lw)
    ax.add_patch(Arc((88.75, 25), 47.5, 47.5, angle=0, theta1=112, theta2=248, color=court_color, lw=lw))

    return ax


def animate_event(game_json_path, event_id):
    """Animate a single event from a game JSON file."""

    with open(game_json_path) as f:
        data = json.load(f)

    # Find the event
    event = next((e for e in data['events'] if e['eventId'] == str(event_id)), None)
    if event is None:
        print(f"Event {event_id} not found.")
        return

    # Build player lookup {player_id: name}
    player_lookup = {-1: 'Ball'}
    for team in [event['home'], event['visitor']]:
        for p in team['players']:
            pid = p['playerid']
            player_lookup[pid] = f"{p['firstname'][0]}. {p['lastname']}"

    # Team colors
    home_id = event['home']['teamid']
    visitor_id = event['visitor']['teamid']
    color_map = {-1: 'orange', home_id: 'blue', visitor_id: 'red'}

    moments = event['moments']

    # Set up figure
    fig, ax = plt.subplots(figsize=(12, 7))
    draw_court(ax)

    title = ax.set_title(
        f"Game: {data['gameid']} | Event: {event_id} | "
        f"{event['home']['abbreviation']} vs {event['visitor']['abbreviation']}",
        fontsize=11
    )

    # Create one dot + label per player
    dots = {}
    labels = {}
    all_ids = [-1] + [p['playerid'] for team in [event['home'], event['visitor']] for p in team['players']]

    for pid in all_ids:
        team_id = -1 if pid == -1 else (home_id if any(p['playerid'] == pid for p in event['home']['players']) else visitor_id)
        color = color_map.get(team_id, 'gray')
        size = 200 if pid == -1 else 100
        dot = ax.scatter([], [], s=size, color=color, zorder=5)
        label = ax.text(0, 0, '', fontsize=6, ha='center', va='bottom', zorder=6)
        dots[pid] = dot
        labels[pid] = label

    # Legend
    ax.scatter([], [], s=100, color='blue', label=event['home']['abbreviation'])
    ax.scatter([], [], s=100, color='red', label=event['visitor']['abbreviation'])
    ax.scatter([], [], s=200, color='orange', label='Ball')
    ax.legend(loc='upper right', fontsize=8)

    def update(frame):
        moment = moments[frame]
        game_clock = moment[2]
        shot_clock = moment[3] if moment[3] else 0.0

        title.set_text(
            f"Game: {data['gameid']} | Event: {event_id} | "
            f"{event['home']['abbreviation']} vs {event['visitor']['abbreviation']} | "
            f"Q{moment[0]} | {int(game_clock//60)}:{int(game_clock%60):02d} | ShotClock: {shot_clock:.1f}s"
        )

        for player in moment[5]:
            pid = player[1]
            x, y = player[2], player[3]
            if pid in dots:
                dots[pid].set_offsets([[x, y]])
                labels[pid].set_position((x, y + 1.2))
                labels[pid].set_text(player_lookup.get(pid, str(pid)))

        return list(dots.values()) + list(labels.values()) + [title]

    ani = animation.FuncAnimation(
        fig, update, frames=len(moments),
        interval=40, blit=False
    )

    plt.tight_layout()
    plt.show()
    return ani


# --- Run it ---
if __name__ == "__main__":
    animate_event('data/extracted/0021500001.json', event_id=3)