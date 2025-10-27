# Part 6: River Crossing UI & Game Controller
# Contributor: Frontend Developer (River UI) / Integration Lead
# Responsible for: River visualization, character interaction, boat mechanics, sound effects, main game flow

"""
River crossing user interface and main game controller for Cryptic Crossings.
Handles river visualization, character interactions, boat mechanics, sound effects, and overall game flow.
"""

import tkinter as tk
from tkinter import messagebox
import random
import time
from typing import Dict, List, Optional, Tuple, Callable

# Try to import sound libraries
try:
    import pygame
    import numpy as np
    pygame.mixer.init()
    SOUND_ENABLED = True
except ImportError:
    print("Pygame not installed. Sound effects will be disabled. Install with: pip install pygame numpy")
    SOUND_ENABLED = False

from part1_game_data import LEVELS, COLORS, LAYOUT, POSITIONING, ICONS, get_level_count
from part2_persistence import load_progress, save_progress, record_attempt
from part4_missionaries_cannibals import (
    missionaries_cannibals_game, initialize_river_challenge, 
    Side, CharacterType, Character
)
from part5_crypto_ui import CryptarithmeticUI

class SoundManager:
    """Manages game sound effects."""
    
    def __init__(self):
        self.sounds = {}
        self._initialize_sounds()
    
    def _initialize_sounds(self):
        """Initialize sound effects using pygame and numpy."""
        if not SOUND_ENABLED:
            self.sounds = {
                'success': lambda: None,
                'fail': lambda: None,
                'move': lambda: None,
                'click': lambda: None
            }
            return
        
        try:
            # Generate simple sine wave tones
            def generate_tone(frequency: float, duration: float, sample_rate: int = 44100):
                frames = int(duration * sample_rate)
                arr = np.zeros(frames)
                
                for i in range(frames):
                    arr[i] = np.sin(2 * np.pi * frequency * i / sample_rate)
                
                arr = (arr * 32767).astype(np.int16)
                
                # Handle stereo/mono
                try:
                    mixer_init = pygame.mixer.get_init()
                    channels = mixer_init[2] if mixer_init else 1
                except:
                    channels = 1
                
                if channels == 2:
                    arr = np.column_stack((arr, arr))
                
                return arr
            
            # Create sound effects
            self.sounds['success'] = pygame.sndarray.make_sound(generate_tone(523, 0.2))  # C note
            self.sounds['fail'] = pygame.sndarray.make_sound(generate_tone(200, 0.3))     # Low tone
            self.sounds['move'] = pygame.sndarray.make_sound(generate_tone(800, 0.1))     # High beep
            self.sounds['click'] = pygame.sndarray.make_sound(generate_tone(1000, 0.05))  # Quick click
            
        except Exception as e:
            print(f"Error initializing sounds: {e}")
            self.sounds = {
                'success': lambda: None,
                'fail': lambda: None,
                'move': lambda: None,
                'click': lambda: None
            }
    
    def play(self, sound_name: str):
        """Play a sound effect."""
        if sound_name in self.sounds and SOUND_ENABLED:
            try:
                pygame.mixer.Sound.play(self.sounds[sound_name])
            except:
                pass  # Silently fail if sound can't play

