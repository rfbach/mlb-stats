"""Unit tests for play_by_play module."""
import pytest
from unittest.mock import patch, MagicMock
from src.play_by_play import (
    get_play_by_play,
    count_strikeouts_by_inning,
    has_three_strikeouts_in_any_inning,
)
from src.config import STRIKEOUTS_PER_INNING


class TestGetPlayByPlay:
    """Tests for get_play_by_play function."""

    @patch("src.play_by_play.statsapi.get")
    def test_returns_plays_data(self, mock_get, sample_pbp_no_strikeouts):
        """Should return plays data when game data is found."""
        mock_get.return_value = {
            "liveData": {
                "plays": sample_pbp_no_strikeouts
            }
        }
        
        result = get_play_by_play(746507)
        
        assert result is not None
        assert "allPlays" in result
        assert "playsByInning" in result
        mock_get.assert_called_once_with("game", {"gamePk": 746507})

    @patch("src.play_by_play.statsapi.get")
    def test_returns_none_when_game_not_found(self, mock_get):
        """Should return None if game data not found."""
        mock_get.return_value = None
        
        result = get_play_by_play(999999)
        
        assert result is None

    @patch("src.play_by_play.statsapi.get")
    def test_returns_none_on_api_error(self, mock_get):
        """Should return None if API raises exception."""
        mock_get.side_effect = Exception("API Error")
        
        result = get_play_by_play(746507)
        
        assert result is None

    @patch("src.play_by_play.statsapi.get")
    def test_handles_missing_livedata(self, mock_get):
        """Should return empty dict if liveData is missing."""
        mock_get.return_value = {"gameStatus": "Final"}  # Missing liveData
        
        result = get_play_by_play(746507)
        
        assert result == {}

    @patch("src.play_by_play.statsapi.get")
    def test_handles_missing_plays(self, mock_get):
        """Should return empty dict if plays is missing from liveData."""
        mock_get.return_value = {"liveData": {}}  # Missing plays
        
        result = get_play_by_play(746507)
        
        assert result == {}


