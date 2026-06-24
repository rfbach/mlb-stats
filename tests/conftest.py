"""Pytest configuration and fixtures for dummy data."""
import pytest
from datetime import datetime
from typing import Dict, Any, List


# ============================================================================
# DUMMY DATA - GAME SCHEDULES
# ============================================================================

@pytest.fixture
def sample_game_scheduled() -> Dict[str, Any]:
    """Sample Cubs home game in scheduled status."""
    return {
        "game_id": 746505,
        "game_datetime": "2026-06-15T18:05:00Z",
        "game_date": "2026-06-15",
        "status": "Scheduled",
        "away_name": "Pittsburgh Pirates",
        "away_id": 25,
        "home_name": "Chicago Cubs",
        "home_id": 112,
        "away_score": 0,
        "home_score": 0,
        "venue_name": "Wrigley Field",
        "venue_id": 17,
    }


@pytest.fixture
def sample_game_live() -> Dict[str, Any]:
    """Sample Cubs home game in live status."""
    return {
        "game_id": 746506,
        "game_datetime": "2026-06-16T18:05:00Z",
        "game_date": "2026-06-16",
        "status": "In Progress",
        "away_name": "Cincinnati Reds",
        "away_id": 113,
        "home_name": "Chicago Cubs",
        "home_id": 112,
        "away_score": 2,
        "home_score": 3,
        "venue_name": "Wrigley Field",
        "venue_id": 17,
    }


@pytest.fixture
def sample_game_final() -> Dict[str, Any]:
    """Sample Cubs home game in final status."""
    return {
        "game_id": 746507,
        "game_datetime": "2026-06-17T18:05:00Z",
        "game_date": "2026-06-17",
        "status": "Final",
        "away_name": "St. Louis Cardinals",
        "away_id": 138,
        "home_name": "Chicago Cubs",
        "home_id": 112,
        "away_score": 4,
        "home_score": 5,
        "venue_name": "Wrigley Field",
        "venue_id": 17,
    }


@pytest.fixture
def sample_game_away() -> Dict[str, Any]:
    """Sample Cubs away game (should be filtered out)."""
    return {
        "game_id": 746508,
        "game_datetime": "2026-06-18T18:05:00Z",
        "game_date": "2026-06-18",
        "status": "Scheduled",
        "away_name": "Chicago Cubs",
        "away_id": 112,
        "home_name": "Milwaukee Brewers",
        "home_id": 158,
        "away_score": 0,
        "home_score": 0,
        "venue_name": "American Family Field",
        "venue_id": 32,
    }


@pytest.fixture
def multiple_games() -> List[Dict[str, Any]]:
    """Multiple Cubs games from statsapi.schedule()."""
    return [
        {
            "game_id": 746505,
            "game_datetime": "2026-06-15T18:05:00Z",
            "game_date": "2026-06-15",
            "status": "Scheduled",
            "away_name": "Pittsburgh Pirates",
            "away_id": 25,
            "home_name": "Chicago Cubs",
            "home_id": 112,
            "away_score": 0,
            "home_score": 0,
            "venue_name": "Wrigley Field",
            "venue_id": 17,
        },
        {
            "game_id": 746506,
            "game_datetime": "2026-06-16T18:05:00Z",
            "game_date": "2026-06-16",
            "status": "In Progress",
            "away_name": "Cincinnati Reds",
            "away_id": 113,
            "home_name": "Chicago Cubs",
            "home_id": 112,
            "away_score": 2,
            "home_score": 3,
            "venue_name": "Wrigley Field",
            "venue_id": 17,
        },
        {
            "game_id": 746507,
            "game_datetime": "2026-06-17T18:05:00Z",
            "game_date": "2026-06-17",
            "status": "Final",
            "away_name": "St. Louis Cardinals",
            "away_id": 138,
            "home_name": "Chicago Cubs",
            "home_id": 112,
            "away_score": 4,
            "home_score": 5,
            "venue_name": "Wrigley Field",
            "venue_id": 17,
        },
    ]


# ============================================================================
# DUMMY DATA - PLAY-BY-PLAY
# ============================================================================

@pytest.fixture
def sample_pbp_no_strikeouts() -> Dict[str, Any]:
    """Play-by-play data with no strikeouts."""
    return {
        "allPlays": [
            {
                "result": {"event": "Single"},
                "about": {"inning": 1, "isScoringPlay": True},
            },
            {
                "result": {"event": "Groundout"},
                "about": {"inning": 1, "isScoringPlay": False},
            },
            {
                "result": {"event": "Walk"},
                "about": {"inning": 1, "isScoringPlay": False},
            },
            {
                "result": {"event": "Single"},
                "about": {"inning": 1, "isScoringPlay": False},
            },
        ],
        "playsByInning": [
            {"top": [0, 1, 2], "bottom": [3]},
        ],
        "currentPlay": {
            "result": {"event": "Single"},
            "about": {"inning": 1},
        },
    }


