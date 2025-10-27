# Part 1: Core Game Data & Configuration
# Contributor: Data Architect / Game Designer
# Responsible for: Game levels, puzzle definitions, configuration constants

"""
Core game data and configuration module for Cryptic Crossings.
Contains all level definitions, puzzle data, and game constants.
"""

# Game configuration constants
SAVE_FILE = "cryptic_crossings_progress.json"
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700
CANVAS_WIDTH = 800
CANVAS_HEIGHT = 350
BANK_RATIO = 0.30  # 30% of canvas width for each bank

# Color scheme
COLORS = {
    'main_bg': '#f0f4f8',
    'crypto_bg': '#e0f7fa',
    'river_bg': '#ffffff',
    'river_water': '#3b82f6',
    'bank_color': '#d1d5db',
    'boat_color': '#993300',
    'boat_outline': '#7c2d12',
    'success_green': '#10b981',
    'error_red': '#ef4444',
    'warning_yellow': '#fffbe3',
    'text_dark': '#333333',
    'text_blue': '#1e40af',
    'text_gray': '#374151'
}

# Character icons
ICONS = {
    'missionary': '👩‍🎓',
    'cannibal': '👹'
}

# Level definitions with cryptarithmetic puzzles and corresponding M&C challenges
LEVELS = [
    {
        'name': 'Level 1: Classic Challenge',
        'puzzle': 'S E N D\n+ M O R E\n= M O N E Y',
        'words': ['SEND', 'MORE', 'MONEY'],
        'unique_letters': ['S', 'E', 'N', 'D', 'M', 'O', 'R', 'Y'],
        'solution': {'S': 9, 'E': 5, 'N': 6, 'D': 7, 'M': 1, 'O': 0, 'R': 8, 'Y': 2},
        'final_m': 3,  # 3 Missionaries
        'final_c': 3,  # 3 Cannibals
        'final_k': 2,  # Boat capacity of 2
        'description': 'The classic SEND+MORE=MONEY puzzle with traditional 3M+3C challenge'
    },
    {
        'name': 'Level 2: Double Trouble',
        'puzzle': 'T W O\n+ T W O\n= F O U R',
        'words': ['TWO', 'TWO', 'FOUR'],
        'unique_letters': ['T', 'W', 'O', 'F', 'U', 'R'],
        'solution': {'T': 7, 'W': 3, 'O': 4, 'F': 1, 'U': 6, 'R': 8},
        'final_m': 4,  # 4 Missionaries
        'final_c': 4,  # 4 Cannibals
        'final_k': 3,  # Boat capacity of 3
        'description': 'TWO+TWO=FOUR with increased difficulty: 4M+4C with larger boat'
    },
    {
        'name': 'Level 3: Master Challenge',
        'puzzle': 'T H I S\n+ I S\n= G O O D',
        'words': ['THIS', 'IS', 'GOOD'],
        'unique_letters': ['T', 'H', 'I', 'S', 'G', 'O', 'D'],
        'solution': {'T': 1, 'H': 9, 'I': 5, 'S': 3, 'G': 2, 'O': 0, 'D': 6},
        'final_m': 5,  # 5 Missionaries
        'final_c': 5,  # 5 Cannibals
        'final_k': 3,  # Boat capacity of 3
        'description': 'THIS+IS=GOOD with maximum difficulty: 5M+5C challenge'
    }
]

# Game rules and help text
GAME_RULES = {
    'cryptarithmetic': [
        "Each letter represents a unique digit (0-9)",
        "Leading letters cannot be zero",
        "All letters must be assigned different digits",
        "The equation must be mathematically correct"
    ],
    'missionaries_cannibals': [
        "Transport all missionaries and cannibals to the right bank",
        "Cannibals cannot outnumber missionaries on either side",
        "Exception: No missionaries present means any number of cannibals is safe",
        "The boat must have at least one passenger to cross",
        "Boat capacity limits how many can travel together"
    ]
}

# UI Layout constants
LAYOUT = {
    'window_width': 1200,
    'window_height': 700,
    'canvas_width': 800,
    'canvas_height': 350,
    'crypto_panel_width': 300,
    'river_panel_expand': True,
    'padding': 10,
    'button_height': 40,
    'entry_width': 3,
    'font_family': 'Inter',
    'puzzle_font': 'Courier',
    'icon_font_size': 24,
    'title_font_size': 18,
    'heading_font_size': 16,
    'body_font_size': 12,
    'small_font_size': 10
}

# Character positioning
POSITIONING = {
    'bank_ratio': 0.30,  # 30% of canvas width for each bank
    'characters_per_row_left': 4,
    'characters_per_row_right': 5,
    'character_spacing_x': 40,
    'character_spacing_y': 50,
    'character_start_x': 10,
    'character_start_y': 50,
    'boat_width': 80,
    'boat_height': 40,
    'boat_y_position': 300,
    'boat_padding': 10
}

def get_level_count():
    """Return the total number of levels available."""
    return len(LEVELS)

def get_level_data(level_index):
    """
    Get level data for a specific level index.
    
    Args:
        level_index (int): Zero-based level index
        
    Returns:
        dict: Level data or None if index is invalid
    """
    if 0 <= level_index < len(LEVELS):
        return LEVELS[level_index]
    return None

def validate_level_index(level_index):
    """
    Validate if a level index is within valid range.
    
    Args:
        level_index (int): Level index to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    return 0 <= level_index < len(LEVELS)

def get_max_level_index():
    """Return the maximum valid level index."""
    return len(LEVELS) - 1
