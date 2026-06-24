"""Unit tests for game_monitor module."""
import pytest
from unittest.mock import patch, MagicMock
from src.game_monitor import (
    get_cubs_home_games_by_day,
    get_cubs_home_games_by_date_range,
    get_game_status,
    get_game_by_id,
)
from src.config import CUBS_TEAM_ID


class TestGetCubsHomeGamesByDay:
    """Tests for get_cubs_home_games_by_day function."""

    @patch("src.game_monitor.statsapi.schedule")
    def test_returns_home_games_only(self, mock_schedule, sample_game_scheduled, sample_game_away):
        """Should return only Cubs home games, not away games."""
        mock_schedule.return_value = [sample_game_scheduled, sample_game_away]
        
        result = get_cubs_home_games_by_day("2026-06-15")
        
        assert len(result) == 1
        assert result[0]["game_id"] == 746505
        assert result[0]["home_id"] == CUBS_TEAM_ID

    @patch("src.game_monitor.statsapi.schedule")
    def test_with_explicit_date(self, mock_schedule, sample_game_scheduled):
        """Should fetch games for the specified date."""
        mock_schedule.return_value = [sample_game_scheduled]
        
        result = get_cubs_home_games_by_day("2026-06-15")
        
        mock_schedule.assert_called_once_with(
            start_date="2026-06-15",
            end_date="2026-06-15",
            team=str(CUBS_TEAM_ID)
        )
        assert len(result) == 1

    @patch("src.game_monitor.datetime")
    @patch("src.game_monitor.statsapi.schedule")
    def test_with_default_date(self, mock_schedule, mock_datetime, sample_game_scheduled):
        """Should use today's date if no date is provided."""
        mock_datetime.now.return_value.strftime.return_value = "2026-06-15"
        mock_schedule.return_value = [sample_game_scheduled]
        
        result = get_cubs_home_games_by_day(None)
        
        mock_datetime.now.assert_called_once()
        assert len(result) == 1

    @patch("src.game_monitor.statsapi.schedule")
    def test_empty_games_list(self, mock_schedule):
        """Should return empty list if no games found."""
        mock_schedule.return_value = []
        
        result = get_cubs_home_games_by_day("2026-06-15")
        
        assert result == []

    @patch("src.game_monitor.statsapi.schedule")
    def test_api_exception_handling(self, mock_schedule):
        """Should return empty list if API raises exception."""
        mock_schedule.side_effect = Exception("API Error")
        
        result = get_cubs_home_games_by_day("2026-06-15")
        
        assert result == []

    @patch("src.game_monitor.statsapi.schedule")
    def test_multiple_home_games(self, mock_schedule, multiple_games):
        """Should return all home games when multiple are scheduled."""
        mock_schedule.return_value = multiple_games
        
        result = get_cubs_home_games_by_day("2026-06-15")
        
        assert len(result) == 3
        assert all(g["home_id"] == CUBS_TEAM_ID for g in result)


class TestGetCubsHomeGamesByDateRange:
    """Tests for get_cubs_home_games_by_date_range function."""

    @patch("src.game_monitor.statsapi.schedule")
    def test_filters_home_games(self, mock_schedule, sample_game_scheduled, sample_game_away):
        """Should filter to home games only."""
        mock_schedule.return_value = [sample_game_scheduled, sample_game_away]
        
        result = get_cubs_home_games_by_date_range("2026-06-15", "2026-06-20")
        
        assert len(result) == 1
        assert result[0]["home_id"] == CUBS_TEAM_ID

    @patch("src.game_monitor.statsapi.schedule")
    def test_date_range_parameters(self, mock_schedule, multiple_games):
        """Should pass start and end dates to statsapi."""
        mock_schedule.return_value = multiple_games
        
        get_cubs_home_games_by_date_range("2026-06-15", "2026-06-30")
        
        mock_schedule.assert_called_once_with(
            start_date="2026-06-15",
            end_date="2026-06-30",
            team=str(CUBS_TEAM_ID)
        )

    @patch("src.game_monitor.statsapi.schedule")
    def test_api_exception_handling(self, mock_schedule):
        """Should return empty list on API error."""
        mock_schedule.side_effect = Exception("Connection Error")
        
        result = get_cubs_home_games_by_date_range("2026-06-15", "2026-06-30")
        
        assert result == []

    @patch("src.game_monitor.statsapi.schedule")
    def test_long_date_range(self, mock_schedule, multiple_games):
        """Should handle long date ranges (e.g., full season)."""
        mock_schedule.return_value = multiple_games
        
        result = get_cubs_home_games_by_date_range("2026-03-26", "2026-09-30")
        
        assert len(result) == 3


