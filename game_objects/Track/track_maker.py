import pyglet
from pyglet.window import mouse, key
import json
from pyglet import shapes
import numpy as np

# Constants
WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 900
POINT_DISTANCE_THRESHOLD = 5  # Minimum distance between consecutive points

# Initialize the game window
window = pyglet.window.Window(WINDOW_WIDTH, WINDOW_HEIGHT, "Track Maker")

# Create a batch for rendering
batch = pyglet.graphics.Batch()

# Track data
track_points = []  # Current segment points
finalized_segments = []  # All finalized track segments (list of point lists)
temp_line = None  # Temporary line being drawn in real-time
permanent_lines = []  # List of all permanent line objects
start_marker = None
end_marker = None
start_point = None
end_point = None
smoothing_level = 10  # Default smoothing granularity


# Add a point to the current segment
def add_point(x, y):
    if len(track_points) == 0 or distance(track_points[-1], (x, y)) > POINT_DISTANCE_THRESHOLD:
        track_points.append((x, y))


# Smooth points
def smooth_points(points, granularity):
    """Smooth points into a curve using Catmull-Rom splines."""
    if len(points) < 3:
        return points  # Not enough points to smooth

    points = np.array(points)
    smoothed = []
    for i in range(1, len(points) - 2):
        p0, p1, p2, p3 = points[i - 1], points[i], points[i + 1], points[i + 2]

        for t in np.linspace(0, 1, granularity):
            t2 = t * t
            t3 = t2 * t

            x = 0.5 * (
                (2 * p1[0]) +
                (-p0[0] + p2[0]) * t +
                (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 +
                (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3
            )

            y = 0.5 * (
                (2 * p1[1]) +
                (-p0[1] + p2[1]) * t +
                (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 +
                (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3
            )

            smoothed.append((x, y))
    return smoothed


# Update permanent lines
def update_permanent_lines():
    """Re-render all finalized lines."""
    global permanent_lines
    for line in permanent_lines:
        line.delete()
    permanent_lines = []

    for segment in finalized_segments:
        smoothed = smooth_points(segment, smoothing_level)
        for i in range(len(smoothed) - 1):
            x1, y1 = smoothed[i]
            x2, y2 = smoothed[i + 1]
            line = shapes.Line(x1, y1, x2, y2, 2, color=(255, 255, 255), batch=batch)
            permanent_lines.append(line)


# Calculate the distance between two points
def distance(p1, p2):
    return ((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2) ** 0.5


# Mouse events
@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    global temp_line, track_points
    if buttons & mouse.LEFT:
        if len(track_points) > 0:
            last_x, last_y = track_points[-1]
            if temp_line:
                temp_line.delete()
            # Temporary line must be visible (gray color)
            temp_line = shapes.Line(last_x, last_y, x, y, 2, color=(200, 200, 200), batch=batch)
        add_point(x, y)


@window.event
def on_mouse_release(x, y, button, modifiers):
    global temp_line, track_points, finalized_segments
    if button == mouse.LEFT:
        if temp_line:
            temp_line.delete()
            temp_line = None
        if len(track_points) > 1:
            finalized_segments.append(track_points[:])
        track_points.clear()
        update_permanent_lines()


@window.event
def on_mouse_press(x, y, button, modifiers):
    global start_marker, end_marker, start_point, end_point
    if button == mouse.RIGHT:
        if not start_point:
            start_point = (x, y)
            start_marker = shapes.Circle(x, y, 5, color=(0, 255, 0), batch=batch)
            print("Start point set!")
        elif not end_point:
            end_point = (x, y)
            end_marker = shapes.Circle(x, y, 5, color=(255, 0, 0), batch=batch)
            print("End point set!")


# Key events
@window.event
def on_key_press(symbol, modifiers):
    global track_points, temp_line, finalized_segments
    if symbol == key.S:
        save_track()
    elif symbol == key.R:
        reset_track()
    elif symbol == key.Z:
        undo_last_segment()
    elif symbol == key.N:  # Start a new disconnected line
        track_points.clear()
        if temp_line:
            temp_line.delete()
            temp_line = None
        print("Starting a new line.")


# Save the track
def save_track():
    global finalized_segments, start_point, end_point
    data = {
        "segments": finalized_segments,
        "start_point": start_point,
        "end_point": end_point,
    }
    with open("track.json", "w", encoding="utf-8") as f:
        json.dump(data, f)
    print("Track saved!")


# Undo the last segment
def undo_last_segment():
    global finalized_segments
    if len(finalized_segments) > 0:
        finalized_segments.pop()
        update_permanent_lines()


# Reset the track
def reset_track():
    global track_points, finalized_segments, start_marker, end_marker, temp_line, permanent_lines
    track_points.clear()
    finalized_segments.clear()
    for line in permanent_lines:
        line.delete()
    permanent_lines = []
    if start_marker:
        start_marker.delete()
        start_marker = None
    if end_marker:
        end_marker.delete()
        end_marker = None
    if temp_line:
        temp_line.delete()
        temp_line = None
    print("Track reset!")


# Draw everything
@window.event
def on_draw():
    window.clear()
    batch.draw()


# Run the track maker
pyglet.app.run()