class TestCountStrikeoutsByInning:
    """Tests for count_strikeouts_by_inning function."""

    @patch("src.play_by_play.get_play_by_play")
    def test_no_strikeouts(self, mock_pbp, sample_pbp_no_strikeouts):
        """Should return zero strikeouts for each inning."""
        mock_pbp.return_value = sample_pbp_no_strikeouts
        
        result = count_strikeouts_by_inning(746507)
        
        assert result[1] == 0

    @patch("src.play_by_play.get_play_by_play")
    def test_single_strikeout(self, mock_pbp, sample_pbp_single_strikeout):
        """Should count single strikeout."""
        mock_pbp.return_value = sample_pbp_single_strikeout
        
        result = count_strikeouts_by_inning(746507)
        
        assert result[1] == 1

    @patch("src.play_by_play.get_play_by_play")
    def test_three_strikeouts_inning_1(self, mock_pbp, sample_pbp_three_strikeouts_inning_1):
        """Should count 3 strikeouts in inning 1."""
        mock_pbp.return_value = sample_pbp_three_strikeouts_inning_1
        
        result = count_strikeouts_by_inning(746507)
        
        assert result[1] == 3

    @patch("src.play_by_play.get_play_by_play")
    def test_three_strikeouts_inning_2(self, mock_pbp, sample_pbp_three_strikeouts_inning_2):
        """Should count 3 strikeouts in inning 2."""
        mock_pbp.return_value = sample_pbp_three_strikeouts_inning_2
        
        result = count_strikeouts_by_inning(746507)
        
        assert result[1] == 0
        assert result[2] == 3

    @patch("src.play_by_play.get_play_by_play")
    def test_mixed_strikeouts_multiple_innings(self, mock_pbp, sample_pbp_mixed_strikeouts):
        """Should count strikeouts correctly across multiple innings."""
        mock_pbp.return_value = sample_pbp_mixed_strikeouts
        
        result = count_strikeouts_by_inning(746507)
        
        assert result[1] == 2
        assert result[2] == 1
        assert result[3] == 4

    @patch("src.play_by_play.get_play_by_play")
    def test_empty_plays_data(self, mock_pbp, sample_pbp_empty):
        """Should return empty dict for empty plays data."""
        mock_pbp.return_value = sample_pbp_empty
        
        result = count_strikeouts_by_inning(746507)
        
        assert result == {}

    @patch("src.play_by_play.get_play_by_play")
    def test_plays_api_returns_none(self, mock_pbp):
        """Should return empty dict if plays API returns None."""
        mock_pbp.return_value = None
        
        result = count_strikeouts_by_inning(746507)
        
        assert result == {}

    @patch("src.play_by_play.get_play_by_play")
    def test_case_insensitive_strikeout_detection(self, mock_pbp):
        """Should detect strikeouts regardless of case."""
        pbp_data = {
            "allPlays": [
                {"result": {"event": "Strikeout"}, "about": {"inning": 1}},
                {"result": {"event": "STRIKEOUT"}, "about": {"inning": 1}},
                {"result": {"event": "strikeout"}, "about": {"inning": 1}},
            ],
            "playsByInning": [
                {"top": [0, 1, 2], "bottom": []},
            ],
        }
        mock_pbp.return_value = pbp_data
        
        result = count_strikeouts_by_inning(746507)
        
        # All three should be counted as strikeouts
        assert result[1] == 3

    @patch("src.play_by_play.get_play_by_play")
    def test_non_strikeout_results_ignored(self, mock_pbp):
        """Should ignore non-strikeout events."""
        pbp_data = {
            "allPlays": [
                {"result": {"event": "Strikeout"}, "about": {"inning": 1}},
                {"result": {"event": "Strike"}, "about": {"inning": 1}},  # Similar name, different
                {"result": {"event": "Strikeout Looking"}, "about": {"inning": 1}},
                {"result": {"event": "Groundout"}, "about": {"inning": 1}},
            ],
            "playsByInning": [
                {"top": [0, 1, 2, 3], "bottom": []},
            ],
        }
        mock_pbp.return_value = pbp_data
        
        result = count_strikeouts_by_inning(746507)
        
        # Only exact "Strikeout" matches should count (1 of them, not "Strikeout Looking")
        assert result[1] == 1

    @patch("src.play_by_play.get_play_by_play")
    def test_inning_mapping_correct(self, mock_pbp):
        """Should correctly map inning indices to inning numbers."""
        pbp_data = {
            "allPlays": [
                {"result": {"event": "Strikeout"}, "about": {"inning": 1}},  # Index 0 -> Inning 1
                {"result": {"event": "Strikeout"}, "about": {"inning": 2}},  # Index 1 -> Inning 2
            ],
            "playsByInning": [
                {"top": [0], "bottom": []},
                {"top": [1], "bottom": []},
            ],
        }
        mock_pbp.return_value = pbp_data
        
        result = count_strikeouts_by_inning(746507)
        
        assert result[1] == 1  # Inning 1 has 1 strikeout
        assert result[2] == 1  # Inning 2 has 1 strikeout


