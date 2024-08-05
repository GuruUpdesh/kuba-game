import queue
import random
from collections import defaultdict
import pickle
import multiprocessing as mp
from tqdm import tqdm

from game.kuba_game import KubaGame

class KubaAI:
    def __init__(self, epsilon=0.1, alpha=0.1, gamma=0.9, look_ahead_depth=2):
        self.q_table = defaultdict(self.default_dict_factory)
        self.epsilon = epsilon
        self.alpha = alpha
        self.gamma = gamma
        self.look_ahead_depth = look_ahead_depth

    @staticmethod
    def default_dict_factory():
        return defaultdict(float)

    def get_state_key(self, game: KubaGame):
        board_state = tuple(tuple(row) for row in game.board.grid)
        return (board_state, game.current_player.color.value)

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
        # score += self.evaluate_potential_moves(game, current_player)
        score += self.evaluate_distance_to_victory(game, current_player)
        
        return score
    
    # def evaluate_potential_moves(self, game, player):
    #     return len(game.get_valid_moves()) * 0.5
    
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

    def get_action(self, game):
        if random.random() < self.epsilon:
            return random.choice(game.get_valid_moves())
        else:
            return self.get_best_move(game, self.look_ahead_depth)

    def get_best_move(self, game, depth):
        best_score = float('-inf')
        best_move = None
        for move in game.get_valid_moves():
            new_game = game.clone()
            new_game.make_move(*move)
            score = self.minimax(new_game, depth - 1, False)
            if score > best_score:
                best_score = score
                best_move = move
        return best_move

    def minimax(self, game, depth, maximizing_player):
        if depth == 0 or game.winner:
            return self.evaluate_state(game)
        
        if maximizing_player:
            max_eval = float('-inf')
            for move in game.get_valid_moves():
                new_game = game.clone()
                new_game.make_move(*move)
                eval = self.minimax(new_game, depth - 1, False)
                max_eval = max(max_eval, eval)
            return max_eval
        else:
            min_eval = float('inf')
            for move in game.get_valid_moves():
                new_game = game.clone()
                new_game.make_move(*move)
                eval = self.minimax(new_game, depth - 1, True)
                min_eval = min(min_eval, eval)
            return min_eval

    def update_q_value(self, state, action, next_state, reward, done):
        current_q = self.q_table[state][tuple(action)]
        if not self.q_table[next_state]:
            max_next_q = 0
        else:
            max_next_q = max(self.q_table[next_state].values())
        new_q = current_q + self.alpha * (reward + self.gamma * max_next_q - current_q)
        self.q_table[state][tuple(action)] = new_q

    def save_model(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(dict(self.q_table), f)

    def load_model(self, filename):
        with open(filename, 'rb') as f:
            loaded_dict = pickle.load(f)
            self.q_table = defaultdict(self.default_dict_factory, loaded_dict)

def train_ai(num_episodes=10000):
    ai = KubaAI()
    for episode in range(num_episodes):
        game = KubaGame()
        state = ai.get_state_key(game)
        while not game.winner:
            action = ai.get_action(game)
            coordinates, direction = action
            game.make_move(coordinates, direction)
            next_state = ai.get_state_key(game)
            
            reward = ai.evaluate_state(game)
            # if game.winner == game.current_player:
            #     reward += 1000
            if game.winner == game.opponent:
                reward -= 1000

            done = game.winner is not None
            ai.update_q_value(state, action, next_state, reward, done)
            state = next_state

        if episode:
            print(f"Episode {episode} completed")

    return ai

# def train_ai_worker(num_episodes, shared_q, worker_id):
#     ai = KubaAI()
#     for _ in range(num_episodes):
#         game = KubaGame()
#         state = ai.get_state_key(game)
#         episode_steps = 0
#         max_steps = 1000  # Add a maximum number of steps per episode
#         while not game.winner and episode_steps < max_steps:
#             action = ai.get_action(game)
#             coordinates, direction = action
#             game.make_move(coordinates, direction)
#             next_state = ai.get_state_key(game)
            
#             reward = ai.evaluate_state(game)
#             if game.winner == game.opponent:
#                 reward -= 1000
#             elif game.winner == game.current_player:
#                 reward += 1000
#             elif episode_steps == max_steps - 1:
#                 reward -= 500  # Penalize for reaching max steps

#             done = game.winner is not None or episode_steps == max_steps - 1
#             ai.update_q_value(state, action, next_state, reward, done)
#             state = next_state
#             episode_steps += 1

#         shared_q.put((worker_id, 1))  # Signal completion of an episode

#     shared_q.put(('q_table', ai.q_table))  # Send the final Q-table

# def train_ai_parallel(num_episodes=10000, num_processes=None):
    if num_processes is None:
        num_processes = mp.cpu_count()

    episodes_per_process = num_episodes // num_processes
    manager = mp.Manager()
    shared_q = manager.Queue()

    with mp.Pool(num_processes) as pool:
        workers = [pool.apply_async(train_ai_worker, (episodes_per_process, shared_q, i)) for i in range(num_processes)]
        
        with tqdm(total=num_episodes, desc="Training Progress") as pbar:
            q_tables = []
            completed_episodes = 0
            while completed_episodes < num_episodes or len(q_tables) < num_processes:
                try:
                    result = shared_q.get(timeout=1)  # Add a timeout
                    if isinstance(result, tuple) and result[0] == 'q_table':
                        q_tables.append(result[1])
                    else:
                        completed_episodes += 1
                        pbar.update(1)
                except queue.Empty:
                    # Check if all workers are done
                    if all(worker.ready() for worker in workers):
                        break

        # Ensure all workers have finished
        for worker in workers:
            worker.wait()

        # Collect any remaining Q-tables
        while not shared_q.empty():
            result = shared_q.get()
            if isinstance(result, tuple) and result[0] == 'q_table':
                q_tables.append(result[1])

    # Combine Q-tables from all processes
    combined_q_table = defaultdict(KubaAI.default_dict_factory)
    for q_table in q_tables:
        for state, actions in q_table.items():
            for action, value in actions.items():
                combined_q_table[state][action] += value / num_processes

    ai = KubaAI()
    ai.q_table = combined_q_table
    return ai

def train_or_load_ai(filename, training_episodes=10000):
    try:
        ai = KubaAI()
        ai.load_model(filename)
        print("Loaded pre-trained AI model.")
        return ai
    except FileNotFoundError:
        print(f"No pre-trained model found. Training new AI with {training_episodes} episodes...")
        ai = train_ai(training_episodes)
        ai.save_model(filename)
        print("AI training complete and model saved.")
        return ai

AI_MODEL_FILE = "./ai/models/kuba_ai_model.pkl"