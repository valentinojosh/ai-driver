import numpy as np
import tensorflow as tf

class AIController:
    def __init__(self, state_size, action_size, learning_rate=0.001, gamma=0.95, epsilon=1.0, epsilon_decay=0.995, epsilon_min=0.1):
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min

        # Q-Network
        self.model = self.build_model()

    def build_model(self):
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(24, input_dim=self.state_size, activation='relu'),
            tf.keras.layers.Dense(24, activation='relu'),
            tf.keras.layers.Dense(self.action_size, activation='linear')
        ])
        model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=self.learning_rate), loss='mse')
        return model

    def get_action(self, state):
        """Choose an action based on the epsilon-greedy policy."""
        if np.random.rand() < self.epsilon:
            return np.random.choice(self.action_size)  # Explore
        q_values = self.model.predict(np.array([state]), verbose=0)
        return np.argmax(q_values[0])  # Exploit

    def train(self, state, action, reward, next_state, done):
        """Train the Q-network."""
        target = reward
        if not done:
            next_q_values = self.model.predict(np.array([next_state]), verbose=0)
            target = reward + self.gamma * np.amax(next_q_values[0])
        target_q_values = self.model.predict(np.array([state]), verbose=0)
        target_q_values[0][action] = target
        self.model.fit(np.array([state]), target_q_values, epochs=1, verbose=0)

        # Update epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
