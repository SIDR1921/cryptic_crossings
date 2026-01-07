"""
Cryptic Crossings - Streamlit Web App Version
A web-based deployment of the puzzle game using Streamlit
"""

import streamlit as st
import json
import os
from typing import Dict, List, Optional
import time

# Import our game modules
from part1_game_data import LEVELS, COLORS, ACHIEVEMENTS, get_level_count
from part2_persistence import ProgressManager
from part3_cryptarithmetic import validate_cryptarithmetic, get_puzzle_hints
from part4_missionaries_cannibals import missionaries_cannibals_game, initialize_river_challenge, Side, CharacterType

# Streamlit page configuration
st.set_page_config(
    page_title="🔢 Cryptic Crossings",
    page_icon="🔢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #2563eb;
        text-align: center;
        margin-bottom: 2rem;
    }
    .level-card {
        background-color: #f0f9ff;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 2px solid #3b82f6;
        margin: 1rem 0;
    }
    .puzzle-display {
        font-family: 'Courier New', monospace;
        font-size: 1.5rem;
        font-weight: bold;
        text-align: center;
        background-color: #e0f7fa;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .achievement-earned {
        color: #10b981;
        font-weight: bold;
    }
    .achievement-locked {
        color: #6b7280;
    }
    .river-character {
        font-size: 2rem;
        display: inline-block;
        margin: 0.5rem;
        padding: 0.5rem;
        background-color: #f3f4f6;
        border-radius: 50%;
        cursor: pointer;
    }
    .boat-area {
        background-color: #993300;
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

class StreamlitGameState:
    """Manages game state for Streamlit session"""
    
    def __init__(self):
        if 'game_state' not in st.session_state:
            st.session_state.game_state = {
                'current_level': 0,
                'crypto_solution': {},
                'river_unlocked': False,
                'level_completed': False,
                'start_time': time.time(),
                'hints_used': False,
                'achievements': set(),
                'statistics': {
                    'levels_completed': 0,
                    'total_attempts': 0,
                    'hints_used_count': 0
                }
            }
        
        self.progress_manager = ProgressManager('streamlit_progress.json')
    
    def get_state(self) -> dict:
        return st.session_state.game_state
    
    def update_state(self, updates: dict):
        st.session_state.game_state.update(updates)
    
    def reset_level(self):
        state = self.get_state()
        state.update({
            'crypto_solution': {},
            'river_unlocked': False,
            'level_completed': False,
            'start_time': time.time(),
            'hints_used': False
        })

def render_header():
    """Render the main header"""
    st.markdown('<h1 class="main-header">🔢 Cryptic Crossings</h1>', unsafe_allow_html=True)
    st.markdown("**Advanced puzzle game combining cryptarithmetic and logic challenges**")
    
def render_sidebar():
    """Render the sidebar with game controls and stats"""
    st.sidebar.header("🎮 Game Controls")
    
    game_state = StreamlitGameState()
    state = game_state.get_state()
    
    # Level selector
    current_level = st.sidebar.selectbox(
        "Select Level:",
        range(get_level_count()),
        index=state['current_level'],
        format_func=lambda x: f"Level {x+1}: {LEVELS[x]['name']}"
    )
    
    if current_level != state['current_level']:
        game_state.update_state({'current_level': current_level})
        game_state.reset_level()
        st.rerun()
    
    # Statistics
    st.sidebar.header("📊 Statistics")
    stats = state['statistics']
    st.sidebar.metric("Levels Completed", stats['levels_completed'])
    st.sidebar.metric("Total Attempts", stats['total_attempts'])
    st.sidebar.metric("Hints Used", stats['hints_used_count'])
    
    # Achievements
    st.sidebar.header("🏅 Achievements")
    for achievement_id, achievement_data in ACHIEVEMENTS.items():
        if achievement_id in state['achievements']:
            st.sidebar.markdown(f"✅ {achievement_data['icon']} {achievement_data['name']}")
        else:
            st.sidebar.markdown(f"⬜ {achievement_data['icon']} {achievement_data['name']}")
    
    # Reset button
    if st.sidebar.button("🔄 Reset Current Level"):
        game_state.reset_level()
        st.rerun()

def render_cryptarithmetic_puzzle():
    """Render the cryptarithmetic puzzle interface"""
    game_state = StreamlitGameState()
    state = game_state.get_state()
    level_data = LEVELS[state['current_level']]
    
    st.header("🔢 Cryptarithmetic Puzzle")
    
    # Display puzzle
    st.markdown(f'<div class="puzzle-display">{level_data["puzzle"]}</div>', unsafe_allow_html=True)
    
    # Display difficulty and hint
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"**Difficulty:** {level_data.get('difficulty', 'Unknown')}")
    with col2:
        if st.button("💡 Get Hint"):
            state['hints_used'] = True
            state['statistics']['hints_used_count'] += 1
            st.info(f"**Hint:** {level_data.get('hint', 'No hint available')}")
    
    # Input fields for letters
    st.subheader("Enter digit assignments:")
    
    # Create columns for input fields
    unique_letters = level_data['unique_letters']
    cols = st.columns(min(len(unique_letters), 4))
    
    solution = {}
    for i, letter in enumerate(unique_letters):
        col_index = i % 4
        with cols[col_index]:
            value = st.number_input(
                f"Letter {letter}:",
                min_value=0,
                max_value=9,
                value=state['crypto_solution'].get(letter, 0),
                key=f"input_{letter}",
                help=f"Enter digit for letter {letter}"
            )
            solution[letter] = value
    
    # Update solution in state
    game_state.update_state({'crypto_solution': solution})
    
    # Verify solution button
    if st.button("✅ Verify Solution", type="primary"):
        state['statistics']['total_attempts'] += 1
        is_valid, message = validate_cryptarithmetic(level_data, solution)
        
        if is_valid:
            st.success(f"🎉 Correct! {message}")
            game_state.update_state({'river_unlocked': True})
            
            # Check for achievements
            solve_time = time.time() - state['start_time']
            if solve_time < 30:
                state['achievements'].add('speed_demon')
                st.balloons()
                st.success("⚡ Achievement Unlocked: Speed Demon!")
            
            if not state['hints_used']:
                state['achievements'].add('no_hints')
                st.success("💪 Achievement Unlocked: Self Sufficient!")
            
            # First solve achievement
            if 'first_solve' not in state['achievements']:
                state['achievements'].add('first_solve')
                st.success("🏅 Achievement Unlocked: First Steps!")
            
        else:
            st.error(f"❌ {message}")
            
            # Show hints for incorrect solution
            hints = get_puzzle_hints(level_data, solution)
            if hints:
                st.warning("**Hints to help you:**")
                for hint in hints:
                    st.write(f"• {hint}")

