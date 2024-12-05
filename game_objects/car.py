import math
import pyglet


class Car:
    def __init__(self, x, y, car_image, batch, scale=0.2):
        self.x = x
        self.y = y
        self.rotation = 90  # Angle in degrees
        self.velocity = 0  # Current speed
        self.acceleration = 300  # Acceleration rate (pixels per second squared)
        self.max_speed = 600  # Maximum speed (pixels per second)
        self.friction = 200  # Friction to slow down the car when no input
        self.turn_speed = 120  # Turning speed (degrees per second)
        self.batch = batch  # Rendering batch

        car_image.anchor_x = car_image.width // 2
        car_image.anchor_y = car_image.height // 2
        self.sprite = pyglet.sprite.Sprite(car_image, x=self.x, y=self.y, batch=self.batch)
        self.sprite.scale = scale

        self.width = car_image.width * scale
        self.height = car_image.height * scale

        self.ray_length = 400  # Max distance the rays can reach
        self.num_rays = 8  # Rays distributed around the car
        self.rays = []
        self.dots = []  # Store intersection dots
        for _ in range(self.num_rays):
            line = pyglet.shapes.Line(0, 0, 0, 0, 1, color=(200, 200, 200, 100), batch=batch)
            self.rays.append(line)

        self.last_action = None  # Last action taken by AI

    def perform_action(self, action):
        """Perform an action based on AI's decision."""
        if action == 0:  # Accelerate
            self.velocity += self.acceleration * 0.1
        elif action == 1:  # Decelerate
            self.velocity -= self.acceleration * 0.1
        elif action == 2:  # Turn left
            self.rotation += self.turn_speed * 0.1
        elif action == 3:  # Turn right
            self.rotation -= self.turn_speed * 0.1

    def apply_manual_input(self, keys, dt):
        """Apply manual control based on key inputs."""
        if keys.get('up', False):
            self.velocity += self.acceleration * dt
        elif keys.get('down', False):
            self.velocity -= self.acceleration * dt
        else:
            # Apply friction
            if self.velocity > 0:
                self.velocity = max(0, self.velocity - self.friction * dt)
            elif self.velocity < 0:
                self.velocity = min(0, self.velocity + self.friction * dt)

        # Limit velocity to max speed
        self.velocity = max(-self.max_speed, min(self.max_speed, self.velocity))

        # Steering logic
        if abs(self.velocity) > 0:  # Only turn if the car is moving
            if keys.get('left', False):
                self.rotation += self.turn_speed * dt * (-1 if self.velocity < 0 else 1)
            if keys.get('right', False):
                self.rotation -= self.turn_speed * dt * (-1 if self.velocity < 0 else 1)

    def get_corners(self):
        """Calculate the four corners of the rotated car rectangle."""
        radians = math.radians(self.rotation)
        dx = self.width / 2
        dy = self.height / 2

        # Calculate corner offsets
        corners = [
            (self.x + math.cos(radians) * dx - math.sin(radians) * dy,  # Top-right
             self.y + math.sin(radians) * dx + math.cos(radians) * dy),
            (self.x - math.cos(radians) * dx - math.sin(radians) * dy,  # Top-left
             self.y - math.sin(radians) * dx + math.cos(radians) * dy),
            (self.x - math.cos(radians) * dx + math.sin(radians) * dy,  # Bottom-left
             self.y - math.sin(radians) * dx - math.cos(radians) * dy),
            (self.x + math.cos(radians) * dx + math.sin(radians) * dy,  # Bottom-right
             self.y + math.sin(radians) * dx - math.cos(radians) * dy)
        ]
        return corners

    def cast_rays(self, track_data):
        """
        Cast rays outward from specific points around the car and detect intersections.

        Args:
            track_data (dict): Contains 'segments' of the track for collision detection.

        Returns:
            list: Distances to the nearest obstacle for each ray.
        """
        segments = track_data["segments"]
        distances = []  # Store distances for AI or debugging

        # Define specific ray angles (relative to the car's rotation)
        ray_angles = [0, 45, -45, 90, -90, 135, -135, 180]  # Degrees

        for i, ray in enumerate(self.rays):
            angle = math.radians(self.rotation + ray_angles[i])  # Calculate ray angle
            end_x = self.x + math.cos(angle) * self.ray_length
            end_y = self.y + math.sin(angle) * self.ray_length
            min_distance = self.ray_length
            closest_point = None

            # Check intersections with track segments
            for segment in segments:
                for j in range(len(segment) - 1):
                    x1, y1 = segment[j]
                    x2, y2 = segment[j + 1]
                    intersection = self.line_intersection(self.x, self.y, end_x, end_y, x1, y1, x2, y2)
                    if intersection:
                        dist = math.sqrt((intersection[0] - self.x) ** 2 + (intersection[1] - self.y) ** 2)
                        if dist < min_distance:
                            min_distance = dist
                            closest_point = intersection

            # Update ray visuals to always extend the full length
            ray.x = self.x
            ray.y = self.y
            ray.x2 = end_x  # Extend fully
            ray.y2 = end_y

            # Render a temporary dot at the intersection point
            if closest_point:
                dot = pyglet.shapes.Circle(
                    closest_point[0], closest_point[1], 3, color=(255, 255, 255), batch=self.batch
                )
                dot.opacity = 200  # Semi-transparent dot
                dot.draw()  # Render immediately without storing it persistently

            # Debugging output for ray data
            # print(f"Ray {i}: Start ({self.x}, {self.y}) -> End ({ray.x2}, {ray.y2}), Intersection: {closest_point}")

            distances.append(min_distance)

        return distances

    @staticmethod
    def line_intersection(x1, y1, x2, y2, x3, y3, x4, y4):
        """Check if two line segments intersect and return the intersection point."""
        def det(a, b, c, d):
            return a * d - b * c

        denom = det(x1 - x2, y1 - y2, x3 - x4, y3 - y4)
        if denom == 0:
            return None  # Lines are parallel

        px = det(det(x1, y1, x2, y2), x1 - x2, det(x3, y3, x4, y4), x3 - x4) / denom
        py = det(det(x1, y1, x2, y2), y1 - y2, det(x3, y3, x4, y4), y3 - y4) / denom

        if min(x1, x2) <= px <= max(x1, x2) and min(y1, y2) <= py <= max(y1, y2) and \
           min(x3, x4) <= px <= max(x3, x4) and min(y3, y4) <= py <= max(y3, y4):
            return px, py
        return None

    def reset(self, start_point):
        """Reset the car to the start position and reset its rotation."""
        self.x, self.y = start_point
        self.rotation = 90
        self.velocity = 0
        self.sprite.x = self.x
        self.sprite.y = self.y
        self.sprite.rotation = -self.rotation

    def check_collision(self, track_data):
        """Check if the car collides with the track."""
        segments = track_data["segments"]
        corners = self.get_corners()
        edges = [
            (corners[0], corners[1]),  # Top edge
            (corners[1], corners[2]),  # Left edge
            (corners[2], corners[3]),  # Bottom edge
            (corners[3], corners[0])   # Right edge
        ]

        for edge in edges:
            for segment in segments:
                for i in range(len(segment) - 1):
                    x1, y1 = segment[i]
                    x2, y2 = segment[i + 1]
                    if self.line_intersection(*edge[0], *edge[1], x1, y1, x2, y2):
                        return True
        return False

    def update(self, dt, keys, track_data, ai_controller=None):
        """Update the car's position and handle collision detection."""
        if ai_controller:
            distances = self.cast_rays(track_data)
            state = tuple(distances + [self.velocity])
            action = ai_controller.get_action(state)
            self.perform_action(action)
            self.last_action = action
        else:
            self.apply_manual_input(keys, dt)

        # Calculate new position
        radians = math.radians(self.rotation)
        dx = math.cos(radians) * self.velocity * dt
        dy = math.sin(radians) * self.velocity * dt
        new_x = self.x + dx
        new_y = self.y + dy

        # Check for collisions
        if not self.check_collision(track_data):
            self.x = new_x
            self.y = new_y
        else:
            # Collision detected, reset car
            if "start_point" in track_data and track_data["start_point"]:
                self.reset(track_data["start_point"])

        # Update sprite position and rotation
        self.sprite.x = self.x
        self.sprite.y = self.y
        self.sprite.rotation = -self.rotation
