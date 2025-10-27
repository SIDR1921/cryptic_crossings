# NOTE: Requires separate installation: pip install pygame numpy
import tkinter as tk
from tkinter import messagebox
import json
import os
import random
import time
try:
    import pygame
    import numpy as np
    pygame.mixer.init()
    SOUND_ENABLED = True
except ImportError:
    print("Pygame not installed. Sound effects will be disabled. Install with: pip install pygame numpy")
    SOUND_ENABLED = False

# --- 1. GLOBAL GAME DATA & CONFIGURATION ---

SAVE_FILE = "cryptic_crossings_progress.json"

# Levels data: Using the classic, solvable SEND + MORE = MONEY for Level 1
LEVELS = [
    {
        'puzzle': 'S E N D\n+ M O R E\n= M O N E Y',
        'words': ['SEND', 'MORE', 'MONEY'],
        'unique_letters': ['S', 'E', 'N', 'D', 'M', 'O', 'R', 'Y'],
        'final_m': 3, 'final_c': 3, 'final_k': 2, # Classic M&C rules
    },
    {
        'puzzle': 'T W O\n+ T W O\n= F O U R',
        'words': ['TWO', 'TWO', 'FOUR'],
        'unique_letters': ['T', 'W', 'O', 'F', 'U', 'R'],
        'final_m': 4, 'final_c': 4, 'final_k': 3,
    },
    {
        'puzzle': 'T H I S\n+ I S\n= G O O D',
        'words': ['THIS', 'IS', 'GOOD'],
        'unique_letters': ['T', 'H', 'I', 'S', 'G', 'O', 'D'],
        'final_m': 5, 'final_c': 5, 'final_k': 3,
    }
]

# --- 2. PERSISTENCE (Local JSON File) ---

def load_progress():
    """Loads the highest level completed from a local JSON file."""
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, 'r') as f:
                data = json.load(f)
                return data.get('highest_level_completed', 0)
        except json.JSONDecodeError:
            return 0
    return 0

def save_progress(level_index):
    """Saves the highest level completed to a local JSON file."""
    data = {'highest_level_completed': level_index}
    with open(SAVE_FILE, 'w') as f:
        json.dump(data, f)

# --- 3. HELPER FUNCTIONS (Cryptarithmetic) ---

def get_num(word, guess_map):
    """Converts a word (list of characters) into an integer using the guess map."""
    number_str = ""
    for char in word:
        if char not in guess_map:
             raise ValueError(f"Letter {char} missing in guess map.")
        number_str += str(guess_map.get(char))
    return int(number_str)

def validate_cryptarithmetic(level_data, current_guess):
    """Validates the three main rules of Cryptarithmetic."""
    letters = level_data['unique_letters']
    words = level_data['words']
    
    if len(current_guess) != len(letters):
        return False, "Error: All letters must be assigned a digit."
    
    assigned_digits = list(current_guess.values())
    if len(set(d for d in assigned_digits if d is not None)) != len(assigned_digits):
        return False, "Error: Digits must be unique."

    for word in words:
        if current_guess.get(word[0]) == 0:
            return False, f"Error: The leading letter '{word[0]}' cannot be zero."

    try:
        num1 = get_num(words[0], current_guess)
        num2 = get_num(words[1], current_guess)
        result_num = get_num(words[2], current_guess)
    except ValueError as e:
        return False, f"Input error: {e}" 

    if num1 + num2 != result_num:
        return False, f"Arithmetic Error: {num1} + {num2} != {result_num}"
    
    return True, "Success! The rules are deciphered."

# --- 4. M&C LOGIC & STATE MACHINE ---

def is_safe(m, c):
    """Checks the core M&C safety constraint: C <= M or M = 0."""
    if m == 0:
        return True
    return c <= m

