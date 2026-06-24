"""Play-by-play parsing module to detect strikeouts."""
from typing import Optional, Dict, Any
import statsapi
from .config import STRIKEOUTS_PER_INNING


def get_play_by_play(game_id: int) -> Optional[Dict[str, Any]]:
    """
    Get play-by-play data for a game.
    
    Args:
        game_id: MLB game ID
        
    Returns:
        Play data dict or None on error.
    """
    try:
        game_data = statsapi.get('game', {'gamePk': game_id})
        if not game_data:
            print(f"No game data found for game {game_id}")
            return None
        plays = game_data.get("liveData", {}).get("plays", {})
        return plays
    except Exception as e:
        print(f"Error fetching play-by-play for game {game_id}: {e}")
        return None


def count_strikeouts_by_inning(game_id: int) -> Dict[int, int]:
    """
    Count strikeouts by inning for Cubs pitcher.
    
    Args:
        game_id: MLB game ID
        
    Returns:
        Dictionary mapping inning number to strikeout count.
    """
    plays_data = get_play_by_play(game_id)
    if not plays_data:
        return {}
    
    all_plays = plays_data.get("allPlays", [])
    if not all_plays:
        return {}

    plays_by_inning = plays_data.get("playsByInning", [])
    if not plays_by_inning:
        return {}
    
    strikeouts_by_inning = {}
    
    for inning_idx, inning_plays in enumerate(plays_by_inning):
        inning_num = inning_idx + 1
        strikeouts_by_inning[inning_num] = 0
        
        # inning_plays['top'] is a list of plays for the top of the inning (Cubs pitching)
        if not isinstance(inning_plays['top'], list):
            continue
            
        for play_index in inning_plays['top']:
            result = all_plays[play_index].get("result", {}).get("event")
            
            # Check if this is a strikeout
            if result and result.lower() == "strikeout":
                strikeouts_by_inning[inning_num] += 1
    
    return strikeouts_by_inning


def has_three_strikeouts_in_any_inning(game_id: int) -> bool:
    """
    Check if there are 3 strikeouts by Cubs pitchers in any inning.
    
    Args:
        game_id: MLB game ID
        
    Returns:
        True if any inning has 3+ strikeouts, False otherwise.
    """
    strikeouts_by_inning = count_strikeouts_by_inning(game_id)
    return any(k >= STRIKEOUTS_PER_INNING for k in strikeouts_by_inning.values())