def render_river_crossing():
    """Render the river crossing challenge"""
    game_state = StreamlitGameState()
    state = game_state.get_state()
    level_data = LEVELS[state['current_level']]
    
    st.header("🚣 River Crossing Challenge")
    
    if not state['river_unlocked']:
        st.warning("🔒 Solve the cryptarithmetic puzzle first to unlock this challenge!")
        return
    
    # Initialize the river challenge
    if 'river_initialized' not in state or not state['river_initialized']:
        initialize_river_challenge(
            level_data['final_m'],
            level_data['final_c'], 
            level_data['final_k']
        )
        game_state.update_state({'river_initialized': True})
    
    # Display rules
    st.info(f"**Rules:** Transport {level_data['final_m']} Missionaries (👩‍🎓) and "
           f"{level_data['final_c']} Cannibals (👹) across the river. "
           f"Boat capacity: {level_data['final_k']}. "
           f"Cannibals cannot outnumber Missionaries on either side!")
    
    # Get game state
    game_status = missionaries_cannibals_game.get_game_status()
    river_state = missionaries_cannibals_game.state
    
    # Display current state
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("🏞️ Left Bank")
        left_chars = missionaries_cannibals_game.get_characters_on_side(Side.LEFT)
        for char in left_chars:
            icon = "👩‍🎓" if char.type == CharacterType.MISSIONARY else "👹"
            if st.button(f"{icon} {char.id}", key=f"left_{char.id}"):
                success, message = missionaries_cannibals_game.add_to_boat(char.id)
                if not success:
                    st.error(message)
                else:
                    st.rerun()
    
    with col2:
        st.subheader("🚤 Boat")
        boat_side = "Left" if river_state.boat_side == Side.LEFT else "Right"
        st.write(f"**Position:** {boat_side} Bank")
        st.write(f"**Capacity:** {len(river_state.boat_crew)}/{river_state.boat_capacity}")
        
        # Show boat passengers
        boat_chars = missionaries_cannibals_game.get_characters_on_boat()
        for char in boat_chars:
            icon = "👩‍🎓" if char.type == CharacterType.MISSIONARY else "👹"
            if st.button(f"{icon} {char.id}", key=f"boat_{char.id}"):
                success, message = missionaries_cannibals_game.remove_from_boat(char.id)
                if not success:
                    st.error(message)
                else:
                    st.rerun()
        
        # Travel button
        if len(river_state.boat_crew) > 0:
            next_side = "Right" if river_state.boat_side == Side.LEFT else "Left"
            if st.button(f"🚣 Row to {next_side} Bank", type="primary"):
                success, message = missionaries_cannibals_game.travel()
                if success:
                    st.success("Boat traveled successfully!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(message)
    
    with col3:
        st.subheader("🏞️ Right Bank")
        right_chars = missionaries_cannibals_game.get_characters_on_side(Side.RIGHT)
        for char in right_chars:
            icon = "👩‍🎓" if char.type == CharacterType.MISSIONARY else "👹"
            if st.button(f"{icon} {char.id}", key=f"right_{char.id}"):
                success, message = missionaries_cannibals_game.add_to_boat(char.id)
                if not success:
                    st.error(message)
                else:
                    st.rerun()
    
    # Check win/loss conditions
    if game_status['is_game_over']:
        if game_status['is_won']:
            st.success("🎉 Level Complete! All characters safely crossed!")
            st.balloons()
            
            # Update statistics
            state['statistics']['levels_completed'] += 1
            state['level_completed'] = True
            
            # Achievement for completing level
            if state['current_level'] == get_level_count() - 1:
                state['achievements'].add('master_cryptologist')
                st.success("🧠 Achievement Unlocked: Master Cryptologist!")
            
            # Perfect crossing achievement
            if missionaries_cannibals_game.state.move_count <= get_minimum_moves(level_data):
                state['achievements'].add('efficiency_expert')
                st.success("🎪 Achievement Unlocked: Efficiency Expert!")
            
            if st.button("➡️ Next Level", type="primary"):
                if state['current_level'] < get_level_count() - 1:
                    game_state.update_state({'current_level': state['current_level'] + 1})
                    game_state.reset_level()
                    st.rerun()
                else:
                    st.success("🎊 Congratulations! You've completed all levels!")
        
        else:
            st.error("💀 Game Over! Cannibals outnumbered Missionaries. Try again!")
            if st.button("🔄 Restart Challenge"):
                missionaries_cannibals_game.restart_game()
                st.rerun()

def get_minimum_moves(level_data):
    """Calculate theoretical minimum moves for perfect crossing achievement"""
    # This is a simplified calculation - in practice this would be more complex
    m, c, k = level_data['final_m'], level_data['final_c'], level_data['final_k']
    # Rough estimate based on boat capacity and total characters
    total_chars = m + c
    return max(3, (total_chars - k) * 2 + 1)

def main():
    """Main Streamlit app"""
    render_header()
    render_sidebar()
    
    # Create two columns for the game layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        render_cryptarithmetic_puzzle()
    
    with col2:
        render_river_crossing()
    
    # Footer
    st.markdown("---")
    
if __name__ == "__main__":
    main()
