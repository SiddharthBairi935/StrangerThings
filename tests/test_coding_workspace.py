import unittest

from fastapi import HTTPException

from app.coding_workspace import (
    _allowed_path,
    _contains_hardcoded_secret,
    _is_test_path,
    _parse_patch,
)


class LucasCodingWorkspaceValidationTests(unittest.TestCase):
    def test_allows_supported_language_files_inside_project_roots(self):
        allowed = (
            "app/brain.py",
            "tests/test_brain.py",
            "frontend/src/App.tsx",
            "frontend/src/styles.scss",
            "frontend/tests/App.test.tsx",
            "mobile/lib/main.dart",
            "mobile/test/widget_test.dart",
            "backend/src/main/java/App.java",
            "backend/src/main/kotlin/App.kt",
            "backend/src/main/go/main.go",
            "backend/src/api.php",
            "database/migrations/001_init.sql",
            "shared/contracts/types.ts",
            "docs/architecture.md",
            "README.md",
            "package.json",
            "pubspec.yaml",
            "pom.xml",
            "go.mod",
            "backend/go.mod",
            "backend/go.sum",
            "backend/Gemfile",
            "backend/Rakefile",
            "mobile/Package.swift",
            ".github/workflows/ci.yml",
            ".github/workflows/deploy.yaml",
            "Dockerfile",
            "docker-compose.yml",
            ".dockerignore",
            "infra/main.tf",
            "deploy/README.md",
        )
        for path in allowed:
            with self.subTest(path=path):
                self.assertTrue(_allowed_path(path))

    def test_rejects_unsafe_or_unapproved_paths(self):
        rejected = (
            "../.env",
            "app/../../secret.py",
            ".github/CODEOWNERS",
            ".github/dependabot.yml",
            ".github/workflows/scripts/deploy.yml",
            "app/secret.env",
            "app/secret.json.bak",
            "/tmp/evil.py",
            "frontend/../../../etc/passwd",
            "app/file?.py",
            "app/file#.py",
            "app/file%2fsecret.py",
            "app/file name.py",
            "unknown_area/source.py",
            "frontend\\\\windows.py",
        )
        for path in rejected:
            with self.subTest(path=path):
                self.assertFalse(_allowed_path(path))

    def test_recognizes_tests_across_supported_stacks(self):
        for path in (
            "tests/test_api.py",
            "frontend/src/Button.test.tsx",
            "frontend/src/Button.spec.ts",
            "mobile/test/widget_test.dart",
            "backend/src/test/java/ServiceTest.java",
            "backend/tests/api_test.go",
            "backend/handler_test.go",
            "backend/spec/models_spec.rb",
            "backend/src/test/java/ServiceTest.java",
        ):
            with self.subTest(path=path):
                self.assertTrue(_is_test_path(path))

    def test_accepts_patch_with_test_file(self):
        patch = _parse_patch(
            '{"title":"Add feature","summary":"Implements feature",'
            '"files":[{"path":"backend/src/handler.ts","content":"export const value = 1;\\n"},'
            '{"path":"backend/tests/handler.test.ts","content":"test(\\\"works\\\", () => {});\\n"}]}'
        )
        self.assertEqual(len(patch["files"]), 2)
        self.assertEqual(patch["title"], "Add feature")

    def test_rejects_patch_without_test_file(self):
        with self.assertRaises(HTTPException):
            _parse_patch(
                '{"files":[{"path":"frontend/src/App.tsx","content":"export default App"}]}'
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

    def test_rejects_hardcoded_secret_like_values(self):
        self.assertTrue(_contains_hardcoded_secret('API_KEY = "1234567890abcdef1234"'))
        self.assertTrue(_contains_hardcoded_secret("ghp_abcdefghijklmnopqrstuvwxyz123456"))
        self.assertTrue(_contains_hardcoded_secret("glpat-abcdefghijklmnopqrstuvwxyz123456"))
        self.assertTrue(_contains_hardcoded_secret("xoxb-123456789012345678901234"))
        self.assertTrue(_contains_hardcoded_secret("Authorization: Bearer abcdefghijklmnopqrstuvwxyz123456"))
        self.assertTrue(_contains_hardcoded_secret('password = "correct-horse-battery"'))
        self.assertTrue(_contains_hardcoded_secret('SECRET_KEY = "abcdefghijklmnop12345"'))
        self.assertTrue(_contains_hardcoded_secret('SUPABASE_SERVICE_ROLE_KEY = "abcdefghijklmnop12345"'))
        with self.assertRaises(HTTPException):
            _parse_patch(
                '{"files":[{"path":"backend/config.py","content":"API_KEY = \\\"1234567890abcdef1234\\\""},'
                '{"path":"tests/test_config.py","content":"pass"}]}'
            )

    def test_accepts_json_fenced_response(self):
        fence = chr(96) * 3
        patch = _parse_patch(
            fence + "json" + chr(10)
            + '{"files":[{"path":"tests/test_x.py","content":"pass"}]}'
            + chr(10) + fence
        )
        self.assertEqual(patch["files"][0]["path"], "tests/test_x.py")


if __name__ == "__main__":
    unittest.main()
