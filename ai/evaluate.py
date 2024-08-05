import numpy as np
from tqdm import tqdm
from ai.kuba_ai import KubaAI
from game.kuba_game import KubaGame


def play_game(ai1, ai2, max_moves=200):
    game = KubaGame()
    moves = 0
    while not game.winner and moves < max_moves:
        current_ai = ai1 if game.current_player.name == "Player1" else ai2
        action = current_ai.get_action(game)
        if action is None:
            break
        coordinates, direction = action
        game.make_move(coordinates, direction)
        moves += 1
    
    return game.winner, moves

def evaluate_models(model1_file, model2_file, num_games=1000):
    ai1 = KubaAI()
    ai2 = KubaAI()
    ai1.load_model(model1_file)
    ai2.load_model(model2_file)

    wins = {None: 0, "You": 0, "Bot": 0}
    total_moves = 0
    move_counts = []

    for _ in tqdm(range(num_games), desc="Playing games"):
        winner, moves = play_game(ai1, ai2)
        wins[winner.name if winner else None] += 1
        total_moves += moves
        move_counts.append(moves)

    avg_moves = total_moves / num_games
    median_moves = np.median(move_counts)

    print(f"\nResults after {num_games} games:")
    print(f"Model 1 wins: {wins['You']} ({wins['Bot']/num_games:.2%})")
    print(f"Model 2 wins: {wins['You']} ({wins['Bot']/num_games:.2%})")
    print(f"Draws: {wins[None]} ({wins[None]/num_games:.2%})")
    print(f"Average moves per game: {avg_moves:.2f}")
    print(f"Median moves per game: {median_moves}")
    print(f"Total moves across all games: {total_moves}")

    if wins['You'] > wins['Bot']:
        print("Model 1 performed better overall.")
    elif wins['You'] > wins['Bot']:
        print("Model 2 performed better overall.")
    else:
        print("Both models performed equally.")

if __name__ == "__main__":
    model1_file = "kuba_ai_model-10.pkl"
    model2_file = "kuba_ai_model-200.pkl"
    evaluate_models(model1_file, model2_file, num_games=100)