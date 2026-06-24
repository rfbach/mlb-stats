"""AWS Lambda handler for Cubs strikeout alerts."""
import json
from typing import Any, Dict
import boto3
from .game_monitor import (
    get_cubs_home_games_by_day,
    get_game_status,
    get_game_by_id
)
from .play_by_play import (
    count_strikeouts_by_inning
)
from .alerts import send_strikeout_alert
from .state import (
    has_alerted_for_inning,
    record_alert,
    get_last_game_state,
    set_game_state,
)
from .config import STRIKEOUTS_PER_INNING, AWS_REGION, EVENTBRIDGE_RULE_NAME


def update_eventbridge_frequency(rule_name: str, frequency_expression: str) -> bool:
    """
    Update EventBridge rule frequency dynamically.
    
    Args:
        rule_name: Name of the EventBridge rule to update
        frequency_expression: New schedule expression (e.g., "rate(1 minute)")
        
    Returns:
        True if updated successfully, False otherwise.
    """
    try:
        events = boto3.client('events', region_name=AWS_REGION)
        
        # Get current rule targets so we can reapply them
        targets_response = events.list_targets_by_rule(Rule=rule_name)
        targets = targets_response.get('Targets', [])
        
        # Update the rule with new frequency
        events.put_rule(
            Name=rule_name,
            ScheduleExpression=frequency_expression,
            State='ENABLED'
        )
        
        # Reapply targets if there are any
        if targets:
            events.put_targets(Rule=rule_name, Targets=targets)
        
        print(f"✓ Updated {rule_name} to {frequency_expression}")
        return True
        
    except Exception as e:
        print(f"✗ Failed to update EventBridge rule: {e}")
        return False


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler for monitoring Cubs games and sending strikeout alerts.
    
    Args:
        event: Lambda event (CloudWatch Events or manual trigger)
        context: Lambda context
        
    Returns:
        Dictionary with statusCode and body for Lambda response.
    """
    try:
        print("Starting Cubs strikeout alert check...")
        
        # Get today's Cubs home games
        games = get_cubs_home_games_by_day()
        # games = get_cubs_home_games_by_day('2026-06-15')  # For testing with a specific date
        
        # Get previous game state to check for games spanning midnight
        last_state = get_last_game_state()
        previous_live_game_ids = []
        if last_state:
            game_state = last_state.get("game_state", {})
            previous_live_game_ids = game_state.get("live_game_ids", [])
        
        if not games and not previous_live_game_ids:
            print("No Cubs home games found today or from previous runs")
            return {
                "statusCode": 200,
                "body": json.dumps({"message": "No Cubs home games today"})
            }
        
        # Combine today's games with any live games from previous run (for cross-midnight tracking)
        all_games_to_check = list(games)
        game_ids_today = {g.get("game_id") for g in games if g.get("game_id")}
        
        for game_id in previous_live_game_ids:
            if game_id not in game_ids_today:
                # Try to check this game from the previous run
                # We'll attempt to get its status
                try:
                    # Create a minimal game object for checking
                    # The game_monitor should handle looking up the game by ID
                    print(f"Attempting to check previous game {game_id} that may span midnight")
                    # We'll check it in the processing loop below
                    previous_game = get_game_by_id(game_id)
                    if previous_game:
                        all_games_to_check.append(previous_game)
                except Exception as e:
                    print(f"Could not retrieve previous game {game_id}: {e}")
        
        # Determine current game states
        live_games = [g for g in all_games_to_check if get_game_status(g) == "Live"]
        final_games = [g for g in all_games_to_check if get_game_status(g) == "Final"]
        
        has_live_games = len(live_games) > 0
        all_final = len(final_games) == len(all_games_to_check)
        
        # Get last recorded state to detect changes
        last_state = get_last_game_state()
        last_state_data = last_state.get("game_state", {}) if last_state else {}
        had_live_games = last_state_data.get("has_live_games", False)
        
        # TRIGGER 1: Game(s) just went live - increase frequency to 1 minute
        if not had_live_games and has_live_games:
            print("GAME WENT LIVE! Increasing polling to 1-minute intervals")
            update_eventbridge_frequency(EVENTBRIDGE_RULE_NAME, "rate(1 minute)")
        
        # TRIGGER 2: All games are now final - decrease frequency to 60 minutes
        if had_live_games and all_final:
            print("ALL GAMES FINISHED! Decreasing polling to 60-minute intervals")
            update_eventbridge_frequency(EVENTBRIDGE_RULE_NAME, "rate(60 minutes)")
        
        alerts_sent = 0
        errors = []
        current_live_game_ids = []
        
        # Track which games were previously live to detect games that just went Final
        previous_live_game_ids = set(last_state_data.get("live_game_ids", []))
        
        for game in all_games_to_check:
            game_id = game.get("game_id")
            status = get_game_status(game)
            
            print(f"Checking game {game_id}: {status}")
            
            # Process both live games and games that just finished (were live -> now final)
            is_live = status == "Live"
            just_finished = status == "Final" and game_id in previous_live_game_ids
            
            if not (is_live or just_finished):
                print(f"Game {game_id} is not live or just finished (status: {status})")
                continue
            
            if just_finished:
                print(f"Game {game_id} just finished - processing final inning data")
            
            # Track this as a currently live game (don't track finished games)
            if is_live and game_id:
                current_live_game_ids.append(game_id)
            
            try:
                # Validate game_id exists
                if game_id is None:
                    print(f"Game ID is missing")
                    continue
                
                # Get strikeout counts for all innings (much more efficient than per-inning calls)
                strikeouts_by_inning = count_strikeouts_by_inning(game_id)
                
                # Check strikeouts by inning and send alerts if needed
                for inning, strikeout_count in strikeouts_by_inning.items():
                    
                    print(f"Strikeouts in inning {inning}: {strikeout_count}")
                    
                    # If 3 strikeouts and we haven't alerted yet, send alert
                    if strikeout_count >= STRIKEOUTS_PER_INNING:
                        if not has_alerted_for_inning(game_id, inning):
                            print(f"Sending alert for game {game_id}, inning {inning}")
                            
                            success = send_strikeout_alert(
                                game_id,
                                inning,
                                strikeout_count
                            )
                            
                            if success:
                                record_alert(game_id, inning)
                                alerts_sent += 1
                            else:
                                errors.append(f"Failed to send alert for game {game_id}, inning {inning}")
                        else:
                            print(f"Already alerted for game {game_id}, inning {inning}")
                
            except Exception as e:
                error_msg = f"Error processing game {game_id}: {str(e)}"
                print(error_msg)
                errors.append(error_msg)
        
        # Save current game state for next invocation, including live game IDs
        set_game_state(has_live_games, all_final, current_live_game_ids)
        
        # Prepare response
        response_body = {
            "message": "Cubs strikeout alert check completed",
            "games_checked": len(games),
            "alerts_sent": alerts_sent,
            "errors": errors,
            "game_state": {
                "has_live_games": has_live_games,
                "all_final": all_final,
            }
        }
        
        return {
            "statusCode": 200,
            "body": json.dumps(response_body)
        }
        
    except Exception as e:
        error_msg = f"Fatal error in Lambda handler: {str(e)}"
        print(error_msg)
        
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Error in Cubs strikeout alert check",
                "error": error_msg
            })
        }


def manual_test_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Manual test handler to test the alert system without waiting for live games.
    Usage: Invoke this handler to test email sending and state management.
    
    Args:
        event: Lambda event (can include game_id and inning override)
        context: Lambda context
        
    Returns:
        Dictionary with test results.
    """
    try:
        print("Starting manual test...")
        
        # Allow overrides from event
        game_id = event.get("game_id", 119009)  # Example game ID
        inning = event.get("inning", 3)
        strikeout_count = event.get("strikeout_count", 3)
        
        print(f"Testing alert for game {game_id}, inning {inning}, {strikeout_count} strikeouts")
        
        # Send test alert
        success = send_strikeout_alert(game_id, inning, strikeout_count)
        
        if success:
            # Record in state
            record_alert(game_id, inning)
            
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": "Test alert sent successfully",
                    "game_id": game_id,
                    "inning": inning
                })
            }
        else:
            return {
                "statusCode": 500,
                "body": json.dumps({
                    "message": "Failed to send test alert"
                })
            }
            
    except Exception as e:
        error_msg = f"Error in manual test: {str(e)}"
        print(error_msg)
        
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Error in manual test",
                "error": error_msg
            })
        }
