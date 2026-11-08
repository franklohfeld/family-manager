"""
Gemeinsame Fixtures für alle Tests.
"""

import sys
from pathlib import Path

import pytest

# Projekt-Root zum Pfad hinzufügen
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture
def sample_config() -> dict:
    """Minimale Testkonfiguration."""
    return {
        "display": {"width": 1920, "height": 1080, "fullscreen": False, "image_area_ratio": 0.33},
        "images": {
            "directory": "/tmp/test_images",
            "state_file": "/tmp/test_image_state.json",
            "fallback_image": "assets/default_image.png",
            "supported_formats": [".jpg", ".jpeg", ".png"],
        },
        "calendar": {
            "refresh_interval_minutes": 15,
            "cache_file": "/tmp/test_calendar_cache.json",
            "credentials_file": "/tmp/test_credentials.json",
            "token_file": "/tmp/test_token.json",
            "lookahead_weeks": 4,
            "lookbehind_weeks": 1,
        },
        "holidays": {"state": "HE"},
        "persons": [
            {"key": "PERSON_A", "column": 1, "display_name": "TestA", "calendar_label": "Label A"},
            {"key": "PERSON_B", "column": 2, "display_name": "TestB", "calendar_label": "Label B"},
            {"key": "PERSON_C", "column": 3, "display_name": "TestC", "calendar_label": "Label C"},
            {"key": "PERSON_D", "column": 4, "display_name": "TestD", "calendar_label": "Label D"},
        ],
        "ui": {
            "font_size_date_overlay": 24,
            "font_size_table_header": 14,
            "font_size_table_cell": 12,
            "color_row_normal": "#FFFFFF",
            "color_row_light_red": "#FFCCCC",
            "color_row_dark_red": "#FF6666",
            "color_cell_vacation": "#FF9999",
        },
    }
