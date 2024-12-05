from pyglet.window import key


class Controls:
    def __init__(self):
        """
        Initialize Controls to handle manual and AI inputs.
        """
        self.key_handler = key.KeyStateHandler()  # Key state handler for manual control
        self.ai_enabled = False  # Toggle for AI control

    def attach_to_window(self, window):
        """
        Attach the key state handler to the game window.

        Args:
            window (pyglet.window.Window): The game window.
        """
        window.push_handlers(self.key_handler)
        window.push_handlers(self)

    def on_key_press(self, symbol, modifiers):
        """
        Handle key press events.

        Args:
            symbol (int): The key symbol pressed.
            modifiers (int): Any modifier keys (e.g., Shift).
        """
        if symbol == key.A:
            self.ai_enabled = not self.ai_enabled
            print("AI control enabled." if self.ai_enabled else "AI control disabled.")

    def get_manual_input(self):
        """
        Get the current manual input state.

        Returns:
            dict: A dictionary mapping actions to their states (True/False).
        """
        return {
            'up': self.key_handler[key.UP],
            'down': self.key_handler[key.DOWN],
            'left': self.key_handler[key.LEFT],
            'right': self.key_handler[key.RIGHT],
        }

    def is_ai_enabled(self):
        """
        Check if AI control is currently enabled.

        Returns:
            bool: True if AI is enabled, False otherwise.
        """
        return self.ai_enabled
