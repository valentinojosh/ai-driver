from pyglet import app
from game_objects.car import Car
from ai.ai_controller import AIController
from controls import Controls
from window import GameWindow
from game_objects.Track.track import Track

# Initialize the game window
window = GameWindow()

# Initialize Controls and attach to the window
controls = Controls()
controls.attach_to_window(window.get_window())

# Initialize the Track and load it
track = Track(batch=window.get_batch())

# Load start point from track
start_point = track.start_point

# Create the car
car = Car(start_point[0], start_point[1], window.get_car_image(), window.get_batch(), scale=0.05)

# Define state and action sizes for the AI
state_size = 9  # 8 ray distances + 1 velocity
action_size = 5  # Accelerate, Decelerate, Turn Left, Turn Right, Do Nothing

# Initialize AI Controller
ai_controller = AIController(state_size=state_size, action_size=action_size)


def update(dt):
    """
    Update the game state on each frame.

    Args:
        dt (float): Time elapsed since the last frame.
    """
    if controls.is_ai_enabled():
        car.update(dt, {}, track.get_track_data(), ai_controller=ai_controller)
    else:
        manual_input = controls.get_manual_input()
        car.update(dt, manual_input, track.get_track_data())


@window.get_window().event
def on_draw():
    """
    Render the game window.
    """
    window.get_window().clear()
    window.get_batch().draw()


# Schedule updates
window.schedule_update(update)

# Run the game loop
app.run()
