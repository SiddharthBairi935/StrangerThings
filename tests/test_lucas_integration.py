import base64
import unittest
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException
from fastapi.testclient import TestClient

from app import main
from app.coding_workspace import GitHubWorkspace, execute_lucas_coding_task


class LucasCodingEndpointTests(unittest.TestCase):
    def setUp(self):
        self.token_patch = patch.object(main.settings, "api_access_token", "owner-test-token")
        self.llm_key_patch = patch.object(main.settings, "llm_api_key", "llm-test-key")
        self.llm_model_patch = patch.object(main.settings, "llm_model", "test-model")
        self.token_patch.start()
        self.llm_key_patch.start()
        self.llm_model_patch.start()
        self.client = TestClient(main.app)

    def tearDown(self):
        self.token_patch.stop()
        self.llm_key_patch.stop()
        self.llm_model_patch.stop()

    def test_owner_authentication_is_required(self):
        response = self.client.post("/api/lucas/code", json={"task": "Build a React page"})
        self.assertEqual(response.status_code, 401)

        response = self.client.post(
            "/api/lucas/code",
            json={"task": "Build a React page"},
            headers={"Authorization": "Bearer wrong-token"},
        )
        self.assertEqual(response.status_code, 401)

    def test_missing_owner_token_configuration_fails_closed(self):
        with patch.object(main.settings, "api_access_token", None):
            response = self.client.post(
                "/api/lucas/code",
                json={"task": "Build a React page"},
            )
        self.assertEqual(response.status_code, 503)

    def test_request_validation_rejects_empty_or_oversized_task(self):
        headers = {"Authorization": "Bearer owner-test-token"}
        self.assertEqual(
            self.client.post("/api/lucas/code", json={"task": ""}, headers=headers).status_code,
            422,
        )
        self.assertEqual(
            self.client.post("/api/lucas/code", json={"task": "x" * 12001}, headers=headers).status_code,
            422,
        )

    def test_missing_ai_configuration_fails_before_coding(self):
        with patch.object(main.settings, "llm_api_key", None):
            response = self.client.post(
                "/api/lucas/code",
                json={"task": "Build a React page"},
                headers={"Authorization": "Bearer owner-test-token"},
            )
        self.assertEqual(response.status_code, 503)

    def test_authenticated_request_invokes_coding_workflow(self):
        expected = {
            "status": "pull_request_opened",
            "execution_started": True,
            "tests_executed_by_app": False,
            "ci_status": "pending",
            "pull_request_url": "https://github.com/example/repo/pull/7",
        }
        with patch("app.main.execute_lucas_coding_task", new=AsyncMock(return_value=expected)) as execute:
            response = self.client.post(
                "/api/lucas/code",
                json={"task": "Build a React page"},
                headers={"Authorization": "Bearer owner-test-token"},
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected)
        execute.assert_awaited_once_with(main.settings, "Build a React page")


class LucasCodingWorkflowIntegrationTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.settings = type(
            "SettingsStub",
            (),
            {
                "github_token": "github-test-token",
                "github_repository": "owner/repo",
                "github_base_branch": "main",
                "llm_api_key": "llm-test-key",
                "llm_model": "test-model",
                "llm_base_url": "https://llm.example",
                "llm_timeout_seconds": 5.0,
            },
        )()
        self.patch_data = {
            "title": "Add tested React feature",
            "summary": "Adds a small tested feature.",
            "files": [
                {"path": "frontend/src/App.tsx", "content": "export default function App(){return null;}"},
                {"path": "frontend/src/App.test.tsx", "content": "it('renders', () => {});"},
            ],
        }

    def _workspace_stub(self):
        workspace = type("WorkspaceStub", (), {})()
        workspace.load_context = AsyncMock(
            return_value=("main", "base-sha", {"frontend/src/App.tsx": "export default function App(){return null;}"})
        )
        workspace.publish_pull_request = AsyncMock(
            return_value={
                "branch": "lucas/task-test",
                "pull_request_url": "https://github.com/owner/repo/pull/7",
                "pull_request_number": 7,
                "commit_sha": "commit-sha",
            }
        )
        workspace.close = AsyncMock()
        return workspace

    async def test_full_workflow_creates_pr_after_specialist_and_qa_pass(self):
        workspace = self._workspace_stub()
        with (
            patch("app.coding_workspace.GitHubWorkspace", return_value=workspace),
            patch("app.delegation.create_lucas_plan", return_value={"specialists": ["frontend", "testing"]}),
            patch("app.coding_workspace._run_specialist_round", new=AsyncMock(return_value={"frontend": "React plan"})) as specialists,
            patch("app.coding_workspace._chat_completion", new=AsyncMock(return_value="Test strategy")) as completion,
            patch("app.coding_workspace._generate_integrated_patch", new=AsyncMock(return_value=self.patch_data)),
            patch("app.coding_workspace._review_integrated_patch", new=AsyncMock(return_value="PASS\\nNo blockers.")) as review,
        ):
            result = await execute_lucas_coding_task(self.settings, "Build a React feature")
        self.assertEqual(result["status"], "pull_request_opened")
        self.assertEqual(result["ci_status"], "pending")
        self.assertEqual(result["specialists_consulted"], ["frontend", "testing"])
        self.assertFalse(result["repair_attempted"])
        specialists.assert_awaited_once()
        completion.assert_awaited_once()
        review.assert_awaited_once()
        workspace.publish_pull_request.assert_awaited_once()
        workspace.close.assert_awaited_once()

    async def test_qa_blocker_gets_one_repair_attempt_before_publish(self):
        workspace = self._workspace_stub()
        with (
            patch("app.coding_workspace.GitHubWorkspace", return_value=workspace),
            patch("app.delegation.create_lucas_plan", return_value={"specialists": ["frontend", "testing"]}),
            patch("app.coding_workspace._run_specialist_round", new=AsyncMock(return_value={"frontend": "React plan"})),
            patch("app.coding_workspace._chat_completion", new=AsyncMock(return_value="Test strategy")),
            patch("app.coding_workspace._generate_integrated_patch", new=AsyncMock(return_value=self.patch_data)) as generate,
            patch(
                "app.coding_workspace._review_integrated_patch",
                new=AsyncMock(side_effect=["NEEDS_CHANGES\\nAdd error-state coverage.", "PASS\\nFixed."]),
            ) as review,
        ):
            result = await execute_lucas_coding_task(self.settings, "Build a React feature")
        self.assertTrue(result["repair_attempted"])
        self.assertEqual(generate.await_count, 2)
        self.assertEqual(review.await_count, 2)
        workspace.publish_pull_request.assert_awaited_once()

    async def test_unresolved_qa_blockers_never_publish_a_pr(self):
        workspace = self._workspace_stub()
        with (
            patch("app.coding_workspace.GitHubWorkspace", return_value=workspace),
            patch("app.delegation.create_lucas_plan", return_value={"specialists": ["frontend", "testing"]}),
            patch("app.coding_workspace._run_specialist_round", new=AsyncMock(return_value={"frontend": "React plan"})),
            patch("app.coding_workspace._chat_completion", new=AsyncMock(return_value="Test strategy")),
            patch("app.coding_workspace._generate_integrated_patch", new=AsyncMock(return_value=self.patch_data)),
            patch(
                "app.coding_workspace._review_integrated_patch",
                new=AsyncMock(side_effect=[
                    "NEEDS_CHANGES\\nCritical authorization flaw.",
                    "BLOCKED\\nThe QA response was malformed and did not explicitly approve.",
                ]),
            ),
            self.assertRaises(HTTPException) as raised,
        ):
            await execute_lucas_coding_task(self.settings, "Build a React feature")
        self.assertEqual(raised.exception.status_code, 422)
        workspace.publish_pull_request.assert_not_awaited()
        workspace.close.assert_awaited_once()

    async def test_coding_task_with_hardcoded_credential_is_rejected_before_github_access(self):
        with patch("app.coding_workspace.GitHubWorkspace") as workspace_factory, self.assertRaises(HTTPException) as raised:
                await execute_lucas_coding_task(
                    self.settings,
                    'Please use API_KEY = "abcdefghijklmnop12345"',
                )
        self.assertEqual(raised.exception.status_code, 422)
        workspace_factory.assert_not_called()

    async def test_context_loader_skips_source_files_containing_credentials(self):
        workspace = GitHubWorkspace("token", "owner/repo")
        safe_source = "def add(left, right):\\n    return left + right\\n"
        secret_source = 'API_KEY = "abcdefghijklmnop12345"\\n'

        async def fake_request(method, path, **kwargs):
            if path == "/repos/owner/repo":
                return {"default_branch": "main"}
            if path.endswith("/git/ref/heads/main"):
                return {"object": {"sha": "base-sha"}}
            if path.endswith("/git/commits/base-sha"):
                return {"tree": {"sha": "tree-sha"}}
            if path.endswith("/git/trees/tree-sha"):
                return {
                    "tree": [
                        {"path": "app/safe.py", "type": "blob"},
                        {"path": "app/secret.py", "type": "blob"},
                    ]
                }
            if path.endswith("/contents/app/safe.py"):
                return {
                    "encoding": "base64",
                    "content": base64.b64encode(safe_source.encode()).decode(),
                }
            if path.endswith("/contents/app/secret.py"):
                return {
                    "encoding": "base64",
                    "content": base64.b64encode(secret_source.encode()).decode(),
                }
            raise AssertionError(f"Unexpected GitHub request: {method} {path}")

        try:
            with patch.object(workspace, "_request", side_effect=fake_request):
                _, _, files = await workspace.load_context()
            self.assertEqual(set(files), {"app/safe.py"})
        finally:
            await workspace.close()

    async def test_credential_like_pr_metadata_is_rejected(self):
        workspace = self._workspace_stub()
        patch_with_secret_metadata = dict(self.patch_data)
        patch_with_secret_metadata["summary"] = 'Accidentally included API_KEY = "abcdefghijklmnop12345"'
        with (
            patch("app.coding_workspace.GitHubWorkspace", return_value=workspace),
            patch("app.delegation.create_lucas_plan", return_value={"specialists": ["frontend", "testing"]}),
            patch("app.coding_workspace._run_specialist_round", new=AsyncMock(return_value={"frontend": "React plan"})),
            patch("app.coding_workspace._chat_completion", new=AsyncMock(return_value="Test strategy")),
            patch("app.coding_workspace._generate_integrated_patch", new=AsyncMock(return_value=patch_with_secret_metadata)),
            patch("app.coding_workspace._review_integrated_patch", new=AsyncMock(return_value="PASS\\nNo blockers.")),
            self.assertRaises(HTTPException) as raised,
        ):
            await execute_lucas_coding_task(self.settings, "Build a React feature")
        self.assertEqual(raised.exception.status_code, 422)
        workspace.publish_pull_request.assert_not_awaited()

    async def test_truncated_repository_tree_fails_closed(self):
        workspace = GitHubWorkspace("token", "owner/repo")

        async def fake_request(method, path, **kwargs):
            if path == "/repos/owner/repo":
                return {"default_branch": "main"}
            if path.endswith("/git/ref/heads/main"):
                return {"object": {"sha": "base-sha"}}
            if path.endswith("/git/commits/base-sha"):
                return {"tree": {"sha": "tree-sha"}}
            if path.endswith("/git/trees/tree-sha"):
                return {"truncated": True, "tree": []}
            raise AssertionError(f"Unexpected GitHub request: {method} {path}")

        try:
            with patch.object(workspace, "_request", side_effect=fake_request), self.assertRaises(HTTPException) as raised:
                await workspace.load_context()
            self.assertEqual(raised.exception.status_code, 422)
        finally:
            await workspace.close()

    async def test_missing_github_configuration_fails_closed(self):
        self.settings.github_token = None
        with self.assertRaises(HTTPException) as raised:
            await execute_lucas_coding_task(self.settings, "Build a React feature")
        self.assertEqual(raised.exception.status_code, 503)

    async def test_publish_failure_attempts_to_delete_orphan_branch(self):
        workspace = GitHubWorkspace("token", "owner/repo")
        calls = []

        async def fake_request(method, path, **kwargs):
            calls.append((method, path))
            if method == "POST" and path.endswith("/pulls"):
                raise HTTPException(status_code=502, detail="PR creation failed")
            if method == "POST" and path.endswith("/git/blobs"):
                return {"sha": "blob-sha"}
            if method == "GET" and "/git/commits/" in path:
                return {"tree": {"sha": "tree-sha"}}
            if method == "POST" and path.endswith("/git/trees"):
                return {"sha": "tree-sha"}
            if method == "POST" and path.endswith("/git/commits"):
                return {"sha": "commit-sha"}
            return {}

        try:
            with patch.object(workspace, "_request", side_effect=fake_request), self.assertRaises(HTTPException):
                await workspace.publish_pull_request(
                        "main",
                        "base-sha",
                        [{"path": "tests/test_feature.py", "content": "def test_feature(): pass"}],
                        "Test feature",
                        "Body",
                    )
            self.assertTrue(any(method == "DELETE" and "/git/refs/heads/lucas/task-" in path for method, path in calls))
        finally:
            await workspace.close()


if __name__ == "__main__":
    unittest.main()
