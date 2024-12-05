import pyglet

class GameWindow:
    def __init__(self, width=1600, height=900, title="Driver", background_color=(25, 25, 25)):
        """
        Initialize the game window and configure global settings.

        Args:
            width (int): Width of the window.
            height (int): Height of the window.
            title (str): Title of the game window.
            background_color (tuple): Background color in RGB format (0-255).
        """
        self.width = width
        self.height = height
        self.title = title
        self.background_color = background_color

        # Initialize the game window
        self.window = pyglet.window.Window(self.width, self.height, self.title)
        self.batch = pyglet.graphics.Batch()  # Central rendering batch

        # Set background color (RGBA values normalized to [0, 1])
        pyglet.gl.glClearColor(*[c / 255 for c in self.background_color], 1)

        # Frame rate configuration
        self.frame_rate = 1 / 60.0  # 60 FPS

        # Resource path setup
        pyglet.resource.path = ['resources']
        pyglet.resource.reindex()

        # Load car image resource
        self.car_image = pyglet.resource.image('car.png')
        self.car_image.anchor_x = self.car_image.width // 2
        self.car_image.anchor_y = self.car_image.height // 2

    def get_window(self):
        """Return the pyglet window instance."""
        return self.window

    def get_batch(self):
        """Return the central rendering batch."""
        return self.batch

    def get_frame_rate(self):
        """Return the frame rate for the game."""
        return self.frame_rate

    def get_car_image(self):
        """Return the car image resource."""
        return self.car_image

    def schedule_update(self, update_func):
        """
        Schedule a function to be called at the specified frame rate.

        Args:
            update_func (function): The function to be called at each frame update.
        """
        pyglet.clock.schedule_interval(update_func, self.frame_rate)
