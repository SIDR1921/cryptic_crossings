# Part 4: Missionaries & Cannibals Game Logic
# Contributor: Logic Developer
# Responsible for: M&C state machine, safety validation, game rules, win/loss conditions

"""
Missionaries and Cannibals game logic module for Cryptic Crossings.
Handles game state management, safety constraints, and win/loss conditions.
"""

from typing import Dict, List, Tuple, Optional
from enum import Enum
from dataclasses import dataclass, field

class Side(Enum):
    """Represents which side of the river."""
    LEFT = "left"
    RIGHT = "right"

class CharacterType(Enum):
    """Represents character types."""
    MISSIONARY = "M"
    CANNIBAL = "C"

@dataclass
class Character:
    """Represents a game character."""
    id: str
    type: CharacterType
    location: Side

@dataclass
class GameState:
    """Represents the complete game state."""
    missionaries_left: int = 0
    cannibals_left: int = 0
    missionaries_right: int = 0
    cannibals_right: int = 0
    boat_side: Side = Side.LEFT
    boat_crew: List[str] = field(default_factory=list)
    boat_capacity: int = 2
    total_missionaries: int = 0
    total_cannibals: int = 0
    move_count: int = 0
    is_game_over: bool = False
    is_won: bool = False

class MissionariesCannibalsGame:
    """Manages the Missionaries and Cannibals game logic."""
    
    def __init__(self):
        self.state = GameState()
        self.characters: List[Character] = []
        self.move_history: List[Dict] = []
    
    def initialize_game(self, missionaries: int, cannibals: int, boat_capacity: int):
        """
        Initialize a new game with specified parameters.
        
        Args:
            missionaries (int): Number of missionaries
            cannibals (int): Number of cannibals
            boat_capacity (int): Maximum boat capacity
        """
        self.state = GameState(
            missionaries_left=missionaries,
            cannibals_left=cannibals,
            missionaries_right=0,
            cannibals_right=0,
            boat_side=Side.LEFT,
            boat_crew=[],
            boat_capacity=boat_capacity,
            total_missionaries=missionaries,
            total_cannibals=cannibals,
            move_count=0,
            is_game_over=False,
            is_won=False
        )
        
        # Create character objects
        self.characters = []
        char_id = 1
        
        # Create missionaries
        for _ in range(missionaries):
            char = Character(f"M{char_id}", CharacterType.MISSIONARY, Side.LEFT)
            self.characters.append(char)
            char_id += 1
        
        # Create cannibals
        for _ in range(cannibals):
            char = Character(f"C{char_id}", CharacterType.CANNIBAL, Side.LEFT)
            self.characters.append(char)
            char_id += 1
        
        self.move_history = []
    
    def is_safe_state(self, m_left: int, c_left: int, m_right: int, c_right: int) -> bool:
        """
        Check if a state satisfies the safety constraint.
        
        The rule: Cannibals cannot outnumber missionaries on either side,
        unless there are no missionaries on that side.
        
        Args:
            m_left (int): Missionaries on left side
            c_left (int): Cannibals on left side
            m_right (int): Missionaries on right side
            c_right (int): Cannibals on right side
            
        Returns:
            bool: True if state is safe, False otherwise
        """
        # Left side safety check
        if m_left > 0 and c_left > m_left:
            return False
        
        # Right side safety check
        if m_right > 0 and c_right > m_right:
            return False
        
        return True
    
    def is_current_state_safe(self) -> bool:
        """Check if the current game state is safe."""
        return self.is_safe_state(
            self.state.missionaries_left,
            self.state.cannibals_left,
            self.state.missionaries_right,
            self.state.cannibals_right
        )
    
    def can_add_to_boat(self, character_id: str) -> Tuple[bool, str]:
        """
        Check if a character can be added to the boat.
        
        Args:
            character_id (str): ID of character to add
            
        Returns:
            Tuple[bool, str]: (can_add, error_message)
        """
        if self.state.is_game_over:
            return False, "Game is over"
        
        # Find character
        character = self.get_character(character_id)
        if not character:
            return False, f"Character {character_id} not found"
        
        # Check if character is on the same side as boat
        if character.location != self.state.boat_side:
            return False, f"Character is on {character.location.value} side, boat is on {self.state.boat_side.value} side"
        
        # Check boat capacity
        if len(self.state.boat_crew) >= self.state.boat_capacity:
            return False, f"Boat is full (capacity: {self.state.boat_capacity})"
        
        # Check if character is already on boat
        if character_id in self.state.boat_crew:
            return False, "Character is already on the boat"
        
        return True, "Can add to boat"
    
    def can_remove_from_boat(self, character_id: str) -> Tuple[bool, str]:
        """
        Check if a character can be removed from the boat.
        
        Args:
            character_id (str): ID of character to remove
            
        Returns:
            Tuple[bool, str]: (can_remove, error_message)
        """
        if self.state.is_game_over:
            return False, "Game is over"
        
        if character_id not in self.state.boat_crew:
            return False, "Character is not on the boat"
        
        return True, "Can remove from boat"
    
    def add_to_boat(self, character_id: str) -> Tuple[bool, str]:
        """
        Add a character to the boat.
        
        Args:
            character_id (str): ID of character to add
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        can_add, message = self.can_add_to_boat(character_id)
        if not can_add:
            return False, message
        
        character = self.get_character(character_id)
        
        # Add to boat crew
        self.state.boat_crew.append(character_id)
        
        # Update character location
        character.location = self.state.boat_side  # Still on current side but now on boat
        
        # Update side counts
        if self.state.boat_side == Side.LEFT:
            if character.type == CharacterType.MISSIONARY:
                self.state.missionaries_left -= 1
            else:
                self.state.cannibals_left -= 1
        else:
            if character.type == CharacterType.MISSIONARY:
                self.state.missionaries_right -= 1
            else:
                self.state.cannibals_right -= 1
        
        return True, f"Added {character_id} to boat"
    
    def remove_from_boat(self, character_id: str) -> Tuple[bool, str]:
        """
        Remove a character from the boat.
        
        Args:
            character_id (str): ID of character to remove
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        can_remove, message = self.can_remove_from_boat(character_id)
        if not can_remove:
            return False, message
        
        character = self.get_character(character_id)
        
        # Remove from boat crew
        self.state.boat_crew.remove(character_id)
        
        # Update character location
        character.location = self.state.boat_side
        
        # Update side counts
        if self.state.boat_side == Side.LEFT:
            if character.type == CharacterType.MISSIONARY:
                self.state.missionaries_left += 1
            else:
                self.state.cannibals_left += 1
        else:
            if character.type == CharacterType.MISSIONARY:
                self.state.missionaries_right += 1
            else:
                self.state.cannibals_right += 1
        
        return True, f"Removed {character_id} from boat"
    
    def can_travel(self) -> Tuple[bool, str]:
        """
        Check if the boat can travel to the other side.
        
        Returns:
            Tuple[bool, str]: (can_travel, error_message)
        """
        if self.state.is_game_over:
            return False, "Game is over"
        
        if len(self.state.boat_crew) == 0:
            return False, "Boat must have at least one passenger"
        
        if len(self.state.boat_crew) > self.state.boat_capacity:
            return False, f"Too many passengers (capacity: {self.state.boat_capacity})"
        
        return True, "Can travel"
    
    def travel(self) -> Tuple[bool, str]:
        """
        Move the boat to the other side of the river.
        
        Returns:
            Tuple[bool, str]: (success, message)
        """
        can_travel, message = self.can_travel()
        if not can_travel:
            return False, message
        
        # Record move in history
        move_data = {
            'move_number': self.state.move_count + 1,
            'from_side': self.state.boat_side.value,
            'passengers': self.state.boat_crew.copy(),
            'state_before': self._get_state_snapshot()
        }
        
        # Switch boat side
        new_side = Side.RIGHT if self.state.boat_side == Side.LEFT else Side.LEFT
        self.state.boat_side = new_side
        
        # Move all passengers to the new side
        for character_id in self.state.boat_crew:
            character = self.get_character(character_id)
            character.location = new_side
            
            # Update side counts
            if new_side == Side.LEFT:
                if character.type == CharacterType.MISSIONARY:
                    self.state.missionaries_left += 1
                else:
                    self.state.cannibals_left += 1
            else:
                if character.type == CharacterType.MISSIONARY:
                    self.state.missionaries_right += 1
                else:
                    self.state.cannibals_right += 1
        
        # Clear boat crew
        self.state.boat_crew = []
        
        # Increment move count
        self.state.move_count += 1
        
        # Complete move record
        move_data['to_side'] = new_side.value
        move_data['state_after'] = self._get_state_snapshot()
        self.move_history.append(move_data)
        
        # Check game status
        self._check_game_status()
        
        return True, f"Traveled to {new_side.value} side"
    
    def _check_game_status(self):
        """Check for win/loss conditions and update game state."""
        # Check for loss (unsafe state)
        if not self.is_current_state_safe():
            self.state.is_game_over = True
            self.state.is_won = False
            return
        
        # Check for win (all characters on right side)
        if (self.state.missionaries_left == 0 and 
            self.state.cannibals_left == 0 and 
            len(self.state.boat_crew) == 0):
            self.state.is_game_over = True
            self.state.is_won = True
            return
    
    def get_character(self, character_id: str) -> Optional[Character]:
        """Get a character by ID."""
        for char in self.characters:
            if char.id == character_id:
                return char
        return None
    
    def get_characters_on_side(self, side: Side) -> List[Character]:
        """Get all characters on a specific side (not including boat)."""
        return [char for char in self.characters if char.location == side and char.id not in self.state.boat_crew]
    
    def get_characters_on_boat(self) -> List[Character]:
        """Get all characters currently on the boat."""
        return [char for char in self.characters if char.id in self.state.boat_crew]
    
    def _get_state_snapshot(self) -> Dict:
        """Get a snapshot of the current state for history tracking."""
        return {
            'missionaries_left': self.state.missionaries_left,
            'cannibals_left': self.state.cannibals_left,
            'missionaries_right': self.state.missionaries_right,
            'cannibals_right': self.state.cannibals_right,
            'boat_side': self.state.boat_side.value,
            'boat_crew_count': len(self.state.boat_crew),
            'is_safe': self.is_current_state_safe()
        }
    
    def get_game_status(self) -> Dict:
        """Get comprehensive game status information."""
        return {
            'is_game_over': self.state.is_game_over,
            'is_won': self.state.is_won,
            'move_count': self.state.move_count,
            'current_state': self._get_state_snapshot(),
            'can_travel': self.can_travel()[0],
            'boat_crew_count': len(self.state.boat_crew),
            'boat_capacity': self.state.boat_capacity
        }
    
    def get_move_history(self) -> List[Dict]:
        """Get the complete move history."""
        return self.move_history.copy()
    
    def restart_game(self):
        """Restart the game with the same parameters."""
        self.initialize_game(
            self.state.total_missionaries,
            self.state.total_cannibals,
            self.state.boat_capacity
        )

# Global game instance
missionaries_cannibals_game = MissionariesCannibalsGame()

# Convenience functions for easy importing
def initialize_river_challenge(missionaries: int, cannibals: int, boat_capacity: int):
    """Initialize a new river crossing challenge."""
    missionaries_cannibals_game.initialize_game(missionaries, cannibals, boat_capacity)

def is_safe(m_left: int, c_left: int, m_right: int, c_right: int) -> bool:
    """Check if a state configuration is safe."""
    return missionaries_cannibals_game.is_safe_state(m_left, c_left, m_right, c_right)

def get_game_state() -> GameState:
    """Get the current game state."""
    return missionaries_cannibals_game.state

def get_characters() -> List[Character]:
    """Get all game characters."""
    return missionaries_cannibals_game.characters
