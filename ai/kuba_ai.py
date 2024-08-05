import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import random
from collections import deque
import numpy as np
from game.kuba_game import Direction, KubaGame

class DQN(nn.Module):
    def __init__(self, input_size, output_size):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(input_size, 128)
        self.fc2 = nn.Linear(128, 64)
        self.fc3 = nn.Linear(64, output_size)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)

class KubaAI:
    def __init__(self, epsilon=0.1, gamma=0.99):
        self.state_size = 7 * 7 * 3 + 1  # 7x7 board with 3 possible states per cell + current player
        self.action_size = 7 * 7 * 4  # 7x7 possible positions, 4 possible directions
        self.epsilon = epsilon
        self.gamma = gamma
        self.memory = deque(maxlen=2000)
        self.batch_size = 32

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {self.device}")
        self.model = DQN(self.state_size, self.action_size)
        self.target_model = DQN(self.state_size, self.action_size)
        self.optimizer = optim.Adam(self.model.parameters())

    def get_state_representation(self, game: KubaGame):
        state = np.zeros((7, 7, 3))
        for i in range(7):
            for j in range(7):
                marble = game.board.get_marble((i, j))
                if marble:
                    if marble.color.value == 'W':
                        state[i, j, 0] = 1
                    elif marble.color.value == 'B':
                        state[i, j, 1] = 1
                    elif marble.color.value == 'R':
                        state[i, j, 2] = 1
        
        current_player = 1 if game.current_player.color.value == 'W' else 0
        return np.concatenate([state.flatten(), [current_player]])

    def action_to_move(self, action):
        position = action // 4
        direction = action % 4
        row = position // 7
        col = position % 7
        directions = [Direction.LEFT, Direction.RIGHT, Direction.UP, Direction.DOWN]
        return ((row, col), directions[direction])

    def move_to_action(self, move):
        coordinates, direction = move
        row, col = coordinates
        position = row * 7 + col
        direction_index = [Direction.LEFT, Direction.RIGHT, Direction.UP, Direction.DOWN].index(direction)
        return position * 4 + direction_index

    def get_action(self, game: KubaGame):
        if random.random() < self.epsilon:
            return random.choice(game.get_valid_moves())
        else:
            state = self.get_state_representation(game)
            with torch.no_grad():
                state_tensor = torch.FloatTensor(state).to(self.device)
                q_values = self.model(state_tensor)
                valid_moves = game.get_valid_moves()
                valid_actions = [self.move_to_action(move) for move in valid_moves]
                valid_q_values = q_values[valid_actions]
                best_action_index = valid_q_values.argmax().item()
                return valid_moves[best_action_index]

    def update_model(self):
        if len(self.memory) < self.batch_size:
            return

        batch = random.sample(self.memory, self.batch_size)
        states, actions, rewards, next_states, dones = map(np.array, zip(*batch))

        states = torch.FloatTensor(states).to(self.device)
        actions = torch.LongTensor(actions).to(self.device)
        rewards = torch.FloatTensor(rewards).to(self.device)
        next_states = torch.FloatTensor(next_states).to(self.device)
        dones = torch.FloatTensor(dones).to(self.device)

        current_q_values = self.model(states).gather(1, actions.unsqueeze(1))
        next_q_values = self.target_model(next_states).max(1)[0]
        target_q_values = rewards + (1 - dones) * self.gamma * next_q_values

        loss = F.mse_loss(current_q_values, target_q_values.unsqueeze(1))
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

    def update_target_model(self):
        self.target_model.load_state_dict(self.model.state_dict())

    def save_model(self, filename):
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'target_model_state_dict': self.target_model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
        }, filename)

    def load_model(self, filename):
        checkpoint = torch.load(filename, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.target_model.load_state_dict(checkpoint['target_model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])

    def evaluate_state(self, game: KubaGame):
        current_player = game.current_player
        opponent = game.opponent
        
        # Count marbles
        marble_counts = game.get_game_state()
        
        # Evaluate position
        score = 0
        score += 10 * (current_player.captured_red - opponent.captured_red)  # Captured red marbles
        score += 5 * (8 - marble_counts[opponent.color.value])  # Removed opponent marbles
        score += 2 * (marble_counts[current_player.color.value] - marble_counts[opponent.color.value])  # Marble advantage
        score += self.evaluate_control(game, current_player.color.value)  # Board control
        score += self.evaluate_distance_to_victory(game, current_player)
        
        return score
    
    def evaluate_distance_to_victory(self, game, player):
        marbles_to_win = 7 - player.captured_red
        return (8 - marbles_to_win) * 5 

    def evaluate_control(self, game: KubaGame, color):
        control_score = 0
        for i in range(7):
            for j in range(7):
                marble = game.board.get_marble((i, j))
                if not marble:
                    continue
                if marble.color.value == color:
                    if (i == 0 or i == 6) and (j == 0 or j == 6):  # Corners
                        control_score += 3
                    elif i == 0 or i == 6 or j == 0 or j == 6:  # Edges
                        control_score += 2
                    elif 2 <= i <= 4 and 2 <= j <= 4:  # Center
                        control_score += 1
        return control_score

def train_ai(num_episodes=10, ai_model_file="kuba_ai_model.pth"):
    ai = KubaAI()
    try:
        ai.load_model(ai_model_file)
        print("Loaded pre-trained AI model.")
        return ai
    except FileNotFoundError:
        print("No pre-trained model found. Starting from scratch.")

    for episode in range(num_episodes):
        game = KubaGame()
        state = ai.get_state_representation(game)
        total_reward = 0
        
        while not game.winner:
            action = ai.get_action(game)
            coordinates, direction = action
            game.make_move(coordinates, direction)
            next_state = ai.get_state_representation(game)
            
            reward = ai.evaluate_state(game)
            if game.winner == game.opponent:
                reward -= 1000
            elif game.winner == game.current_player:
                reward += 1000

            done = game.winner is not None
            ai.memory.append((state, ai.move_to_action(action), reward, next_state, done))
            
            ai.update_model()
            if episode % 10 == 0:
                ai.update_target_model()

            state = next_state
            total_reward += reward

        print(f"Episode {episode}, Total Reward: {total_reward}")
        if episode % 100 == 0:
            ai.save_model(ai_model_file)

    ai.save_model(ai_model_file)
    return ai