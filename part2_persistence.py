# Part 2: Persistence & Progress Management
# Contributor: Backend Developer
# Responsible for: Save/load functionality, progress tracking, session management

"""
Persistence and progress management module for Cryptic Crossings.
Handles saving and loading game progress, managing user sessions.
"""

import json
import os
from datetime import datetime
from part1_game_data import SAVE_FILE, get_max_level_index

class ProgressManager:
    """Manages game progress persistence and user session data."""
    
    def __init__(self, save_file=SAVE_FILE):
        self.save_file = save_file
        self.session_data = {
            'session_start': datetime.now().isoformat(),
            'levels_attempted': [],
            'total_playtime': 0,
            'cryptarithmetic_attempts': 0,
            'river_crossing_attempts': 0
        }
    
    def load_progress(self):
        """
        Load the highest level completed from the save file.
        
        Returns:
            int: Highest level completed (0-based index)
        """
        if not os.path.exists(self.save_file):
            return 0
            
        try:
            with open(self.save_file, 'r') as f:
                data = json.load(f)
                
            # Validate the loaded data
            highest_level = data.get('highest_level_completed', 0)
            max_level = get_max_level_index()
            
            # Ensure the level is within valid range
            if highest_level > max_level:
                highest_level = max_level
                
            return highest_level
            
        except (json.JSONDecodeError, FileNotFoundError, KeyError) as e:
            print(f"Error loading progress: {e}. Starting fresh.")
            return 0
    
    def save_progress(self, level_index):
        """
        Save the highest level completed to the save file.
        
        Args:
            level_index (int): The level index that was just completed
        """
        try:
            # Load existing data if available
            existing_data = {}
            if os.path.exists(self.save_file):
                try:
                    with open(self.save_file, 'r') as f:
                        existing_data = json.load(f)
                except json.JSONDecodeError:
                    pass  # Start fresh if file is corrupted
            
            # Update with new progress
            existing_data['highest_level_completed'] = level_index
            existing_data['last_played'] = datetime.now().isoformat()
            
            # Merge session data
            if 'session_history' not in existing_data:
                existing_data['session_history'] = []
            
            # Write updated data
            with open(self.save_file, 'w') as f:
                json.dump(existing_data, f, indent=2)
                
        except Exception as e:
            print(f"Error saving progress: {e}")
    
    def load_full_save_data(self):
        """
        Load complete save data including statistics and history.
        
        Returns:
            dict: Complete save data or empty dict if no save exists
        """
        if not os.path.exists(self.save_file):
            return {}
            
        try:
            with open(self.save_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def update_session_stats(self, stat_type, value=1):
        """
        Update session statistics.
        
        Args:
            stat_type (str): Type of statistic to update
            value (int): Value to add (default 1)
        """
        valid_stats = [
            'cryptarithmetic_attempts',
            'river_crossing_attempts',
            'total_playtime'
        ]
        
        if stat_type in valid_stats:
            self.session_data[stat_type] = self.session_data.get(stat_type, 0) + value
    
    def record_level_attempt(self, level_index, puzzle_type, success=False):
        """
        Record an attempt at a level.
        
        Args:
            level_index (int): Level that was attempted
            puzzle_type (str): 'cryptarithmetic' or 'river_crossing'
            success (bool): Whether the attempt was successful
        """
        attempt_data = {
            'level': level_index,
            'type': puzzle_type,
            'success': success,
            'timestamp': datetime.now().isoformat()
        }
        
        self.session_data['levels_attempted'].append(attempt_data)
        
        # Update attempt counters
        if puzzle_type == 'cryptarithmetic':
            self.update_session_stats('cryptarithmetic_attempts')
        elif puzzle_type == 'river_crossing':
            self.update_session_stats('river_crossing_attempts')
    
    def get_session_summary(self):
        """
        Get a summary of the current session.
        
        Returns:
            dict: Session summary data
        """
        return {
            'session_duration': self._calculate_session_duration(),
            'levels_attempted': len(set(attempt['level'] for attempt in self.session_data['levels_attempted'])),
            'total_attempts': len(self.session_data['levels_attempted']),
            'cryptarithmetic_attempts': self.session_data.get('cryptarithmetic_attempts', 0),
            'river_crossing_attempts': self.session_data.get('river_crossing_attempts', 0),
            'success_rate': self._calculate_success_rate()
        }
    
    def _calculate_session_duration(self):
        """Calculate session duration in minutes."""
        try:
            start_time = datetime.fromisoformat(self.session_data['session_start'])
            duration = datetime.now() - start_time
            return round(duration.total_seconds() / 60, 2)
        except:
            return 0
    
    def _calculate_success_rate(self):
        """Calculate success rate for the session."""
        if not self.session_data['levels_attempted']:
            return 0
            
        successful_attempts = sum(1 for attempt in self.session_data['levels_attempted'] if attempt['success'])
        total_attempts = len(self.session_data['levels_attempted'])
        
        return round((successful_attempts / total_attempts) * 100, 2)
    
    def reset_progress(self):
        """Reset all saved progress (for debugging or fresh start)."""
        try:
            if os.path.exists(self.save_file):
                os.remove(self.save_file)
            return True
        except Exception as e:
            print(f"Error resetting progress: {e}")
            return False
    
    def backup_save_data(self, backup_path=None):
        """
        Create a backup of the save data.
        
        Args:
            backup_path (str): Path for backup file. If None, uses timestamp.
        """
        if not os.path.exists(self.save_file):
            return False
            
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"cryptic_crossings_backup_{timestamp}.json"
        
        try:
            import shutil
            shutil.copy2(self.save_file, backup_path)
            return True
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False

# Global progress manager instance
progress_manager = ProgressManager()

# Convenience functions for easy importing
def load_progress():
    """Load game progress using the global progress manager."""
    return progress_manager.load_progress()

def save_progress(level_index):
    """Save game progress using the global progress manager."""
    return progress_manager.save_progress(level_index)

def record_attempt(level_index, puzzle_type, success=False):
    """Record a puzzle attempt."""
    return progress_manager.record_level_attempt(level_index, puzzle_type, success)

def get_session_summary():
    """Get current session summary."""
    return progress_manager.get_session_summary()