class RiverCrossingUI:
    """Manages the river crossing visualization and interactions."""
    
    def __init__(self, parent_frame: tk.Frame, sound_manager: SoundManager, on_complete_callback: Callable[[], None] = None):
        self.parent_frame = parent_frame
        self.sound_manager = sound_manager
        self.on_complete_callback = on_complete_callback
        
        # UI Components
        self.main_frame = None
        self.canvas = None
        self.control_frame = None
        self.crew_label = None
        self.travel_button = None
        self.restart_button = None
        self.level_label = None
        self.rule_label = None
        
        # Visual elements
        self.char_icons = {}
        self.boat_id = None
        
        # State
        self.is_unlocked = False
        
        self._create_ui()
    
    def _create_ui(self):
        """Create the river crossing UI components."""
        # Main container
        self.main_frame = tk.Frame(
            self.parent_frame,
            bg=COLORS['river_bg'],
            bd=2,
            relief=tk.GROOVE,
            padx=LAYOUT['padding'],
            pady=LAYOUT['padding']
        )
        self.main_frame.pack(side=tk.RIGHT, fill="both", expand=True, padx=LAYOUT['padding'], pady=LAYOUT['padding'])
        
        # Title
        title_label = tk.Label(
            self.main_frame,
            text="🚣 River Crossing Challenge",
            font=(LAYOUT['font_family'], LAYOUT['title_font_size'], "bold"),
            bg=COLORS['river_bg'],
            fg=COLORS['text_dark']
        )
        title_label.pack(pady=5)
        
        # Rules display
        self.rule_label = tk.Label(
            self.main_frame,
            text="Solve the cryptarithmetic puzzle to unlock this challenge!",
            bg=COLORS['warning_yellow'],
            fg=COLORS['text_dark'],
            padx=10,
            pady=5,
            wraplength=600,
            justify=tk.CENTER
        )
        self.rule_label.pack(pady=5, fill=tk.X)
        
        # River canvas
        self.canvas = tk.Canvas(
            self.main_frame,
            width=LAYOUT['canvas_width'],
            height=LAYOUT['canvas_height'],
            bg=COLORS['river_water'],
            highlightthickness=0
        )
        self.canvas.pack(pady=10)
        
        # Control panel
        self._create_control_panel()
        
        # Initialize empty display
        self._draw_static_elements()
    
    def _create_control_panel(self):
        """Create the control panel at the bottom."""
        self.control_frame = tk.Frame(
            self.main_frame,
            bg='#f9f9f9',
            padx=LAYOUT['padding'],
            pady=LAYOUT['padding']
        )
        self.control_frame.pack(pady=10, fill=tk.X)
        
        # Left side - crew info
        crew_frame = tk.Frame(self.control_frame, bg='#f9f9f9')
        crew_frame.pack(side=tk.LEFT)
        
        tk.Label(
            crew_frame,
            text="Boat Crew: ",
            font=(LAYOUT['font_family'], LAYOUT['body_font_size']),
            bg='#f9f9f9'
        ).pack(side=tk.LEFT)
        
        self.crew_label = tk.Label(
            crew_frame,
            text="0",
            font=(LAYOUT['font_family'], LAYOUT['body_font_size'], "bold"),
            bg='white',
            fg=COLORS['text_blue'],
            width=4,
            relief=tk.RIDGE
        )
        self.crew_label.pack(side=tk.LEFT)
        
        # Center - level info
        self.level_label = tk.Label(
            self.control_frame,
            text="",
            font=(LAYOUT['font_family'], LAYOUT['body_font_size'], "bold"),
            bg='#f9f9f9',
            fg=COLORS['text_blue']
        )
        self.level_label.pack(side=tk.LEFT, padx=20)
        
        # Right side - action buttons
        button_frame = tk.Frame(self.control_frame, bg='#f9f9f9')
        button_frame.pack(side=tk.RIGHT)
        
        self.restart_button = tk.Button(
            button_frame,
            text="Restart Puzzle",
            command=self._restart_river_challenge,
            font=(LAYOUT['font_family'], LAYOUT['small_font_size']),
            bg=COLORS['error_red'],
            fg='white',
            relief=tk.RAISED
        )
        self.restart_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        self.travel_button = tk.Button(
            button_frame,
            text="Row Boat (0 on board)",
            command=self._travel_boat,
            font=(LAYOUT['font_family'], LAYOUT['body_font_size'], "bold"),
            bg='#059669',
            fg='white',
            relief=tk.RAISED,
            state=tk.DISABLED
        )
        self.travel_button.pack(side=tk.RIGHT)
    
    def _draw_static_elements(self):
        """Draw static elements like river banks."""
        canvas_width = LAYOUT['canvas_width']
        canvas_height = LAYOUT['canvas_height']
        bank_width = canvas_width * POSITIONING['bank_ratio']
        
        # Clear canvas
        self.canvas.delete("all")
        
        # Left bank
        self.canvas.create_rectangle(
            0, 0, bank_width, canvas_height,
            fill=COLORS['bank_color'],
            outline=COLORS['bank_color']
        )
        self.canvas.create_text(
            bank_width / 2, 20,
            text="Left Bank",
            font=(LAYOUT['font_family'], LAYOUT['small_font_size'], "bold"),
            fill=COLORS['text_gray']
        )
        
        # Right bank
        self.canvas.create_rectangle(
            canvas_width - bank_width, 0, canvas_width, canvas_height,
            fill=COLORS['bank_color'],
            outline=COLORS['bank_color']
        )
        self.canvas.create_text(
            canvas_width - (bank_width / 2), 20,
            text="Right Bank",
            font=(LAYOUT['font_family'], LAYOUT['small_font_size'], "bold"),
            fill=COLORS['text_gray']
        )
    
    def unlock_challenge(self, missionaries: int, cannibals: int, boat_capacity: int):
        """
        Unlock and initialize the river crossing challenge.
        
        Args:
            missionaries (int): Number of missionaries
            cannibals (int): Number of cannibals  
            boat_capacity (int): Boat capacity
        """
        self.is_unlocked = True
        initialize_river_challenge(missionaries, cannibals, boat_capacity)
        self._update_display()
        self._update_rule_display(missionaries, cannibals, boat_capacity)
    
    def lock_challenge(self):
        """Lock the challenge and show locked state."""
        self.is_unlocked = False
        self._draw_static_elements()
        self.rule_label.config(
            text="Solve the cryptarithmetic puzzle to unlock this challenge!",
            bg=COLORS['warning_yellow']
        )
        self.travel_button.config(state=tk.DISABLED)
        self.crew_label.config(text="0")
    
    def _update_display(self):
        """Update the complete river crossing display."""
        if not self.is_unlocked:
            return
        
        self._draw_static_elements()
        self._draw_boat()
        self._draw_characters()
        self._update_controls()
    
    def _draw_boat(self):
        """Draw the boat on the current side."""
        game_state = missionaries_cannibals_game.state
        canvas_width = LAYOUT['canvas_width']
        bank_width = canvas_width * POSITIONING['bank_ratio']
        
        boat_width = POSITIONING['boat_width']
        boat_height = POSITIONING['boat_height']
        boat_y = POSITIONING['boat_y_position']
        padding = POSITIONING['boat_padding']
        
        # Calculate boat position
        if game_state.boat_side == Side.LEFT:
            boat_x = bank_width - boat_width + padding
        else:
            boat_x = canvas_width - bank_width - padding
        
        # Draw boat
        self.boat_id = self.canvas.create_polygon(
            boat_x, boat_y,
            boat_x + boat_width, boat_y,
            boat_x + boat_width, boat_y + boat_height,
            boat_x, boat_y + boat_height,
            fill=COLORS['boat_color'],
            outline=COLORS['boat_outline'],
            width=2,
            smooth=True
        )
    
    def _draw_characters(self):
        """Draw all characters in their current positions."""
        self.char_icons = {}
        
        left_chars = missionaries_cannibals_game.get_characters_on_side(Side.LEFT)
        right_chars = missionaries_cannibals_game.get_characters_on_side(Side.RIGHT)
        boat_chars = missionaries_cannibals_game.get_characters_on_boat()
        
        # Draw left side characters
        self._draw_side_characters(left_chars, Side.LEFT)
        
        # Draw right side characters  
        self._draw_side_characters(right_chars, Side.RIGHT)
        
        # Draw boat characters
        self._draw_boat_characters(boat_chars)
    
    def _draw_side_characters(self, characters: List[Character], side: Side):
        """Draw characters on a specific side."""
        canvas_width = LAYOUT['canvas_width']
        bank_width = canvas_width * POSITIONING['bank_ratio']
        
        if side == Side.LEFT:
            start_x = POSITIONING['character_start_x']
            chars_per_row = POSITIONING['characters_per_row_left']
        else:
            start_x = canvas_width - bank_width + POSITIONING['character_start_x']
            chars_per_row = POSITIONING['characters_per_row_right']
        
        for i, char in enumerate(characters):
            row = i // chars_per_row
            col = i % chars_per_row
            
            x = start_x + col * POSITIONING['character_spacing_x']
            y = POSITIONING['character_start_y'] + row * POSITIONING['character_spacing_y']
            
            icon = ICONS['missionary'] if char.type == CharacterType.MISSIONARY else ICONS['cannibal']
            
            char_id = self.canvas.create_text(
                x, y,
                text=icon,
                font=(LAYOUT['font_family'], LAYOUT['icon_font_size'])
            )
            
            # Bind click event
            self.canvas.tag_bind(char_id, '<Button-1>', 
                               lambda event, c_id=char.id: self._on_character_click(c_id))
            
            self.char_icons[char.id] = char_id
    
    def _draw_boat_characters(self, characters: List[Character]):
        """Draw characters on the boat."""
        game_state = missionaries_cannibals_game.state
        canvas_width = LAYOUT['canvas_width']
        bank_width = canvas_width * POSITIONING['bank_ratio']
        
        boat_width = POSITIONING['boat_width']
        boat_y = POSITIONING['boat_y_position']
        padding = POSITIONING['boat_padding']
        
        # Calculate boat position
        if game_state.boat_side == Side.LEFT:
            boat_x = bank_width - boat_width + padding
        else:
            boat_x = canvas_width - bank_width - padding
        
        for i, char in enumerate(characters):
            x = boat_x + 20 + i * 20  # Space characters across boat
            y = boat_y + 10
            
            icon = ICONS['missionary'] if char.type == CharacterType.MISSIONARY else ICONS['cannibal']
            
            char_id = self.canvas.create_text(
                x, y,
                text=icon,
                font=(LAYOUT['font_family'], LAYOUT['icon_font_size'])
            )
            
            # Bind click event
            self.canvas.tag_bind(char_id, '<Button-1>', 
                               lambda event, c_id=char.id: self._on_character_click(c_id))
            
            self.char_icons[char.id] = char_id
    
    def _on_character_click(self, character_id: str):
        """Handle character click events."""
        if not self.is_unlocked:
            messagebox.showinfo("Locked", "Solve the cryptarithmetic puzzle first to unlock the boat!")
            return
        
        self.sound_manager.play('click')
        
        character = missionaries_cannibals_game.get_character(character_id)
        if not character:
            return
        
        # Determine action based on character location
        if character_id in missionaries_cannibals_game.state.boat_crew:
            # Remove from boat
            success, message = missionaries_cannibals_game.remove_from_boat(character_id)
        else:
            # Add to boat (if on same side)
            success, message = missionaries_cannibals_game.add_to_boat(character_id)
        
        if not success:
            messagebox.showwarning("Action Failed", message)
        
        self._update_display()
    
    def _travel_boat(self):
        """Handle boat travel action."""
        if not self.is_unlocked:
            return
        
        success, message = missionaries_cannibals_game.travel()
        
        if success:
            self.sound_manager.play('move')
            self._update_display()
            
            # Check game status after a short delay
            self.main_frame.after(1000, self._check_game_status)
        else:
            messagebox.showerror("Travel Failed", message)
    
    def _check_game_status(self):
        """Check for win/loss conditions."""
        game_status = missionaries_cannibals_game.get_game_status()
        
        if game_status['is_game_over']:
            if game_status['is_won']:
                self.sound_manager.play('success')
                # Notify parent controller of completion
                if self.on_complete_callback:
                    self.on_complete_callback()
                return True  # Signal win to parent controller
            else:
                self.sound_manager.play('fail')
                messagebox.showerror(
                    "Game Over", 
                    "FAILURE! Cannibals outnumbered Missionaries on a bank. Resetting challenge."
                )
                self._restart_river_challenge()
        
        return False
    
    def _restart_river_challenge(self):
        """Restart the current river challenge."""
        if self.is_unlocked:
            missionaries_cannibals_game.restart_game()
            self._update_display()
    
    def _update_controls(self):
        """Update control panel state."""
        game_state = missionaries_cannibals_game.state
        
        # Update crew count
        self.crew_label.config(text=str(len(game_state.boat_crew)))
        
        # Update travel button
        can_travel = self.is_unlocked and len(game_state.boat_crew) > 0
        self.travel_button.config(state=tk.NORMAL if can_travel else tk.DISABLED)
        
        next_side = 'Right' if game_state.boat_side == Side.LEFT else 'Left'
        self.travel_button.config(
            text=f"Row Boat {next_side} ({len(game_state.boat_crew)} on board)"
        )
    
    def _update_rule_display(self, missionaries: int, cannibals: int, boat_capacity: int):
        """Update the rules display with current challenge parameters."""
        rules_text = (
            f"Rules: Transport {missionaries} Missionaries ({ICONS['missionary']}) and "
            f"{cannibals} Cannibals ({ICONS['cannibal']}). Boat capacity: {boat_capacity}. "
            f"Cannibals cannot outnumber Missionaries on either side!"
        )
        self.rule_label.config(
            text=rules_text,
            bg='#f0f9ff'
        )
    
    def update_level_display(self, level_index: int):
        """Update the level display."""
        self.level_label.config(text=f"Level {level_index + 1}")