@pytest.fixture
def sample_pbp_single_strikeout() -> Dict[str, Any]:
    """Play-by-play data with a single strikeout."""
    return {
        "allPlays": [
            {
                "result": {"event": "Strikeout"},
                "about": {"inning": 1, "isScoringPlay": False},
            },
            {
                "result": {"event": "Single"},
                "about": {"inning": 1, "isScoringPlay": False},
            },
            {
                "result": {"event": "Groundout"},
                "about": {"inning": 1, "isScoringPlay": False},
            },
        ],
        "playsByInning": [
            {"top": [0, 1, 2], "bottom": []},
        ],
        "currentPlay": {
            "result": {"event": "Single"},
            "about": {"inning": 1},
        },
    }


@pytest.fixture
def sample_pbp_three_strikeouts_inning_1() -> Dict[str, Any]:
    """Play-by-play data with 3 strikeouts in inning 1."""
    return {
        "allPlays": [
            {
                "result": {"event": "Strikeout"},
                "about": {"inning": 1, "isScoringPlay": False},
            },
            {
                "result": {"event": "Strikeout"},
                "about": {"inning": 1, "isScoringPlay": False},
            },
            {
                "result": {"event": "Strikeout"},
                "about": {"inning": 1, "isScoringPlay": False},
            },
            {
                "result": {"event": "Single"},
                "about": {"inning": 1, "isScoringPlay": False},
            },
        ],
        "playsByInning": [
            {"top": [0, 1, 2], "bottom": [3]},
        ],
        "currentPlay": {
            "result": {"event": "Single"},
            "about": {"inning": 1},
        },
    }


@pytest.fixture
def sample_pbp_three_strikeouts_inning_2() -> Dict[str, Any]:
    """Play-by-play data with 3 strikeouts in inning 2."""
    return {
        "allPlays": [
            {
                "result": {"event": "Single"},
                "about": {"inning": 1, "isScoringPlay": False},
            },
            {
                "result": {"event": "Single"},
                "about": {"inning": 1, "isScoringPlay": False},
            },
            {
                "result": {"event": "Single"},
                "about": {"inning": 1, "isScoringPlay": False},
            },
            {
                "result": {"event": "Strikeout"},
                "about": {"inning": 2, "isScoringPlay": False},
            },
            {
                "result": {"event": "Strikeout"},
                "about": {"inning": 2, "isScoringPlay": False},
            },
            {
                "result": {"event": "Strikeout"},
                "about": {"inning": 2, "isScoringPlay": False},
            },
        ],
        "playsByInning": [
            {"top": [0, 1, 2], "bottom": []},
            {"top": [3, 4, 5], "bottom": []},
        ],
        "currentPlay": {
            "result": {"event": "Strikeout"},
            "about": {"inning": 2},
        },
    }


@pytest.fixture
def sample_pbp_empty() -> Dict[str, Any]:
    """Empty play-by-play data."""
    return {
        "allPlays": [],
        "playsByInning": [],
        "currentPlay": {},
    }


@pytest.fixture
def sample_pbp_mixed_strikeouts() -> Dict[str, Any]:
    """Play-by-play data with varying strikeouts across innings."""
    return {
        "allPlays": [
            # Inning 1: 2 strikeouts
            {"result": {"event": "Strikeout"}, "about": {"inning": 1}},
            {"result": {"event": "Strikeout"}, "about": {"inning": 1}},
            {"result": {"event": "Single"}, "about": {"inning": 1}},
            # Inning 2: 1 strikeout
            {"result": {"event": "Strikeout"}, "about": {"inning": 2}},
            {"result": {"event": "Walk"}, "about": {"inning": 2}},
            {"result": {"event": "Double"}, "about": {"inning": 2}},
            # Inning 3: 4 strikeouts (exceeds threshold)
            {"result": {"event": "Strikeout"}, "about": {"inning": 3}},
            {"result": {"event": "Strikeout"}, "about": {"inning": 3}},
            {"result": {"event": "Strikeout"}, "about": {"inning": 3}},
            {"result": {"event": "Strikeout"}, "about": {"inning": 3}},
        ],
        "playsByInning": [
            {"top": [0, 1, 2], "bottom": []},
            {"top": [3, 4, 5], "bottom": []},
            {"top": [6, 7, 8, 9], "bottom": []},
        ],
        "currentPlay": {
            "result": {"event": "Strikeout"},
            "about": {"inning": 3},
        },
    }


@pytest.fixture
def sample_full_game_data() -> Dict[str, Any]:
    """Full game data structure as returned by statsapi.get('game')."""
    return {
        "gamePk": 746507,
        "gameType": "R",
        "season": 2026,
        "gameStatus": "Final",
        "liveData": {
            "plays": {
                "allPlays": [
                    {
                        "result": {"event": "Strikeout"},
                        "about": {"inning": 1, "isScoringPlay": False},
                    },
                    {
                        "result": {"event": "Single"},
                        "about": {"inning": 1, "isScoringPlay": True},
                    },
                    {
                        "result": {"event": "Strikeout"},
                        "about": {"inning": 1, "isScoringPlay": False},
                    },
                    {
                        "result": {"event": "Strikeout"},
                        "about": {"inning": 1, "isScoringPlay": False},
                    },
                ],
                "playsByInning": [
                    {"top": [0, 1, 2, 3], "bottom": []},
                ],
                "currentPlay": {
                    "result": {"event": "Strikeout"},
                    "about": {"inning": 1},
                },
            }
        },
    }
