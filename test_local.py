"""Local testing script for Cubs strikeout alert system."""
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Optional
from src.config import get_config
from src.game_monitor import (
    get_cubs_home_games_by_day,
    get_cubs_home_games_by_date_range
)
from src.play_by_play import (
    count_strikeouts_by_inning,
    has_three_strikeouts_in_any_inning
)


def test_game_monitor(single_game: bool = False, date_str: Optional[str] = None):
    """Test fetching Cubs games.
    
    Args:
        single_game: If True, only fetch a single game.
        date_str: Date in YYYY-MM-DD format. If None, uses today's date.
    """
    print("=" * 60)
    if single_game:
        print(f"Testing Game Monitor{f' for {date_str}' if date_str else ' (today)'}")
    else:
        print("Testing Game Monitor for whole season")
    print("=" * 60)
    
    if single_game:
        games = get_cubs_home_games_by_day(date_str)
    else:
        # Get games for range of March 26 this year to today
        start_date = f"{datetime.now().year}-03-26"
        end_date = datetime.now().strftime("%Y-%m-%d")
        games = get_cubs_home_games_by_date_range(start_date, end_date)
    print(f"Found {len(games)} Cubs home games\n")
    
    for game in games:
        game_id = game.get("game_id")
        if game_id is None:
            print(f"⚠️  Game ID not found")
            continue
        print(f"Game ID: {game_id}")
        print(f"Date: {game.get('game_date')}")
        print(f"Teams: {game.get('away_name')} @ {game.get('home_name')}")
        print(f"Status: {game.get('status')}")
        test_three_strikeouts_any_inning(game_id)
        print()
    
    return games


def test_play_by_play(game_id: int):
    """Test fetching play-by-play data."""
    print("=" * 60)
    print(f"Testing Play-by-Play for Game {game_id}")
    print("=" * 60)
    
    strikeouts = count_strikeouts_by_inning(game_id)
    print("Strikeouts by inning (Cubs pitching):")
    for inn, k_count in sorted(strikeouts.items()):
        print(f"  Inning {inn}: {k_count} strikeouts")
    print()


def test_three_strikeouts_any_inning(game_id: int):
    """Test if there are 3 strikeouts in any inning."""
    
    has_three_k = has_three_strikeouts_in_any_inning(game_id)
    if has_three_k:
        print("✅ There are 3 or more strikeouts in at least one inning.")
    else:
        print("❌ No inning has 3 or more strikeouts.")
    print()

def test_config():
    """Test configuration loading."""
    print("=" * 60)
    print("Configuration")
    print("=" * 60)
    
    config = get_config()
    for key, value in config.items():
        # Mask sensitive values
        if "email" in key.lower():
            value = f"{str(value)[:5]}***" if value else "Not configured"
        print(f"{key}: {value}")
    print()


def main():
    """Run all tests."""
    print("\n🔍 Cubs Strikeout Alert System - Local Test\n")
    
    # Get optional date argument
    date_str = None
    if len(sys.argv) > 1:
        date_str = sys.argv[1]
        print(f"Testing for date: {date_str}\n")
    
    # Test configuration
    test_config()
    
    # Test game monitor
    if date_str:
        games = test_game_monitor(single_game=True, date_str=date_str)
    else:
        games = test_game_monitor(single_game=False)
    
    # Test play-by-play for single game (live or finished)
    if date_str and games:
        for game in games:
            game_id = game.get("game_id")
            if game_id is not None:
                test_play_by_play(game_id)
                pass
        else:
            print("\nℹ️  No game ID found. Play-by-play test skipped.")
    
    print("=" * 60)
    print("Local testing completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
