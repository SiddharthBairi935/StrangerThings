import tempfile
import unittest
from pathlib import Path

from app.database import get_history, init_db, save_message


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
