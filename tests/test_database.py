import tempfile
import unittest
from pathlib import Path

from app.database import delete_health_entry, get_health_entries, get_history, init_db, save_health_entry, save_message


class DatabaseTests(unittest.TestCase):
    def test_messages_are_saved_and_returned_in_order(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            database_path = Path(directory) / "eleven.db"
            init_db(database_path)
            save_message(database_path, "conversation-1", "user", "Hello")
            save_message(database_path, "conversation-1", "assistant", "Hi")

            self.assertEqual(
                get_history(database_path, "conversation-1"),
                [
                    {"role": "user", "content": "Hello"},
                    {"role": "assistant", "content": "Hi"},
                ],
            )

    def test_health_entries_are_owner_scoped_and_structured(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            database_path = Path(directory) / "eleven.db"
            init_db(database_path)
            save_health_entry(
                database_path, "owner-a", "food",
                {"item": "oats", "grams": 60}, "2026-11-13T08:00:00"
            )
            save_health_entry(
                database_path, "owner-b", "weight",
                {"kg": 72.0}, "2026-11-13T08:05:00"
            )

            entries = get_health_entries(database_path, "owner-a")
            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0]["entry_type"], "food")
            self.assertEqual(entries[0]["data"], {"item": "oats", "grams": 60})
            self.assertEqual(entries[0]["logged_at"], "2026-11-13T08:00:00")
            self.assertEqual(
                [entry["entry_type"] for entry in get_health_entries(database_path, "owner-b")],
                ["weight"],
            )

    def test_health_entries_can_be_filtered_and_invalid_types_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            database_path = Path(directory) / "eleven.db"
            init_db(database_path)
            save_health_entry(database_path, "owner", "food", {"item": "rice"})
            save_health_entry(database_path, "owner", "workout", {"exercise": "squat"})
            self.assertEqual(
                [entry["entry_type"] for entry in get_health_entries(
                    database_path, "owner", entry_type="food"
                )],
                ["food"],
            )
            with self.assertRaises(ValueError):
                save_health_entry(database_path, "owner", "diagnosis", {"value": "x"})

    def test_health_log_delete_is_owner_scoped(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            database_path = Path(directory) / "eleven.db"
            init_db(database_path)
            entry_id = save_health_entry(database_path, "owner-a", "food", {"item": "banana"})
            self.assertFalse(delete_health_entry(database_path, "owner-b", entry_id))
            self.assertEqual(len(get_health_entries(database_path, "owner-a")), 1)
            self.assertTrue(delete_health_entry(database_path, "owner-a", entry_id))
            self.assertEqual(get_health_entries(database_path, "owner-a"), [])

    def test_conversations_are_isolated(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            database_path = Path(directory) / "eleven.db"
            init_db(database_path)
            save_message(database_path, "one", "user", "Private to one")
            save_message(database_path, "two", "user", "Private to two")

            self.assertEqual(
                get_history(database_path, "one"),
                [{"role": "user", "content": "Private to one"}],
            )


if __name__ == "__main__":
    unittest.main()