class CrypticCrossingsGame:
    def __init__(self, master):
        self.master = master
        master.title("Cryptic Crossings")
        # --- INCREASED WINDOW SIZE FOR WIDER RIVER CANVAS ---
        master.geometry("1200x700") 
        master.resizable(False, False)
        
        # --- Game State ---
        self.current_level_index = 0
        self.highest_level_completed = load_progress()
        self.state = {
            'M_L': 0, 'C_L': 0, 'M_R': 0, 'C_R': 0,
            'boat_side': 'left',
            'total_m': 0, 'total_c': 0, 'boat_capacity': 0,
            'boat_crew': [],
            'is_unlocked': False,
            'current_guess': {},
            'characters': []
        }
        
        # --- UI Components ---
        self.main_frame = tk.Frame(master, padx=10, pady=10, bg='#f0f4f8')
        self.main_frame.pack(fill="both", expand=True)

        self.crypt_frame = tk.Frame(self.main_frame, width=300, bg='#e0f7fa', bd=2, relief=tk.GROOVE, padx=10, pady=10)
        self.crypt_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        self.river_frame = tk.Frame(self.main_frame, bg='#ffffff', bd=2, relief=tk.GROOVE, padx=10, pady=10)
        self.river_frame.pack(side=tk.RIGHT, fill="both", expand=True, padx=10, pady=10)

        self.create_crypt_widgets()
        self.create_river_widgets()
        
        self.load_level(min(self.highest_level_completed, len(LEVELS) - 1))

    # --- 5. CRYPTARITHMETIC UI & LOGIC ---

    def create_crypt_widgets(self):
        """Creates the Cryptarithmetic input panel."""
        tk.Label(self.crypt_frame, text="🔢 Decipher the Rules", font=("Inter", 16, "bold"), bg='#e0f7fa').pack(pady=5)
        
        self.puzzle_text_frame = tk.Frame(self.crypt_frame, bg='#e0f7fa')
        self.puzzle_text_frame.pack(pady=10)
        
        self.input_frame = tk.Frame(self.crypt_frame, bg='#e0f7fa')
        self.input_frame.pack(pady=10)
        
        self.guess_entries = {}
        
        self.feedback_label = tk.Label(self.crypt_frame, text="", font=("Inter", 10), bg='#e0f7fa', fg='red')
        self.feedback_label.pack(pady=5)
        
        self.solve_button = tk.Button(self.crypt_frame, text="Verify Solution", command=self.solve_puzzle, 
                                     font=("Inter", 12, "bold"), bg='#10b981', fg='white', relief=tk.RAISED)
        self.solve_button.pack(pady=10, fill=tk.X)
        
        self.error_display = tk.Entry(self.crypt_frame, font=("Courier", 12), bd=2, relief=tk.SUNKEN, justify=tk.LEFT, state='readonly')
        self.error_display.pack(pady=5, fill=tk.X)

    def render_cryptarithmetic(self):
        """Populates the UI with the current level's puzzle."""
        level_data = LEVELS[self.current_level_index]
        
        for widget in self.puzzle_text_frame.winfo_children():
            widget.destroy()
        tk.Label(self.puzzle_text_frame, text=level_data['puzzle'], font=("Courier", 16), 
                 justify=tk.CENTER, bg='#e0f7fa', fg='#333333').pack()
        
        for widget in self.input_frame.winfo_children():
            widget.destroy()
        self.guess_entries = {}
        self.state['current_guess'] = {}
        
        for letter in level_data['unique_letters']:
            var = tk.StringVar(self.master)
            # Simple, robust callback for input changes
            def on_input_change(name, index, mode, letter=letter, var=var):
                content = var.get()
                print(f"DEBUG: {letter} changed to '{content}' (len={len(content)})")
                
                # Limit to 1 character
                if len(content) > 1:
                    var.set(content[-1])  # Keep the last character typed
                    content = var.get()
                
                # Update the guess immediately
                if content == "":
                    # Deletion case
                    if letter in self.state['current_guess']:
                        del self.state['current_guess'][letter]
                        print(f"DEBUG: Deleted {letter} from guess")
                    self.feedback_label.config(text="", fg='gray')
                elif content.isdigit():
                    # Valid digit case
                    digit = int(content)
                    # Check for duplicates
                    duplicate_found = False
                    for l, d in self.state['current_guess'].items():
                        if d == digit and l != letter:
                            self.feedback_label.config(text=f"Error: {digit} is already assigned to {l}.", fg='red')
                            var.set("")
                            if letter in self.state['current_guess']:
                                del self.state['current_guess'][letter]
                            duplicate_found = True
                            break
                    
                    if not duplicate_found:
                        self.state['current_guess'][letter] = digit
                        self.feedback_label.config(text="", fg='gray')
                        print(f"DEBUG: Set {letter} = {digit}")
                else:
                    # Invalid input case
                    var.set("")
                    if letter in self.state['current_guess']:
                        del self.state['current_guess'][letter]
                
                print(f"DEBUG: Current guess: {self.state['current_guess']}")
            
            var.trace_add('write', on_input_change)
            
            frame = tk.Frame(self.input_frame, bg='#e0f7fa')
            frame.pack(side=tk.LEFT, padx=5, pady=5)
            
            tk.Label(frame, text=letter, font=("Inter", 10, "bold"), bg='#e0f7fa', fg='#1e40af').pack()
            entry = tk.Entry(frame, textvariable=var, width=3, font=("Inter", 14), justify=tk.CENTER, fg='black')
            entry.pack()
            self.guess_entries[letter] = var
            
        self.feedback_label.config(text="Enter your solution to decipher the river rules.", fg='gray')
        self.error_display.config(state='normal')
        self.error_display.delete(0, tk.END)
        self.error_display.insert(0, "")
        self.error_display.config(state='readonly')
        self.master.update_idletasks()

    def solve_puzzle(self):
        """Handles the solve button click and locks/unlocks the M&C game."""
        guess_map = self.state['current_guess']
        level_data = LEVELS[self.current_level_index]
        
        is_valid, message = validate_cryptarithmetic(level_data, guess_map)
        
        self.error_display.config(state='normal')
        self.error_display.delete(0, tk.END)
        self.error_display.config(state='readonly')
        
        if is_valid:
            if SOUND_ENABLED: pygame.mixer.Sound.play(self.sfx['success'])
            
            self.state['is_unlocked'] = True
            self.feedback_label.config(text=message, fg='green')
            
            M = level_data['final_m']
            C = level_data['final_c']
            K = level_data['final_k']
            self.init_river_challenge(M, C, K, False)
        else:
            if SOUND_ENABLED: pygame.mixer.Sound.play(self.sfx['fail'])
            self.state['is_unlocked'] = False
            self.feedback_label.config(text="Solution Invalid. Check below for details.", fg='red')
            
            self.error_display.config(state='normal')
            self.error_display.delete(0, tk.END)
            self.error_display.insert(0, message)
            self.error_display.config(state='readonly')
            
            self.render_river_crossing()

    # --- 6. RIVER CROSSING UI & LOGIC ---

    def create_river_widgets(self):
        """Creates the main River Crossing layout."""
        self.setup_sfx()

        tk.Label(self.river_frame, text="River Crossing Challenge", font=("Inter", 18, "bold"), bg='white').pack(pady=5)
        
        rule_text = tk.StringVar(self.master)
        self.rule_label = tk.Label(self.river_frame, textvariable=rule_text, bg='#fffbe3', fg='#333333', padx=10, pady=5)
        self.rule_label.pack(pady=5, fill=tk.X)
        self.rule_text = rule_text
        
        # --- INCREASED CANVAS WIDTH ---
        self.river_canvas = tk.Canvas(self.river_frame, width=800, height=350, bg='#3b82f6', highlightthickness=0)
        self.river_canvas.pack(pady=10)
        self.draw_river_banks()
        
        control_frame = tk.Frame(self.river_frame, bg='#f9f9f9', padx=10, pady=10)
        control_frame.pack(pady=10, fill=tk.X)

        tk.Label(control_frame, text="Boat Crew: ", font=("Inter", 12), bg='#f9f9f9').pack(side=tk.LEFT)
        self.crew_label = tk.Label(control_frame, text="0", font=("Inter", 12, "bold"), bg='#ffffff', fg='#1e40af', width=4, relief=tk.RIDGE)
        self.crew_label.pack(side=tk.LEFT)
        
        self.travel_button = tk.Button(control_frame, text="Row Boat Right (0 on board)", command=self.travel,
                                       font=("Inter", 12, "bold"), bg='#059669', fg='white', relief=tk.RAISED, state=tk.DISABLED)
        self.travel_button.pack(side=tk.RIGHT, padx=20)
        
        self.restart_button = tk.Button(control_frame, text="Restart Puzzle", command=lambda: self.init_river_challenge(self.state['total_m'], self.state['total_c'], self.state['boat_capacity'], True),
                                     font=("Inter", 10), bg='#ef4444', fg='white', relief=tk.RAISED)
        self.restart_button.pack(side=tk.RIGHT)

        self.current_level_label = tk.Label(control_frame, text="", font=("Inter", 12, "bold"), bg='#f9f9f9', fg='#1e40af')
        self.current_level_label.pack(side=tk.LEFT, padx=10)

        self.boat_id = None
        self.boat_pos = 'left'
        self.char_icons = {}

    def setup_sfx(self):
        """Initializes simple sound effects using pygame mixer."""
        self.sfx = {}
        if SOUND_ENABLED:
            def _generate_sine_wave(freq, duration, samplerate=44100):
                t = np.linspace(0, duration, int(samplerate * duration), False)
                amplitude = np.iinfo(np.int16).max * 0.2
                note = amplitude * np.sin(2 * np.pi * freq * t)
                arr = np.int16(note)
                try:
                    mixer_init = pygame.mixer.get_init()
                    channels = mixer_init[2] if mixer_init is not None else 1
                except Exception:
                    channels = 1
                if channels == 2 and arr.ndim == 1:
                    arr = np.column_stack((arr, arr))
                return arr
                
            self.sfx['success'] = pygame.sndarray.make_sound(_generate_sine_wave(440, 0.1))
            self.sfx['fail'] = pygame.sndarray.make_sound(_generate_sine_wave(150, 0.2))
            self.sfx['move'] = pygame.sndarray.make_sound(_generate_sine_wave(2000, 0.05))
        else:
            self.sfx['success'] = lambda: None; self.sfx['fail'] = lambda: None; self.sfx['move'] = lambda: None

    def draw_river_banks(self):
        """Draws the static bank graphics."""
        # W is the canvas width (now 800)
        W, H = 800, 350
        BANK_RATIO = 0.30 # Increased to 0.30 for even wider banks (240px each)
        
        # Left Bank 
        self.river_canvas.create_rectangle(0, 0, W * BANK_RATIO, H, fill='#d1d5db', outline='#d1d5db')
        self.river_canvas.create_text(W * BANK_RATIO / 2, 20, text="Left Bank", font=("Inter", 10, "bold"), fill='#374151')
        
        # Right Bank 
        self.river_canvas.create_rectangle(W * (1 - BANK_RATIO), 0, W, H, fill='#d1d5db', outline='#d1d5db')
        self.river_canvas.create_text(W * (1 - BANK_RATIO / 2), 20, text="Right Bank", font=("Inter", 10, "bold"), fill='#374151')

    def render_river_crossing(self):
        """Clears the canvas and redraws all elements based on the current state."""
        self.river_canvas.delete("all")
        self.draw_river_banks()
        W = 800 # Canvas width
        BANK_RATIO = 0.30 # Updated to match draw_river_banks
        BANK_WIDTH = W * BANK_RATIO # 240 pixels
        
        # Draw boat
        boat_color = '#993300'
        boat_width = 80
        boat_height = 40
        boat_y = 300
        
        # Dock the boat relative to the bank edges
        # Left: Dock at BANK_WIDTH - boat_width + buffer (10px)
        # Right: Dock at W - BANK_WIDTH - buffer (10px)
        x_offset = BANK_WIDTH - boat_width + 10 if self.state['boat_side'] == 'left' else W - BANK_WIDTH - 10
        
        self.boat_id = self.river_canvas.create_polygon(
            x_offset, boat_y, 
            x_offset + boat_width, boat_y, 
            x_offset + boat_width, boat_y + boat_height, 
            x_offset, boat_y + boat_height, 
            fill=boat_color, smooth=True, outline='#7c2d12', width=2
        )
        
        self.char_icons = {}
        m_count_left, c_count_left = 0, 0
        m_count_right, c_count_right = 0, 0
        
        for char in self.state['characters']:
            icon = "👩‍🎓" if char['type'] == 'M' else "👹"
            
            x, y = 0, 0
            
            if char['location'] == 'left':
                # Start icons 10px from the left edge of the canvas
                # Arrange in rows if needed
                total_left = m_count_left + c_count_left
                row = total_left // 4  # 4 characters per row
                col = total_left % 4
                x, y = 10 + col * 40, 50 + row * 50
                if char['type'] == 'M': m_count_left += 1
                else: c_count_left += 1
                
            elif char['location'] == 'right':
                # Start icons 10px from the inner edge of the Right Bank
                right_bank_start_x = W * (1 - BANK_RATIO) + 10 # 800 * 0.70 + 10 = 570
                
                # Arrange in rows if needed for better spacing
                total_right = m_count_right + c_count_right
                row = total_right // 5  # 5 characters per row for more space
                col = total_right % 5
                x, y = right_bank_start_x + col * 40, 50 + row * 50
                
                if char['type'] == 'M': m_count_right += 1
                else: c_count_right += 1
                
            elif char['location'] == 'boat':
                try:
                    idx = self.state['boat_crew'].index(char['id'])
                    x, y = x_offset + 20 + idx * 20, boat_y + 10
                except ValueError:
                    continue
            
            icon_id = self.river_canvas.create_text(x, y, text=icon, font=("Inter", 24))
            self.river_canvas.tag_bind(icon_id, '<Button-1>', lambda event, char_id=char['id']: self.select_character(char_id))
            self.char_icons[char['id']] = icon_id

        can_travel = self.state['is_unlocked'] and len(self.state['boat_crew']) > 0
        self.travel_button.config(state=tk.NORMAL if can_travel else tk.DISABLED)
        
        next_side = 'Right' if self.state['boat_side'] == 'left' else 'Left'
        self.travel_button.config(text=f"Row Boat {next_side} ({len(self.state['boat_crew'])} on board)")
        
        self.crew_label.config(text=str(len(self.state['boat_crew'])))
        
        self.rule_text.set(
            f"Rules: Transport {self.state['total_m']} Missionaries (👩‍🎓) and {self.state['total_c']} Cannibals (👹). Boat capacity is {self.state['boat_capacity']}."
        )
        self.current_level_label.config(text=f"Level {self.current_level_index + 1}")
        self.master.update_idletasks()

    def select_character(self, char_id):
        """Handles character selection to move to/from the boat."""
        if not self.state['is_unlocked']:
            messagebox.showinfo("Locked", "Solve the Cryptarithmetic puzzle first to unlock the boat!")
            return

        char = next((c for c in self.state['characters'] if c['id'] == char_id), None)
        if not char: return

        current_location = char['location']
        
        # --- Move FROM Boat to Bank ---
        if current_location == 'boat':
            char['location'] = self.state['boat_side']
            self.state['boat_crew'].remove(char_id)
            if self.state['boat_side'] == 'left':
                if char['type'] == 'M': self.state['M_L'] += 1
                else: self.state['C_L'] += 1
            else:
                if char['type'] == 'M': self.state['M_R'] += 1
                else: self.state['C_R'] += 1
                
        # --- Move FROM Bank to Boat ---
        elif current_location == self.state['boat_side']:
            if len(self.state['boat_crew']) < self.state['boat_capacity']:
                char['location'] = 'boat'
                self.state['boat_crew'].append(char_id)
                if current_location == 'left':
                    if char['type'] == 'M': self.state['M_L'] -= 1
                    else: self.state['C_L'] -= 1
                else:
                    if char['type'] == 'M': self.state['M_R'] -= 1
                    else: self.state['C_R'] -= 1
            else:
                messagebox.showerror("Capacity Limit", f"The boat capacity is only {self.state['boat_capacity']}. Please deselect a passenger.")
        else:
            messagebox.showwarning("Boat Location", f"The boat is currently at the {self.state['boat_side'].capitalize()} Bank.")

        self.render_river_crossing()

    def travel(self):
        """Handles the boat crossing the river."""
        if len(self.state['boat_crew']) == 0:
            messagebox.showerror("Empty Boat", "The boat must have at least one passenger!")
            return

        if SOUND_ENABLED: pygame.mixer.Sound.play(self.sfx['move'])
            
        new_side = 'right' if self.state['boat_side'] == 'left' else 'left'
        self.state['boat_side'] = new_side
        
        for char_id in self.state['boat_crew']:
             char = next((c for c in self.state['characters'] if c['id'] == char_id), None)
             if char:
                char['location'] = new_side 
                
                if new_side == 'left':
                    if char['type'] == 'M': self.state['M_L'] += 1
                    else: self.state['C_L'] += 1
                else: 
                    if char['type'] == 'M': self.state['M_R'] += 1
                    else: self.state['C_R'] += 1
                
        self.state['boat_crew'] = []
        
        self.render_river_crossing() 
        
        self.master.after(1000, self.check_game_status) 

    def check_game_status(self):
        """Checks for win/loss conditions after a move."""
        M_L, C_L = self.state['M_L'], self.state['C_L']
        M_R, C_R = self.state['M_R'], self.state['C_R']
        
        # Loss Condition
        if not is_safe(M_L, C_L) or not is_safe(M_R, C_R):
            if SOUND_ENABLED: pygame.mixer.Sound.play(self.sfx['fail'])
            messagebox.showerror("Game Over", "FAILURE! Cannibals outnumbered Missionaries on a bank. Resetting challenge.")
            self.init_river_challenge(self.state['total_m'], self.state['total_c'], self.state['boat_capacity'], True)
            return

        # Win Condition
        if M_L == 0 and C_L == 0:
            if SOUND_ENABLED: pygame.mixer.Sound.play(self.sfx['success'])
            
            messagebox.showinfo("Level Complete", f"Level {self.current_level_index + 1} Solved! Deciphering the next cryptic challenge.")
            
            if self.current_level_index >= self.highest_level_completed:
                self.highest_level_completed = self.current_level_index + 1
                save_progress(self.highest_level_completed)
            
            if self.current_level_index < len(LEVELS) - 1:
                self.load_level(self.current_level_index + 1)
            else:
                messagebox.showinfo("Master Cryptologist", "CONGRATULATIONS! You have mastered all Cryptic Crossings!")
                self.load_level(0) 

    # --- 7. INITIALIZATION & FLOW CONTROL ---

    def init_river_challenge(self, m_total, c_total, capacity, force_reset):
        """Resets the M&C state based on solved parameters."""
        if not self.state['is_unlocked'] and not force_reset: return

        self.state['total_m'] = m_total
        self.state['total_c'] = c_total
        self.state['boat_capacity'] = capacity
        self.state['boat_side'] = 'left'
        
        self.state['M_L'] = m_total
        self.state['C_L'] = c_total
        self.state['M_R'] = 0
        self.state['C_R'] = 0
        self.state['boat_crew'] = []

        self.state['characters'] = []
        char_id = 1
        for _ in range(m_total):
            self.state['characters'].append({'id': f'M{char_id}', 'type': 'M', 'location': 'left'})
            char_id += 1
        for _ in range(c_total):
            self.state['characters'].append({'id': f'C{char_id}', 'type': 'C', 'location': 'left'})
            char_id += 1

        self.render_river_crossing()

    def load_level(self, index):
        """Loads a new level, resetting the Cryptarithmetic UI."""
        if index >= len(LEVELS):
            messagebox.showinfo("Complete", "You've finished all levels! Restarting from Level 1.")
            index = 0
            
        self.current_level_index = index
        
        self.state['total_m'] = 0
        self.state['total_c'] = 0
        self.state['boat_capacity'] = 0
        self.state['is_unlocked'] = False
        self.state['characters'] = []

        self.render_cryptarithmetic()
        self.render_river_crossing() 

# --- Main Application Loop ---
if __name__ == '__main__':
    root = tk.Tk()
    game = CrypticCrossingsGame(root)
    root.mainloop()
