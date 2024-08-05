import time
import random
from tqdm import tqdm
import cProfile
import pstats
import io
from pstats import SortKey
from kuba_game import KubaGame

def play_random_game():
    game = KubaGame()
    while not game.winner:
        moves = game.get_valid_moves()
        if not moves:
            break
        move = random.choice(moves)
        game.make_move(move[0], move[1])
    return game.moves

def performance_test(duration=20):
    start_time = time.time()
    end_time = start_time + duration
    games_played = 0
    total_moves = 0

    # Initialize tqdm progress bar
    pbar = tqdm(total=duration, desc="Running games", unit="s")

    while time.time() < end_time:
        moves = play_random_game()
        games_played += 1
        total_moves += moves
        
        # Update progress bar
        elapsed = time.time() - start_time
        pbar.n = min(elapsed, duration)
        pbar.refresh()

    elapsed_time = time.time() - start_time
    pbar.close()
    
    print(f"\nPerformance Test Results (Duration: {elapsed_time:.2f} seconds):")
    print(f"Games played: {games_played}")
    print(f"Total moves: {total_moves}")
    print(f"Average moves per game: {total_moves / games_played:.2f}")
    print(f"Games per second: {games_played / elapsed_time:.2f}")
    print(f"Moves per second: {total_moves / elapsed_time:.2f}")

def performance_test_with_profiling(duration=20):
    pr = cProfile.Profile()
    pr.enable()

    performance_test(duration)

    pr.disable()
    s = io.StringIO()
    sortby = SortKey.CUMULATIVE
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats(10)  # Print top 10 time-consuming functions
    print(s.getvalue())
    

if __name__ == "__main__":
    performance_test_with_profiling(20)
    # performance_test(1)