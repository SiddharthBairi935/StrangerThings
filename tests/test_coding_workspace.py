import unittest

from fastapi import HTTPException

from app.coding_workspace import _allowed_path, _parse_patch


class LucasCodingWorkspaceValidationTests(unittest.TestCase):
    def test_allows_only_project_source_and_tests(self):
        self.assertTrue(_allowed_path("app/brain.py"))
        self.assertTrue(_allowed_path("tests/test_brain.py"))
        self.assertTrue(_allowed_path("README.md"))
        self.assertFalse(_allowed_path("../.env"))
        self.assertFalse(_allowed_path("app/../../secret.py"))
        self.assertFalse(_allowed_path(".github/workflows/deploy.yml"))
        self.assertFalse(_allowed_path("app/secret.json"))
        self.assertFalse(_allowed_path("/tmp/evil.py"))

    def test_accepts_patch_with_test_file(self):
        patch = _parse_patch(
            '{"title":"Add feature","summary":"Implements feature",'
            '"files":[{"path":"app/feature.py","content":"VALUE = 1\\n"},'
            '{"path":"tests/test_feature.py","content":"import unittest\\n"}]}'
        )
        self.assertEqual(len(patch["files"]), 2)
        self.assertEqual(patch["title"], "Add feature")

    def test_rejects_patch_without_test_file(self):
        with self.assertRaises(HTTPException):
            _parse_patch(
                '{"files":[{"path":"app/feature.py","content":"VALUE = 1"}]}'
            )

    def test_rejects_path_traversal_and_duplicate_paths(self):
        with self.assertRaises(HTTPException):
            _parse_patch(
                '{"files":[{"path":"app/../evil.py","content":"x"},'
                '{"path":"tests/test_x.py","content":"y"}]}'
            )
        with self.assertRaises(HTTPException):
            _parse_patch(
                '{"files":[{"path":"app/a.py","content":"x"},'
                '{"path":"app/a.py","content":"y"},'
                '{"path":"tests/test_x.py","content":"z"}]}'
            )

    def test_accepts_json_fenced_response(self):
        fence = chr(96) * 3
        patch = _parse_patch(
            fence + "json" + chr(10) + '{"files":[{"path":"tests/test_x.py","content":"pass"}]}' + chr(10) + fence
        )
        self.assertEqual(patch["files"][0]["path"], "tests/test_x.py")


if __name__ == "__main__":
    unittest.main()