class TestHasThreeStrikeoutsInAnyInning:
    """Tests for has_three_strikeouts_in_any_inning function."""

    @patch("src.play_by_play.count_strikeouts_by_inning")
    def test_true_when_three_strikeouts_in_first_inning(self, mock_count):
        """Should return True if 3 strikeouts in first inning."""
        mock_count.return_value = {1: 3, 2: 0, 3: 0}
        
        result = has_three_strikeouts_in_any_inning(746507)
        
        assert result is True

    @patch("src.play_by_play.count_strikeouts_by_inning")
    def test_true_when_three_strikeouts_in_middle_inning(self, mock_count):
        """Should return True if 3 strikeouts in any inning."""
        mock_count.return_value = {1: 1, 2: 3, 3: 0}
        
        result = has_three_strikeouts_in_any_inning(746507)
        
        assert result is True

    @patch("src.play_by_play.count_strikeouts_by_inning")
    def test_true_when_more_than_three_strikeouts(self, mock_count):
        """Should return True if 3+ strikeouts in any inning."""
        mock_count.return_value = {1: 0, 2: 4, 3: 0}
        
        result = has_three_strikeouts_in_any_inning(746507)
        
        assert result is True

    @patch("src.play_by_play.count_strikeouts_by_inning")
    def test_false_when_less_than_three(self, mock_count):
        """Should return False if no inning has 3+ strikeouts."""
        mock_count.return_value = {1: 2, 2: 2, 3: 1}
        
        result = has_three_strikeouts_in_any_inning(746507)
        
        assert result is False

    @patch("src.play_by_play.count_strikeouts_by_inning")
    def test_false_when_no_strikeouts(self, mock_count):
        """Should return False if no strikeouts at all."""
        mock_count.return_value = {1: 0, 2: 0, 3: 0}
        
        result = has_three_strikeouts_in_any_inning(746507)
        
        assert result is False

    @patch("src.play_by_play.count_strikeouts_by_inning")
    def test_true_with_multiple_innings_exceeding_threshold(self, mock_count):
        """Should return True if multiple innings exceed threshold."""
        mock_count.return_value = {1: 3, 2: 3, 3: 2}
        
        result = has_three_strikeouts_in_any_inning(746507)
        
        assert result is True

    @patch("src.play_by_play.count_strikeouts_by_inning")
    def test_empty_strikeout_dict(self, mock_count):
        """Should return False if no strikeouts data."""
        mock_count.return_value = {}
        
        result = has_three_strikeouts_in_any_inning(746507)
        
        assert result is False


class TestPlayByPlayIntegration:
    """Integration tests for play-by-play functionality."""

    @patch("src.play_by_play.statsapi.get")
    def test_full_workflow_triggers_alert(self, mock_get, sample_pbp_three_strikeouts_inning_1):
        """Full workflow: fetch plays -> count -> detect alert."""
        mock_get.return_value = {
            "liveData": {
                "plays": sample_pbp_three_strikeouts_inning_1
            }
        }
        
        # Step 1: Get play-by-play
        plays = get_play_by_play(746507)
        assert plays is not None
        
        # Step 2: Count strikeouts
        counts = count_strikeouts_by_inning(746507)
        assert counts[1] == 3
        
        # Step 3: Check for alert
        should_alert = has_three_strikeouts_in_any_inning(746507)
        assert should_alert is True

    @patch("src.play_by_play.statsapi.get")
    def test_full_workflow_no_alert(self, mock_get, sample_pbp_no_strikeouts):
        """Full workflow should not trigger alert when threshold not met."""
        mock_get.return_value = {
            "liveData": {
                "plays": sample_pbp_no_strikeouts
            }
        }
        
        plays = get_play_by_play(746507)
        assert plays is not None
        
        counts = count_strikeouts_by_inning(746507)
        assert all(count < STRIKEOUTS_PER_INNING for count in counts.values())
        
        should_alert = has_three_strikeouts_in_any_inning(746507)
        assert should_alert is False

    @patch("src.play_by_play.statsapi.get")
    def test_game_with_multiple_inning_variations(self, mock_get, sample_pbp_mixed_strikeouts):
        """Should correctly handle game with varying strikeouts per inning."""
        mock_get.return_value = {
            "liveData": {
                "plays": sample_pbp_mixed_strikeouts
            }
        }
        
        plays = get_play_by_play(746507)
        counts = count_strikeouts_by_inning(746507)
        
        assert counts[1] == 2
        assert counts[2] == 1
        assert counts[3] == 4
        
        # Should alert because inning 3 has 4 strikeouts (>= 3)
        should_alert = has_three_strikeouts_in_any_inning(746507)
        assert should_alert is True
