# Cryptic Crossings - Complete Integrated Game
# This file integrates all 6 contributor parts into a single working application

"""
Complete Cryptic Crossings game - Integration of all 6 parts.
This file demonstrates how all contributor parts work together.
"""

# Import all parts
from part1_game_data import LEVELS, COLORS, LAYOUT, get_level_count
from part2_persistence import load_progress, save_progress, progress_manager
from part3_cryptarithmetic import validate_cryptarithmetic, cryptarithmetic_solver
from part4_missionaries_cannibals import missionaries_cannibals_game, initialize_river_challenge
from part5_crypto_ui import CryptarithmeticUI
from part6_river_ui_controller import CrypticCrossingsGame, main

# For backward compatibility, create a simplified entry point
def run_game():
    """Run the complete Cryptic Crossings game."""
    main()

if __name__ == "__main__":
    print("🔢 Cryptic Crossings - Integrated Game")
    print("=" * 50)
    print("Starting game with all 6 contributor parts:")
    print("1. Game Data & Configuration (part1_game_data.py)")
    print("2. Persistence & Progress (part2_persistence.py)")  
    print("3. Cryptarithmetic Logic (part3_cryptarithmetic.py)")
    print("4. Missionaries & Cannibals Logic (part4_missionaries_cannibals.py)")
    print("5. Cryptarithmetic UI (part5_crypto_ui.py)")
    print("6. River UI & Controller (part6_river_ui_controller.py)")
    print("=" * 50)
    
    run_game()
