import json
from pyglet import shapes
import os


class Track:
    def __init__(self, batch, save_file="game_objects/Track/track.json"):
        """
        Initialize the Track object to load, manage, and render track segments.

        Args:
            batch (pyglet.graphics.Batch): Pyglet batch for rendering.
            save_file (str): Path to the track JSON file.
        """
        self.segments = []  # Store segments as lists of connected points
        self.start_point = None  # Starting point for the car
        self.end_point = None  # Ending point of the track
        self.batch = batch
        self.lines = []  # Store line shapes for rendering
        self.save_file = save_file

        # Load the track from the file if it exists
        if os.path.exists(self.save_file):
            self.load()

    def add_segment(self, segment):
        """
        Add a new segment to the track.

        Args:
            segment (list): A list of (x, y) tuples representing a track segment.
        """
        self.segments.append(segment)
        self._create_line_shapes(segment)

    def set_start(self, x, y):
        """Set the starting point of the track."""
        self.start_point = (x, y)
        self.start_marker = shapes.Circle(x, y, 5, color=(0, 255, 0), batch=self.batch)

    def set_end(self, x, y):
        """Set the ending point of the track."""
        self.end_point = (x, y)
        self.end_marker = shapes.Circle(x, y, 5, color=(255, 0, 0), batch=self.batch)

    def reset(self):
        """Clear the track and all associated markers."""
        self.segments = []
        self.lines = []
        self.start_point = None
        self.end_point = None

    def save(self):
        """Save the track data to a file."""
        data = {
            "segments": self.segments,
            "start_point": self.start_point,
            "end_point": self.end_point,
        }
        with open(self.save_file, "w") as f:
            json.dump(data, f)

    def load(self):
        """Load the track data from a file."""
        with open(self.save_file, "r") as f:
            data = json.load(f)
        self.segments = data.get("segments", [])
        self.start_point = data.get("start_point")
        self.end_point = data.get("end_point")

        # Render the segments and markers
        self._render_segments()
        if self.start_point:
            self.start_marker = shapes.Circle(
                self.start_point[0], self.start_point[1], 5, color=(0, 255, 0), batch=self.batch
            )
        if self.end_point:
            self.end_marker = shapes.Circle(
                self.end_point[0], self.end_point[1], 5, color=(255, 0, 0), batch=self.batch
            )

    def _render_segments(self):
        """Render all track segments."""
        self.lines = []
        for segment in self.segments:
            self._create_line_shapes(segment)

    def _create_line_shapes(self, segment):
        """
        Create line shapes for a segment.

        Args:
            segment (list): A list of (x, y) tuples representing a track segment.
        """
        for i in range(len(segment) - 1):
            x1, y1 = segment[i]
            x2, y2 = segment[i + 1]
            line = shapes.Line(x1, y1, x2, y2, 2, color=(255, 255, 255), batch=self.batch)
            self.lines.append(line)

    def get_track_data(self):
        """
        Get the loaded track data.

        Returns:
            dict: The track data (segments, start_point, end_point).
        """
        return {
            "segments": self.segments,
            "start_point": self.start_point,
            "end_point": self.end_point,
        }
