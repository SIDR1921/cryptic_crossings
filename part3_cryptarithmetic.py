# Part 3: Cryptarithmetic Logic & Validation
# Contributor: Algorithm Developer
# Responsible for: Puzzle solving logic, validation rules, mathematical verification

"""
Cryptarithmetic puzzle logic and validation module for Cryptic Crossings.
Handles puzzle solving, input validation, and mathematical verification.
"""

from typing import Dict, List, Tuple, Optional, Any

class CryptarithmeticSolver:
    """Handles cryptarithmetic puzzle logic and validation."""
    
    def __init__(self):
        self.current_puzzle = None
        self.solution_cache = {}
    
    def set_puzzle(self, words: List[str], unique_letters: List[str]):
        """
        Set the current puzzle to work with.
        
        Args:
            words (List[str]): List of words in the puzzle [word1, word2, result]
            unique_letters (List[str]): List of unique letters in the puzzle
        """
        self.current_puzzle = {
            'words': words,
            'unique_letters': unique_letters
        }
        self.solution_cache = {}
    
    def validate_input(self, guess_map: Dict[str, int]) -> Tuple[bool, str]:
        """
        Validate user input against cryptarithmetic rules.
        
        Args:
            guess_map (Dict[str, int]): Mapping of letters to digits
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if not self.current_puzzle:
            return False, "No puzzle loaded"
        
        words = self.current_puzzle['words']
        letters = self.current_puzzle['unique_letters']
        
        # Rule 1: All letters must be assigned
        if len(guess_map) != len(letters):
            missing_letters = set(letters) - set(guess_map.keys())
            if missing_letters:
                return False, f"Missing assignments for: {', '.join(sorted(missing_letters))}"
            extra_letters = set(guess_map.keys()) - set(letters)
            if extra_letters:
                return False, f"Extra assignments for: {', '.join(sorted(extra_letters))}"
        
        # Rule 2: All digits must be unique
        assigned_digits = [d for d in guess_map.values() if d is not None]
        if len(set(assigned_digits)) != len(assigned_digits):
            duplicates = self._find_duplicate_assignments(guess_map)
            return False, f"Duplicate digit assignments: {duplicates}"
        
        # Rule 3: Leading letters cannot be zero
        for word in words:
            if word and guess_map.get(word[0]) == 0:
                return False, f"Leading letter '{word[0]}' cannot be zero"
        
        # Rule 4: Mathematical correctness
        try:
            is_correct, math_error = self._verify_mathematics(words, guess_map)
            if not is_correct:
                return False, math_error
        except ValueError as e:
            return False, f"Input error: {str(e)}"
        
        return True, "Solution is correct!"
    
    def _find_duplicate_assignments(self, guess_map: Dict[str, int]) -> str:
        """Find and report duplicate digit assignments."""
        digit_to_letters = {}
        for letter, digit in guess_map.items():
            if digit is not None:
                if digit not in digit_to_letters:
                    digit_to_letters[digit] = []
                digit_to_letters[digit].append(letter)
        
        duplicates = []
        for digit, letters in digit_to_letters.items():
            if len(letters) > 1:
                duplicates.append(f"{digit} → {', '.join(letters)}")
        
        return "; ".join(duplicates)
    
    def _verify_mathematics(self, words: List[str], guess_map: Dict[str, int]) -> Tuple[bool, str]:
        """
        Verify that the mathematical equation is correct.
        
        Args:
            words (List[str]): [word1, word2, result]
            guess_map (Dict[str, int]): Letter to digit mapping
            
        Returns:
            Tuple[bool, str]: (is_correct, error_message)
        """
        if len(words) != 3:
            return False, "Puzzle must have exactly 3 words (operand1, operand2, result)"
        
        try:
            num1 = self._word_to_number(words[0], guess_map)
            num2 = self._word_to_number(words[1], guess_map)
            result = self._word_to_number(words[2], guess_map)
            
            if num1 + num2 == result:
                return True, f"Correct: {num1} + {num2} = {result}"
            else:
                return False, f"Incorrect: {num1} + {num2} ≠ {result} (equals {num1 + num2})"
                
        except KeyError as e:
            return False, f"Missing digit assignment for letter: {e}"
        except ValueError as e:
            return False, f"Invalid number conversion: {e}"
    
    def _word_to_number(self, word: str, guess_map: Dict[str, int]) -> int:
        """
        Convert a word to its numeric value using the guess map.
        
        Args:
            word (str): Word to convert
            guess_map (Dict[str, int]): Letter to digit mapping
            
        Returns:
            int: Numeric value of the word
            
        Raises:
            KeyError: If a letter is not in the guess map
            ValueError: If conversion fails
        """
        if not word:
            raise ValueError("Empty word provided")
        
        number_str = ""
        for char in word:
            if char not in guess_map:
                raise KeyError(f"Letter '{char}' not found in guess map")
            if guess_map[char] is None:
                raise ValueError(f"Letter '{char}' has no assigned digit")
            number_str += str(guess_map[char])
        
        return int(number_str)
    
    def solve_puzzle(self, words: List[str], unique_letters: List[str]) -> Optional[Dict[str, int]]:
        """
        Automatically solve a cryptarithmetic puzzle using backtracking.
        
        Args:
            words (List[str]): List of words [word1, word2, result]
            unique_letters (List[str]): List of unique letters
            
        Returns:
            Optional[Dict[str, int]]: Solution mapping or None if no solution
        """
        # Check cache first
        puzzle_key = tuple(words + unique_letters)
        if puzzle_key in self.solution_cache:
            return self.solution_cache[puzzle_key]
        
        # Set up the puzzle
        self.set_puzzle(words, unique_letters)
        
        # Get leading letters (cannot be zero)
        leading_letters = set()
        for word in words:
            if word:
                leading_letters.add(word[0])
        
        # Use backtracking to find solution
        solution = self._backtrack_solve(
            assignment={},
            remaining_letters=unique_letters[:],
            used_digits=set(),
            leading_letters=leading_letters,
            words=words
        )
        
        # Cache the result
        self.solution_cache[puzzle_key] = solution
        return solution
    
    def _backtrack_solve(self, assignment: Dict[str, int], remaining_letters: List[str], 
                        used_digits: set, leading_letters: set, words: List[str]) -> Optional[Dict[str, int]]:
        """
        Recursive backtracking algorithm to solve cryptarithmetic puzzles.
        """
        # Base case: all letters assigned
        if not remaining_letters:
            is_valid, _ = self._verify_mathematics(words, assignment)
            return assignment if is_valid else None
        
        # Get next letter to assign
        letter = remaining_letters[0]
        remaining = remaining_letters[1:]
        
        # Try each possible digit
        for digit in range(10):
            # Skip if digit already used
            if digit in used_digits:
                continue
            
            # Skip if this is a leading letter and digit is 0
            if letter in leading_letters and digit == 0:
                continue
            
            # Make assignment and recurse
            assignment[letter] = digit
            used_digits.add(digit)
            
            result = self._backtrack_solve(assignment, remaining, used_digits, leading_letters, words)
            if result is not None:
                return result
            
            # Backtrack
            del assignment[letter]
            used_digits.remove(digit)
        
        return None
    
    def get_hints(self, guess_map: Dict[str, int]) -> List[str]:
        """
        Provide hints for the current puzzle state.
        
        Args:
            guess_map (Dict[str, int]): Current user assignments
            
        Returns:
            List[str]: List of helpful hints
        """
        if not self.current_puzzle:
            return ["No puzzle loaded"]
        
        hints = []
        words = self.current_puzzle['words']
        letters = self.current_puzzle['unique_letters']
        
        # Check for unassigned letters
        unassigned = [letter for letter in letters if letter not in guess_map or guess_map[letter] is None]
        if unassigned:
            hints.append(f"Still need to assign: {', '.join(unassigned)}")
        
        # Check for constraint violations
        for word in words:
            if word and word[0] in guess_map and guess_map[word[0]] == 0:
                hints.append(f"'{word[0]}' cannot be 0 (leading letter)")
        
        # Check for duplicates
        if len(guess_map) > 1:
            digit_counts = {}
            for letter, digit in guess_map.items():
                if digit is not None:
                    digit_counts[digit] = digit_counts.get(digit, 0) + 1
            
            duplicates = [digit for digit, count in digit_counts.items() if count > 1]
            if duplicates:
                hints.append(f"Duplicate digits found: {duplicates}")
        
        # Mathematical hints if all letters assigned
        if len(guess_map) == len(letters) and all(d is not None for d in guess_map.values()):
            try:
                num1 = self._word_to_number(words[0], guess_map)
                num2 = self._word_to_number(words[1], guess_map)
                actual_sum = num1 + num2
                expected = self._word_to_number(words[2], guess_map)
                
                if actual_sum != expected:
                    hints.append(f"Math check: {num1} + {num2} = {actual_sum}, but {words[2]} = {expected}")
            except (KeyError, ValueError):
                pass
        
        return hints if hints else ["Looking good so far!"]
    
    def is_puzzle_solvable(self, words: List[str], unique_letters: List[str]) -> bool:
        """
        Check if a puzzle has at least one valid solution.
        
        Args:
            words (List[str]): Puzzle words
            unique_letters (List[str]): Unique letters in puzzle
            
        Returns:
            bool: True if solvable, False otherwise
        """
        solution = self.solve_puzzle(words, unique_letters)
        return solution is not None

# Global solver instance
cryptarithmetic_solver = CryptarithmeticSolver()

# Convenience functions for easy importing
def validate_cryptarithmetic(level_data: Dict[str, Any], current_guess: Dict[str, int]) -> Tuple[bool, str]:
    """
    Validate a cryptarithmetic solution for a given level.
    
    Args:
        level_data (Dict): Level data containing words and unique_letters
        current_guess (Dict): User's letter-to-digit mapping
        
    Returns:
        Tuple[bool, str]: (is_valid, message)
    """
    words = level_data['words']
    unique_letters = level_data['unique_letters']
    
    cryptarithmetic_solver.set_puzzle(words, unique_letters)
    return cryptarithmetic_solver.validate_input(current_guess)

def get_puzzle_hints(level_data: Dict[str, Any], current_guess: Dict[str, int]) -> List[str]:
    """Get hints for the current puzzle state."""
    words = level_data['words']
    unique_letters = level_data['unique_letters']
    
    cryptarithmetic_solver.set_puzzle(words, unique_letters)
    return cryptarithmetic_solver.get_hints(current_guess)

def solve_puzzle_automatically(level_data: Dict[str, Any]) -> Optional[Dict[str, int]]:
    """Automatically solve a puzzle (for testing/debugging)."""
    words = level_data['words']
    unique_letters = level_data['unique_letters']
    
    return cryptarithmetic_solver.solve_puzzle(words, unique_letters)
