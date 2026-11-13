import unittest
from unittest.mock import AsyncMock, patch

from app.coding_workspace import (
    _generate_integrated_patch,
    _review_integrated_patch,
    _run_specialist_round,
)


class LucasSpecialistEngineTests(unittest.IsolatedAsyncioTestCase):
    async def test_runs_selected_domain_specialists(self):
        settings = type("SettingsStub", (), {"llm_model": "test-model"})()
        with patch(
            "app.coding_workspace._chat_completion",
            new_callable=AsyncMock,
        ) as completion:
            completion.side_effect = ["React architecture plan", "Flutter architecture plan"]
            results = await _run_specialist_round(
                object(), settings, ["frontend", "mobile"],
                "Build a cross-platform product app", "--- frontend/App.tsx ---",
            )
        self.assertEqual(set(results), {"frontend", "mobile"})
        self.assertEqual(results["frontend"], "React architecture plan")
        self.assertEqual(results["mobile"], "Flutter architecture plan")
        self.assertEqual(completion.await_count, 2)

    async def test_integrator_requires_multistack_patch_and_test_file(self):
        settings = type("SettingsStub", (), {"llm_model": "test-model"})()
        patch_json = (
            '{"title":"Build UI","summary":"Adds a tested web component",'
            '"files":[{"path":"frontend/src/App.tsx","content":"export default function App(){return null;}"},'
            '{"path":"frontend/src/App.test.tsx","content":"it(\\\"renders\\\",()=>{});"}]}'
        )
        with patch(
            "app.coding_workspace._chat_completion",
            new_callable=AsyncMock,
            return_value=patch_json,
        ) as completion:
            result = await _generate_integrated_patch(
                object(), settings, "Build a React app",
                "--- package.json ---",
                {"frontend": "Use existing React stack."},
                "Add a component render test.",
            )
        self.assertEqual(result["title"], "Build UI")
        self.assertEqual(len(result["files"]), 2)
        self.assertTrue(completion.await_args.kwargs["json_mode"])

    async def test_testing_specialist_reviews_exact_patch(self):
        settings = type("SettingsStub", (), {"llm_model": "test-model"})()
        patch_data = {
            "title": "Build API",
            "summary": "Adds endpoint",
            "files": [
                {"path": "backend/src/api.py", "content": "def api(): return 1"},
                {"path": "tests/test_api.py", "content": "def test_api(): assert True"},
            ],
        }
        with patch(
            "app.coding_workspace._chat_completion",
            new_callable=AsyncMock,
            return_value="PASS\nNo blocking issues found.",
        ) as completion:
            review = await _review_integrated_patch(
                object(), settings, "Build API", patch_data, "Test success and errors."
            )
        self.assertTrue(review.startswith("PASS"))
        review_messages = completion.await_args.args[2]
        self.assertIn("backend/src/api.py", review_messages[1]["content"])
        self.assertIn("Test success and errors.", review_messages[1]["content"])


if __name__ == "__main__":
    unittest.main()
