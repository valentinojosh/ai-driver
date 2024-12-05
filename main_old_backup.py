import pyglet
from pyglet.window import key
from car import Car
from ai.ai_controller import AIController
import json

WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 900

# Initialize the game window and create a batch for rendering
window = pyglet.window.Window(WINDOW_WIDTH, WINDOW_HEIGHT, "Driver")
batch = pyglet.graphics.Batch()

pyglet.resource.path = ['../resources']
pyglet.resource.reindex()
car_image = pyglet.resource.image('car.png')

with open("game_objects/Track/track.json", "r") as f:
    track_data = json.load(f)

# Draw Track
lines = []
for segment in track_data["segments"]:
    for i in range(len(segment) - 1):
        x1, y1 = segment[i]
        x2, y2 = segment[i + 1]
        line = pyglet.shapes.Line(x1, y1, x2, y2, 2, color=(255, 255, 255), batch=batch)
        lines.append(line)

# Draw start and end markers
start_point = track_data["start_point"]
end_point = track_data["end_point"]
start_marker = pyglet.shapes.Circle(start_point[0], start_point[1], 5, color=(0, 255, 0), batch=batch)  # Green circle
end_marker = pyglet.shapes.Circle(end_point[0], end_point[1], 5, color=(255, 0, 0), batch=batch)  # Red circle

# Create the car
car = Car(start_point[0], start_point[1], car_image, batch, 0.07)  # Start car at the starting point

# Define state and action sizes
state_size = 9  # 8 ray distances + 1 velocity
action_size = 5  # Accelerate, Decelerate, Turn Left, Turn Right, Do Nothing

# Initialize AI Controller
ai_controller = AIController(state_size=state_size, action_size=action_size)

# Key tracking
keys = key.KeyStateHandler()
window.push_handlers(keys)

# AI control toggle
ai_enabled = False  # AI starts disabled


@window.event
def on_key_press(symbol, modifiers):
    global ai_enabled
    if symbol == key.A:
        ai_enabled = not ai_enabled  # Toggle AI
        car.is_ai_controlled = ai_enabled  # Sync car state with toggle
        print("AI control enabled." if ai_enabled else "AI control disabled.")


def update(dt):
    global ai_enabled
    if ai_enabled:
        # AI controls the car
        car.update(dt, {}, track_data, ai_controller=ai_controller)
    else:
        # Manual control by arrow keys
        manual_input = {
            'up': keys[key.UP],
            'down': keys[key.DOWN],
            'left': keys[key.LEFT],
            'right': keys[key.RIGHT],
        }
        car.update(dt, manual_input, track_data)


@window.event
def on_draw():
    # Render everything
    window.clear()
    batch.draw()


# Schedule the update function
pyglet.clock.schedule_interval(update, 1 / 60.0)

# Run the game
pyglet.app.run()
