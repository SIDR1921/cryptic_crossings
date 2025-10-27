# Part 5: Cryptarithmetic User Interface
# Contributor: Frontend Developer (Crypto UI)
# Responsible for: Puzzle display, input management, feedback system, solution interface

"""
Cryptarithmetic user interface module for Cryptic Crossings.
Handles puzzle display, user input, validation feedback, and solution verification.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Callable, Optional
from part1_game_data import LEVELS, COLORS, LAYOUT
from part3_cryptarithmetic import validate_cryptarithmetic, get_puzzle_hints

class CryptarithmeticUI:
    """Manages the cryptarithmetic puzzle user interface."""
    
    def __init__(self, parent_frame: tk.Frame, on_solution_callback: Callable[[bool], None]):
        """
        Initialize the cryptarithmetic UI.
        
        Args:
            parent_frame (tk.Frame): Parent frame to contain the UI
            on_solution_callback (Callable): Function to call when solution is verified
        """
        self.parent_frame = parent_frame
        self.on_solution_callback = on_solution_callback
        
        # Current puzzle state
        self.current_level_index = 0
        self.current_guess = {}
        self.guess_entries = {}
        
        # UI Components
        self.main_frame = None
        self.puzzle_display_frame = None
        self.input_frame = None
        self.feedback_label = None
        self.error_display = None
        self.solve_button = None
        self.hint_button = None
        self.hint_display = None
        
        self._create_ui()
    
    def _create_ui(self):
        """Create the cryptarithmetic UI components."""
        # Main container
        self.main_frame = tk.Frame(
            self.parent_frame,
            width=LAYOUT['crypto_panel_width'],
            bg=COLORS['crypto_bg'],
            bd=2,
            relief=tk.GROOVE,
            padx=LAYOUT['padding'],
            pady=LAYOUT['padding']
        )
        self.main_frame.pack(side=tk.LEFT, fill=tk.Y, padx=LAYOUT['padding'], pady=LAYOUT['padding'])
        self.main_frame.pack_propagate(False)  # Maintain fixed width
        
        # Title
        title_label = tk.Label(
            self.main_frame,
            text="🔢 Decipher the Rules",
            font=(LAYOUT['font_family'], LAYOUT['heading_font_size'], "bold"),
            bg=COLORS['crypto_bg'],
            fg=COLORS['text_dark']
        )
        title_label.pack(pady=(0, 10))
        
        # Puzzle display frame
        self.puzzle_display_frame = tk.Frame(self.main_frame, bg=COLORS['crypto_bg'])
        self.puzzle_display_frame.pack(pady=10)
        
        # Input frame
        self.input_frame = tk.Frame(self.main_frame, bg=COLORS['crypto_bg'])
        self.input_frame.pack(pady=10)
        
        # Feedback label
        self.feedback_label = tk.Label(
            self.main_frame,
            text="Enter your solution to decipher the river rules.",
            font=(LAYOUT['font_family'], LAYOUT['small_font_size']),
            bg=COLORS['crypto_bg'],
            fg='gray',
            wraplength=LAYOUT['crypto_panel_width'] - 20,
            justify=tk.LEFT
        )
        self.feedback_label.pack(pady=5)
        
        # Control buttons frame
        button_frame = tk.Frame(self.main_frame, bg=COLORS['crypto_bg'])
        button_frame.pack(pady=10, fill=tk.X)
        
        # Solve button
        self.solve_button = tk.Button(
            button_frame,
            text="Verify Solution",
            command=self._on_solve_clicked,
            font=(LAYOUT['font_family'], LAYOUT['body_font_size'], "bold"),
            bg=COLORS['success_green'],
            fg='white',
            relief=tk.RAISED,
            height=2
        )
        self.solve_button.pack(fill=tk.X, pady=(0, 5))
        
        # Hint button
        self.hint_button = tk.Button(
            button_frame,
            text="Get Hint",
            command=self._show_hints,
            font=(LAYOUT['font_family'], LAYOUT['small_font_size']),
            bg='#6b7280',
            fg='white',
            relief=tk.RAISED
        )
        self.hint_button.pack(fill=tk.X)
        
        # Error display
        self.error_display = tk.Text(
            self.main_frame,
            font=(LAYOUT['puzzle_font'], LAYOUT['small_font_size']),
            bd=2,
            relief=tk.SUNKEN,
            height=3,
            wrap=tk.WORD,
            state=tk.DISABLED,
            bg='#fff5f5',
            fg=COLORS['error_red']
        )
        self.error_display.pack(pady=5, fill=tk.X)
        
        # Hint display
        self.hint_display = tk.Text(
            self.main_frame,
            font=(LAYOUT['font_family'], LAYOUT['small_font_size']),
            bd=2,
            relief=tk.SUNKEN,
            height=4,
            wrap=tk.WORD,
            state=tk.DISABLED,
            bg='#f0f9ff',
            fg=COLORS['text_blue']
        )
        self.hint_display.pack(pady=5, fill=tk.X)
    
    def load_level(self, level_index: int):
        """
        Load a specific level and update the UI.
        
        Args:
            level_index (int): Index of the level to load
        """
        if not (0 <= level_index < len(LEVELS)):
            return
        
        self.current_level_index = level_index
        self.current_guess = {}
        
        self._render_puzzle_display()
        self._create_input_fields()
        self._clear_feedback()
        self._update_ui_state()
    
    def _render_puzzle_display(self):
        """Render the current level's puzzle in the display area."""
        # Clear existing display
        for widget in self.puzzle_display_frame.winfo_children():
            widget.destroy()
        
        level_data = LEVELS[self.current_level_index]
        
        # Level info
        level_info = tk.Label(
            self.puzzle_display_frame,
            text=f"Level {self.current_level_index + 1}: {level_data['name'].split(': ')[1]}",
            font=(LAYOUT['font_family'], LAYOUT['small_font_size'], "bold"),
            bg=COLORS['crypto_bg'],
            fg=COLORS['text_blue']
        )
        level_info.pack(pady=(0, 5))
        
        # Puzzle display
        puzzle_label = tk.Label(
            self.puzzle_display_frame,
            text=level_data['puzzle'],
            font=(LAYOUT['puzzle_font'], 14),
            justify=tk.CENTER,
            bg=COLORS['crypto_bg'],
            fg=COLORS['text_dark']
        )
        puzzle_label.pack()
        
        # Rules reminder
        rules_text = "Each letter = unique digit (0-9)\\nLeading letters ≠ 0"
        rules_label = tk.Label(
            self.puzzle_display_frame,
            text=rules_text,
            font=(LAYOUT['font_family'], 8),
            bg=COLORS['crypto_bg'],
            fg='gray',
            justify=tk.CENTER
        )
        rules_label.pack(pady=(5, 0))
    
    def _create_input_fields(self):
        """Create input fields for the current puzzle's letters."""
        # Clear existing input fields
        for widget in self.input_frame.winfo_children():
            widget.destroy()
        
        self.guess_entries = {}
        level_data = LEVELS[self.current_level_index]
        
        # Create a grid of input fields
        letters_per_row = 4
        current_row = 0
        current_col = 0
        
        for letter in level_data['unique_letters']:
            # Create frame for this letter's input
            letter_frame = tk.Frame(self.input_frame, bg=COLORS['crypto_bg'])
            letter_frame.grid(row=current_row, column=current_col, padx=3, pady=3)
            
            # Letter label
            tk.Label(
                letter_frame,
                text=letter,
                font=(LAYOUT['font_family'], LAYOUT['small_font_size'], "bold"),
                bg=COLORS['crypto_bg'],
                fg=COLORS['text_blue']
            ).pack()
            
            # Input field with validation
            var = tk.StringVar(self.main_frame)
            # Simple, direct callback for input changes
            def on_input_change(name, index, mode, letter=letter, var=var):
                content = var.get()
                
                # Limit to 1 character
                if len(content) > 1:
                    var.set(content[-1])  # Keep the last character typed
                    content = var.get()
                
                # Update the guess
                if content == "":
                    # Deletion case
                    self.current_guess.pop(letter, None)
                    self._update_ui_state()
                elif content.isdigit():
                    # Valid digit case
                    digit = int(content)
                    # Check for duplicates
                    duplicate_letter = self._find_duplicate_assignment(digit, letter)
                    if duplicate_letter:
                        self._show_feedback(f"Error: {digit} is already assigned to {duplicate_letter}.", 'error')
                        var.set("")
                        self.current_guess.pop(letter, None)
                    else:
                        self.current_guess[letter] = digit
                        self._update_ui_state()
                else:
                    # Invalid input case
                    var.set("")
                    self.current_guess.pop(letter, None)
                    self._update_ui_state()
            
            var.trace_add('write', on_input_change)
            
            entry = tk.Entry(
                letter_frame,
                textvariable=var,
                width=LAYOUT['entry_width'],
                font=(LAYOUT['font_family'], 12),
                justify=tk.CENTER,
                fg='black'
            )
            entry.pack()
            
            # Bind additional events
            entry.bind('<FocusIn>', lambda e, l=letter: self._on_entry_focus(l))
            entry.bind('<KeyPress>', lambda e, v=var: self._limit_input(e, v))
            
            self.guess_entries[letter] = var
            
            # Update grid position
            current_col += 1
            if current_col >= letters_per_row:
                current_col = 0
                current_row += 1
    
    def _limit_input(self, event, var):
        """Limit input to single digits."""
        if event.char.isdigit() and len(var.get()) >= 1:
            return "break"  # Prevent further input
        elif not event.char.isdigit() and event.char not in ['\\b', '\\x7f']:  # Allow backspace/delete
            return "break"  # Block non-digit characters
    
    def _find_duplicate_assignment(self, digit: int, exclude_letter: str) -> Optional[str]:
        """Find if a digit is already assigned to another letter."""
        for letter, assigned_digit in self.current_guess.items():
            if letter != exclude_letter and assigned_digit == digit:
                return letter
        return None
    
    def _on_entry_focus(self, letter: str):
        """Handle when an entry field receives focus."""
        self._clear_feedback()
    
    def _on_solve_clicked(self):
        """Handle solve button click."""
        level_data = LEVELS[self.current_level_index]
        
        # Validate solution
        is_valid, message = validate_cryptarithmetic(level_data, self.current_guess)
        
        if is_valid:
            self._show_feedback(message, 'success')
            self._clear_error_display()
            self.on_solution_callback(True)
        else:
            self._show_feedback("Solution Invalid. Check details below.", 'error')
            self._show_error_message(message)
            self.on_solution_callback(False)
        
        self._update_ui_state()
    
    def _show_hints(self):
        """Display hints for the current puzzle state."""
        level_data = LEVELS[self.current_level_index]
        hints = get_puzzle_hints(level_data, self.current_guess)
        
        hint_text = "\\n".join(f"• {hint}" for hint in hints)
        self._update_hint_display(hint_text)
    
    def _show_feedback(self, message: str, feedback_type: str):
        """
        Show feedback message to the user.
        
        Args:
            message (str): Message to display
            feedback_type (str): 'success', 'error', or 'info'
        """
        color_map = {
            'success': 'green',
            'error': COLORS['error_red'],
            'info': 'gray'
        }
        
        self.feedback_label.config(
            text=message,
            fg=color_map.get(feedback_type, 'gray')
        )
    
    def _clear_feedback(self):
        """Clear the feedback display."""
        self.feedback_label.config(
            text="Enter your solution to decipher the river rules.",
            fg='gray'
        )
    
    def _show_error_message(self, message: str):
        """Display detailed error message."""
        self.error_display.config(state=tk.NORMAL)
        self.error_display.delete(1.0, tk.END)
        self.error_display.insert(1.0, message)
        self.error_display.config(state=tk.DISABLED)
    
    def _clear_error_display(self):
        """Clear the error display."""
        self.error_display.config(state=tk.NORMAL)
        self.error_display.delete(1.0, tk.END)
        self.error_display.config(state=tk.DISABLED)
    
    def _update_hint_display(self, hints: str):
        """Update the hint display with new hints."""
        self.hint_display.config(state=tk.NORMAL)
        self.hint_display.delete(1.0, tk.END)
        self.hint_display.insert(1.0, hints)
        self.hint_display.config(state=tk.DISABLED)
    
    def _update_ui_state(self):
        """Update UI state based on current input."""
        level_data = LEVELS[self.current_level_index]
        required_letters = len(level_data['unique_letters'])
        assigned_letters = len([v for v in self.current_guess.values() if v is not None])
        
        # Update solve button state
        all_assigned = assigned_letters == required_letters
        self.solve_button.config(
            state=tk.NORMAL if all_assigned else tk.DISABLED,
            text="Verify Solution" if all_assigned else f"Need {required_letters - assigned_letters} more"
        )
        
        # Update feedback if all letters are assigned
        if all_assigned and not self.feedback_label.cget('text').startswith(('Solution', 'Error:')):
            self._show_feedback("All letters assigned. Click 'Verify Solution'!", 'info')
    
    def get_current_solution(self) -> Dict[str, int]:
        """Get the current user solution."""
        return self.current_guess.copy()
    
    def set_solution(self, solution: Dict[str, int]):
        """
        Set the solution programmatically (for testing/debugging).
        
        Args:
            solution (Dict[str, int]): Letter to digit mapping
        """
        self.current_guess = solution.copy()
        
        # Update UI to reflect the solution
        for letter, digit in solution.items():
            if letter in self.guess_entries:
                self.guess_entries[letter].set(str(digit))
        
        self._update_ui_state()
    
    def reset_puzzle(self):
        """Reset the current puzzle to initial state."""
        self.current_guess = {}
        for var in self.guess_entries.values():
            var.set("")
        self._clear_feedback()
        self._clear_error_display()
        self._update_hint_display("")
        self._update_ui_state()
    
    def is_solution_complete(self) -> bool:
        """Check if a complete solution has been entered."""
        level_data = LEVELS[self.current_level_index]
        required_letters = len(level_data['unique_letters'])
        assigned_letters = len([v for v in self.current_guess.values() if v is not None])
        return assigned_letters == required_letters
    
    def get_completion_percentage(self) -> float:
        """Get the percentage of completion for current puzzle."""
        level_data = LEVELS[self.current_level_index]
        required_letters = len(level_data['unique_letters'])
        assigned_letters = len([v for v in self.current_guess.values() if v is not None])
        return (assigned_letters / required_letters) * 100 if required_letters > 0 else 0