class TestGetGameStatus:
    """Tests for get_game_status function."""

    @patch("src.game_monitor.statsapi.meta")
    def test_maps_scheduled_status(self, mock_meta, sample_game_scheduled):
        """Should map detailed status to abstract game state."""
        mock_meta.return_value = [
            {
                "detailedState": "Scheduled",
                "abstractGameState": "Scheduled"
            },
            {
                "detailedState": "In Progress",
                "abstractGameState": "Live"
            },
        ]
        sample_game_scheduled["status"] = "Scheduled"
        
        result = get_game_status(sample_game_scheduled)
        
        assert result == "Scheduled"

    @patch("src.game_monitor.statsapi.meta")
    def test_maps_live_status(self, mock_meta, sample_game_live):
        """Should map 'In Progress' to 'Live'."""
        mock_meta.return_value = [
            {"detailedState": "In Progress", "abstractGameState": "Live"},
        ]
        sample_game_live["status"] = "In Progress"
        
        result = get_game_status(sample_game_live)
        
        assert result == "Live"

    @patch("src.game_monitor.statsapi.meta")
    def test_maps_final_status(self, mock_meta, sample_game_final):
        """Should map 'Final' status."""
        mock_meta.return_value = [
            {"detailedState": "Game Over", "abstractGameState": "Final"},
        ]
        sample_game_final["status"] = "Game Over"
        
        result = get_game_status(sample_game_final)
        
        assert result == "Final"

    @patch("src.game_monitor.statsapi.meta")
    def test_returns_original_status_if_no_match(self, mock_meta, sample_game_scheduled):
        """Should return original status if no mapping found."""
        mock_meta.return_value = []
        sample_game_scheduled["status"] = "Unknown Status"
        
        result = get_game_status(sample_game_scheduled)
        
        assert result == "Unknown Status"

    @patch("src.game_monitor.statsapi.meta")
    def test_returns_original_on_meta_api_error(self, mock_meta, sample_game_scheduled):
        """Should return original status if meta API fails."""
        mock_meta.side_effect = Exception("API Error")
        sample_game_scheduled["status"] = "Scheduled"
        
        result = get_game_status(sample_game_scheduled)
        
        assert result == "Scheduled"

    @patch("src.game_monitor.statsapi.meta")
    def test_handles_missing_status_field(self, mock_meta):
        """Should handle game dict without status field."""
        mock_meta.return_value = []
        game = {"game_id": 123}  # Missing status
        
        result = get_game_status(game)
        
        assert result == "Unknown"


class TestGetGameById:
    """Tests for get_game_by_id function."""

    @patch("src.game_monitor.statsapi.schedule")
    def test_returns_game_when_found(self, mock_schedule, sample_game_scheduled):
        """Should return game data when found by ID."""
        mock_schedule.return_value = [sample_game_scheduled]
        
        result = get_game_by_id(746505)
        
        assert result is not None
        assert result["game_id"] == 746505
        mock_schedule.assert_called_once_with(game_id=746505)

    @patch("src.game_monitor.statsapi.schedule")
    def test_returns_none_when_game_not_found(self, mock_schedule):
        """Should return None if game not found."""
        mock_schedule.return_value = []
        
        result = get_game_by_id(999999)
        
        assert result is None

    @patch("src.game_monitor.statsapi.schedule")
    def test_api_exception_returns_none(self, mock_schedule):
        """Should return None if API raises exception."""
        mock_schedule.side_effect = Exception("API Error")
        
        result = get_game_by_id(746505)
        
        assert result is None

    @patch("src.game_monitor.statsapi.schedule")
    def test_returns_first_game_from_list(self, mock_schedule, multiple_games):
        """Should return first game if multiple returned (edge case)."""
        mock_schedule.return_value = multiple_games
        
        result = get_game_by_id(746505)
        
        assert result["game_id"] == 746505


class TestGameFilterLogic:
    """Integration tests for game filtering logic."""

    @patch("src.game_monitor.statsapi.schedule")
    def test_filters_only_home_games(self, mock_schedule):
        """Should correctly identify home vs away games."""
        games = [
            {
                "game_id": 1,
                "away_id": CUBS_TEAM_ID,
                "home_id": 25,
                "status": "Scheduled"
            },
            {
                "game_id": 2,
                "away_id": 25,
                "home_id": CUBS_TEAM_ID,
                "status": "Scheduled"
            },
            {
                "game_id": 3,
                "away_id": CUBS_TEAM_ID,
                "home_id": 138,
                "status": "Scheduled"
            },
        ]
        mock_schedule.return_value = games
        
        result = get_cubs_home_games_by_day("2026-06-15")
        
        # Only game 2 should be included (Cubs at home)
        assert len(result) == 1
        assert result[0]["game_id"] == 2
