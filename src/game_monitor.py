"""Game monitoring module to fetch Cubs home games."""
from typing import Optional, Dict, Any
import statsapi
from datetime import datetime
from .config import CUBS_TEAM_ID


def get_cubs_home_games_by_day(date_str: Optional[str] = None) -> list[Dict[str, Any]]:
    """
    Get Cubs home games for a specific date (defaults to today).
    
    Args:
        date_str: Date in YYYY-MM-DD format. If None, uses today's date.
    
    Returns:
        List of game dictionaries, empty if no games.
    """
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    try:
        games = statsapi.schedule(
            start_date=date_str,
            end_date=date_str,
            team=str(CUBS_TEAM_ID)
        )
        
        # Filter for home games only (home_name is Cubs)
        home_games = [
            g for g in games 
            if g.get("away_id") != CUBS_TEAM_ID  # Cubs are home team if they're not away
        ]
        
        return home_games
    except Exception as e:
        print(f"Error fetching Cubs games: {e}")
        return []


def get_cubs_home_games_by_date_range(start_date: str, end_date: str) -> list[Dict[str, Any]]:
    """
    Get Cubs home games within a date range.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    
    Returns:
        List of game dictionaries, empty if no games.
    """
    try:
        games = statsapi.schedule(
            start_date=start_date,
            end_date=end_date,
            team=str(CUBS_TEAM_ID)
        )
        
        # Filter for home games only (Cubs are home team if away_id is not CUBS_TEAM_ID)
        home_games = [
            g for g in games 
            if g.get("away_id") != CUBS_TEAM_ID
        ]
        
        return home_games
    except Exception as e:
        print(f"Error fetching Cubs games for date range {start_date} to {end_date}: {e}")
        return []


def get_game_status(game: Dict[str, Any]) -> str:
    """
    Get the abstract game state by transforming the detailed status field.
    
    Args:
        game: Game dictionary from statsapi.schedule()
        
    Returns:
        Abstract game state string (e.g., "Pre-Game", "Live", "Final")
    """
    detailed_status = game.get("status", "Unknown")
    
    try:
        # Get the game status metadata from statsapi to map detailed status to abstract state
        game_status_meta = statsapi.meta('gameStatus')
        if not game_status_meta:
            return detailed_status  # Fallback if metadata is unavailable
        
        # Find the abstract state for this detailed status
        for state_info in game_status_meta:
            if state_info.get('detailedState') == detailed_status:
                return state_info.get('abstractGameState', detailed_status)
        
        # If no match found, return original status
        return detailed_status
    except Exception as e:
        print(f"Error transforming game status: {e}")
        return detailed_status

def get_game_by_id(game_id: int) -> Optional[Dict[str, Any]]:
    """
    Get game data by MLB game ID.
    
    Args:
        game_id: MLB game ID
        
    Returns:
        Game dictionary or None if not found.
    """
    try:
        game_data = statsapi.schedule(game_id=game_id)
        if not game_data:
            print(f"No game data found for game {game_id}")
            return None
        return game_data[0]
    except Exception as e:
        print(f"Error fetching game data for game {game_id}: {e}")
        return None