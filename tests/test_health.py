import unittest
from datetime import date

from app.health import summarize_health_entries


class HealthSummaryTests(unittest.TestCase):
    def test_summarizes_only_logged_numeric_nutrition_and_progress(self):
        entries = [
            {
                "entry_type": "food",
                "logged_at": "2026-11-13T08:00:00",
                "data": {
                    "item": "oats",
                    "nutrition": {"calories": 230, "protein_g": 8, "carbs_g": 40, "fat_g": 4},
                },
            },
            {
                "entry_type": "food",
                "logged_at": "2026-11-13T13:00:00",
                "data": {"item": "dal", "nutrition": {"calories": 180, "protein_g": 10}},
            },
            {
                "entry_type": "workout",
                "logged_at": "2026-11-12T18:00:00",
                "data": {"exercise": "push day"},
            },
            {
                "entry_type": "weight",
                "logged_at": "2026-11-13T07:00:00",
                "data": {"kg": 72.2},
            },
            {
                "entry_type": "measurement",
                "logged_at": "2026-11-10T07:00:00",
                "data": {"waist_cm": 89},
            },
            {
                "entry_type": "food",
                "logged_at": "2026-10-01T08:00:00",
                "data": {"item": "old meal", "nutrition": {"calories": 900}},
            },
        ]
        summary = summarize_health_entries(entries, 30, today=date(2026, 11, 13))
        self.assertEqual(summary["totals"], {
            "calories": 410.0, "protein_g": 18.0, "carbs_g": 40.0, "fat_g": 4.0
        })
        self.assertEqual(summary["workout_sessions"], 1)
        self.assertEqual(summary["latest_weight"]["value"], 72.2)
        self.assertEqual(summary["measurements"][0]["waist_cm"], 89)
        self.assertEqual(len(summary["daily"]), 2)

    def test_missing_nutrition_is_not_invented_and_days_are_bounded(self):
        entries = [{
            "entry_type": "food",
            "logged_at": "2026-11-13T08:00:00",
            "data": {"item": "homemade meal"},
        }]
        summary = summarize_health_entries(entries, 999, today=date(2026, 11, 13))
        self.assertEqual(summary["period_days"], 365)
        self.assertEqual(summary["totals"]["calories"], 0)
        self.assertIn("AI estimate", summary["note"])


if __name__ == "__main__":
    unittest.main()