class CrypticCrossingsGame:
    """Main game controller that coordinates all components."""
    
    def __init__(self, master: tk.Tk):
        self.master = master
        self._setup_window()
        
        # Components
        self.sound_manager = SoundManager()
        self.main_frame = None
        self.crypto_ui = None
        self.river_ui = None
        
        # Game state
        self.current_level = 0
        self.highest_level_completed = load_progress()
        
        self._create_ui()
        self._load_level(min(self.highest_level_completed, get_level_count() - 1))
    
    def _setup_window(self):
        """Setup main window properties."""
        self.master.title("Cryptic Crossings")
        self.master.geometry(f"{LAYOUT['window_width']}x{LAYOUT['window_height']}")
        self.master.resizable(False, False)
        self.master.configure(bg=COLORS['main_bg'])
    
    def _create_ui(self):
        """Create the main UI layout."""
        self.main_frame = tk.Frame(
            self.master,
            padx=LAYOUT['padding'],
            pady=LAYOUT['padding'],
            bg=COLORS['main_bg']
        )
        self.main_frame.pack(fill="both", expand=True)
        
        # Create crypto UI (left panel)
        self.crypto_ui = CryptarithmeticUI(self.main_frame, self._on_crypto_solution)
        
        # Create river UI (right panel)
        self.river_ui = RiverCrossingUI(self.main_frame, self.sound_manager, self._on_river_complete)
    
    def _on_crypto_solution(self, is_valid: bool):
        """Handle cryptarithmetic solution callback."""
        level_data = LEVELS[self.current_level]
        
        if is_valid:
            # Unlock river challenge
            self.river_ui.unlock_challenge(
                level_data['final_m'],
                level_data['final_c'],
                level_data['final_k']
            )
            record_attempt(self.current_level, 'cryptarithmetic', True)
        else:
            # Keep locked
            self.river_ui.lock_challenge()
            record_attempt(self.current_level, 'cryptarithmetic', False)
    
    def _on_river_complete(self):
        """Handle river crossing completion."""
        record_attempt(self.current_level, 'river_crossing', True)
        
        # Update progress
        if self.current_level >= self.highest_level_completed:
            self.highest_level_completed = self.current_level + 1
            save_progress(self.highest_level_completed)
        
        # Show completion message
        messagebox.showinfo(
            "Level Complete",
            f"Level {self.current_level + 1} Solved! Deciphering the next cryptic challenge."
        )
        
        # Load next level or show completion
        if self.current_level < get_level_count() - 1:
            self._load_level(self.current_level + 1)
        else:
            messagebox.showinfo(
                "Master Cryptologist",
                "CONGRATULATIONS! You have mastered all Cryptic Crossings!"
            )
            self._load_level(0)  # Restart from beginning
    
    def _load_level(self, level_index: int):
        """Load a specific level."""
        if not (0 <= level_index < get_level_count()):
            return
        
        self.current_level = level_index
        
        # Update both UIs
        self.crypto_ui.load_level(level_index)
        self.river_ui.update_level_display(level_index)
        self.river_ui.lock_challenge()  # Start locked
    
    def run(self):
        """Start the main game loop."""
        self.master.mainloop()

def main():
    """Main entry point for the application."""
    root = tk.Tk()
    game = CrypticCrossingsGame(root)
    game.run()

if __name__ == "__main__":
    main()
