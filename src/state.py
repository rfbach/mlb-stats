"""State management module for tracking alert history using DynamoDB."""
import boto3
from botocore.exceptions import ClientError
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from .config import DYNAMODB_TABLE_NAME, AWS_REGION


def get_dynamodb_client():
    """Get DynamoDB client."""
    return boto3.client("dynamodb", region_name=AWS_REGION)


def create_alert_state_table() -> bool:
    """
    Create DynamoDB table for alert state (if it doesn't exist).
    
    Returns:
        True if table created or already exists, False on error.
    """
    dynamodb = get_dynamodb_client()
    
    try:
        table = dynamodb.create_table(
            TableName=DYNAMODB_TABLE_NAME,
            KeySchema=[
                {"AttributeName": "game_id", "KeyType": "HASH"},
                {"AttributeName": "inning", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "game_id", "AttributeType": "N"},
                {"AttributeName": "inning", "AttributeType": "N"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        
        # Wait for table to be created
        table.wait_until_exists()
        print(f"Table {DYNAMODB_TABLE_NAME} created successfully")
        return True
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"Table {DYNAMODB_TABLE_NAME} already exists")
            return True
        print(f"Error creating DynamoDB table: {e}")
        return False


def has_alerted_for_inning(game_id: int, inning: int) -> bool:
    """
    Check if we've already sent an alert for a game/inning combination.
    
    Args:
        game_id: MLB game ID
        inning: Inning number
        
    Returns:
        True if alert was already sent, False otherwise.
    """
    try:
        dynamodb = get_dynamodb_client()
        table = dynamodb.Table(DYNAMODB_TABLE_NAME)
        
        response = table.get_item(
            Key={
                "game_id": game_id,
                "inning": inning,
            }
        )
        
        return "Item" in response
        
    except Exception as e:
        print(f"Error checking alert state: {e}")
        return False


def record_alert(game_id: int, inning: int) -> bool:
    """
    Record that we've sent an alert for a game/inning combination.
    
    Args:
        game_id: MLB game ID
        inning: Inning number
        
    Returns:
        True if recorded successfully, False otherwise.
    """
    try:
        dynamodb = get_dynamodb_client()
        table = dynamodb.Table(DYNAMODB_TABLE_NAME)
        
        # Set TTL to 7 days from now to auto-delete old records
        ttl = int((datetime.now() + timedelta(days=7)).timestamp())
        
        table.put_item(
            Item={
                "game_id": game_id,
                "inning": inning,
                "alerted_at": datetime.now().isoformat(),
                "ttl": ttl,
            }
        )
        
        print(f"Recorded alert for game {game_id}, inning {inning}")
        return True
        
    except Exception as e:
        print(f"Error recording alert: {e}")
        return False


def clear_game_alerts(game_id: int) -> bool:
    """
    Clear all alert records for a specific game (useful when game ends).
    
    Args:
        game_id: MLB game ID
        
    Returns:
        True if cleared successfully, False otherwise.
    """
    try:
        dynamodb = get_dynamodb_client()
        table = dynamodb.Table(DYNAMODB_TABLE_NAME)
        
        # Query all items for this game
        response = table.query(
            KeyConditionExpression="game_id = :game_id",
            ExpressionAttributeValues={":game_id": game_id},
        )
        
        # Delete each item
        for item in response.get("Items", []):
            table.delete_item(
                Key={
                    "game_id": item["game_id"],
                    "inning": item["inning"],
                }
            )
        
        print(f"Cleared all alerts for game {game_id}")
        return True
        
    except Exception as e:
        print(f"Error clearing game alerts: {e}")
        return False


def get_last_game_state() -> Optional[Dict[str, Any]]:
    """
    Get the last recorded game state (has_live_games, all_final).
    
    Returns:
        Dictionary with game state or None if not found.
    """
    try:
        dynamodb = get_dynamodb_client()
        table = dynamodb.Table(DYNAMODB_TABLE_NAME)
        
        response = table.get_item(
            Key={
                "game_id": 0,  # Special key for metadata
                "inning": 0,   # Special inning for metadata
            }
        )
        
        if "Item" in response:
            return response["Item"].get("game_state")
        
        return None
        
    except Exception as e:
        print(f"Error getting last game state: {e}")
        return None


def set_game_state(has_live_games: bool, all_final: bool, live_game_ids: list) -> bool:
    """
    Record the current game state for state change detection.
    
    Args:
        has_live_games: Whether there are any live games
        all_final: Whether all games have finished
        live_game_ids: List of game IDs that are currently live (for cross-midnight tracking)
        
    Returns:
        True if recorded successfully, False otherwise.
    """
    try:
        dynamodb = get_dynamodb_client()
        table = dynamodb.Table(DYNAMODB_TABLE_NAME)
        
        if live_game_ids is None:
            live_game_ids = []
        
        table.put_item(
            Item={
                "game_id": 0,  # Special key for metadata
                "inning": 0,   # Special inning for metadata
                "game_state": {
                    "has_live_games": has_live_games,
                    "all_final": all_final,
                    "live_game_ids": live_game_ids,
                    "timestamp": datetime.now().isoformat(),
                },
                "alerted_at": datetime.now().isoformat(),
                "ttl": int((datetime.now() + timedelta(days=7)).timestamp()),
            }
        )
        
        print(f"Recorded game state: has_live_games={has_live_games}, all_final={all_final}, live_games={len(live_game_ids)}")
        return True
        
    except Exception as e:
        print(f"Error recording game state: {e}")
        return False
