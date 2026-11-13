"""Guarded GitHub-backed coding workspace for Lucas.

The service creates a branch and pull request; it never writes directly to the
default branch, runs arbitrary shell commands, or merges a pull request.
"""
from __future__ import annotations

import json
import re
import uuid
from pathlib import PurePosixPath
from typing import Any

import httpx
from fastapi import HTTPException

ALLOWED_ROOTS = ("app/", "tests/")
ALLOWED_FILES = {"README.md", "requirements.txt"}
ALLOWED_SUFFIXES = {".py", ".md", ".txt"}
MAX_CONTEXT_FILES = 16
MAX_CONTEXT_CHARS = 80_000
MAX_CHANGED_FILES = 8
MAX_FILE_CHARS = 30_000


class GitHubWorkspace:
    def __init__(self, token: str, repository: str, base_branch: str = "main",
                 timeout_seconds: float = 30.0) -> None:
        self.repository = repository
        self.base_branch = base_branch
        self.client = httpx.AsyncClient(
            base_url="https://api.github.com",
            timeout=timeout_seconds,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )

    async def close(self) -> None:
        await self.client.aclose()

    async def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        response = await self.client.request(method, path, **kwargs)
        if response.is_error:
            # Do not return GitHub response bodies: they may contain sensitive metadata.
            raise HTTPException(
                status_code=502,
                detail=f"GitHub workspace request failed ({response.status_code}).",
            )
        if response.status_code == 204 or not response.content:
            return {}
        return response.json()

    async def load_context(self) -> tuple[str, str, dict[str, str]]:
        repo = await self._request("GET", f"/repos/{self.repository}")
        base = self.base_branch or repo.get("default_branch", "main")
        ref = await self._request("GET", f"/repos/{self.repository}/git/ref/heads/{base}")
        base_sha = ref["object"]["sha"]
        commit = await self._request("GET", f"/repos/{self.repository}/git/commits/{base_sha}")
        tree_sha = commit["tree"]["sha"]
        tree = await self._request(
            "GET", f"/repos/{self.repository}/git/trees/{tree_sha}", params={"recursive": "1"}
        )
        candidates = []
        for item in tree.get("tree", []):
            path = item.get("path", "")
            if item.get("type") != "blob" or not _allowed_path(path):
                continue
            if path.startswith("tests/") or path.startswith("app/") or path in ALLOWED_FILES:
                candidates.append(path)
        priority = sorted(candidates, key=lambda p: (0 if p.startswith("tests/") else 1 if p.startswith("app/") else 2, p))
        files: dict[str, str] = {}
        total = 0
        for path in priority[:MAX_CONTEXT_FILES]:
            data = await self._request("GET", f"/repos/{self.repository}/contents/{path}",
                                       params={"ref": base})
            if data.get("encoding") != "base64":
                continue
            import base64
            try:
                text = base64.b64decode(data["content"]).decode("utf-8")
            except (ValueError, UnicodeDecodeError, KeyError):
                continue
            if total + len(text) > MAX_CONTEXT_CHARS:
                continue
            files[path] = text
            total += len(text)
        return base, base_sha, files

    async def publish_pull_request(self, base: str, base_sha: str,
                                   changes: list[dict[str, str]],
                                   title: str, body: str) -> dict[str, Any]:
        branch = "lucas/task-" + uuid.uuid4().hex[:10]
        await self._request("POST", f"/repos/{self.repository}/git/refs", json={
            "ref": f"refs/heads/{branch}", "sha": base_sha,
        })
        blobs = []
        for change in changes:
            blob = await self._request("POST", f"/repos/{self.repository}/git/blobs", json={
                "content": change["content"], "encoding": "utf-8",
            })
            blobs.append({"path": change["path"], "mode": "100644",
                          "type": "blob", "sha": blob["sha"]})
        base_commit = await self._request(
            "GET", f"/repos/{self.repository}/git/commits/{base_sha}"
        )
        tree = await self._request("POST", f"/repos/{self.repository}/git/trees", json={
            "base_tree": base_commit["tree"]["sha"], "tree": blobs,
        })
        commit = await self._request("POST", f"/repos/{self.repository}/git/commits", json={
            "message": "Lucas: " + title[:60],
            "tree": tree["sha"],
            "parents": [base_sha],
        })
        await self._request("PATCH", f"/repos/{self.repository}/git/refs/heads/{branch}",
                            json={"sha": commit["sha"], "force": False})
        pr = await self._request("POST", f"/repos/{self.repository}/pulls", json={
            "title": title[:120], "body": body[:6000], "head": branch, "base": base,
            "draft": True,
        })
        return {"branch": branch, "pull_request_url": pr["html_url"],
                "pull_request_number": pr["number"], "commit_sha": commit["sha"]}


def _allowed_path(path: str) -> bool:
    if not path or "\\" in path or path.startswith("/") or any(part in {"", ".", ".."} for part in path.split("/")):
        return False
    pure = PurePosixPath(path)
    if pure.suffix not in ALLOWED_SUFFIXES:
        return False
    if path in ALLOWED_FILES:
        return True
    return any(path.startswith(root) for root in ALLOWED_ROOTS)


def _parse_patch(raw: str) -> dict[str, Any]:
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else ""
        if text.rstrip().endswith("```"):
            text = text.rstrip().rsplit("\n", 1)[0]
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=502, detail="Lucas returned an invalid coding patch.") from exc
    if not isinstance(value, dict) or not isinstance(value.get("files"), list):
        raise HTTPException(status_code=502, detail="Lucas returned an invalid coding patch.")
    changes = value["files"]
    if not 1 <= len(changes) <= MAX_CHANGED_FILES:
        raise HTTPException(status_code=422, detail="A coding task must change between 1 and 8 files.")
    clean: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in changes:
        if not isinstance(item, dict) or not isinstance(item.get("path"), str) or not isinstance(item.get("content"), str):
            raise HTTPException(status_code=502, detail="Lucas returned a malformed file change.")
        path, content = item["path"], item["content"]
        if not _allowed_path(path) or path in seen or len(content) > MAX_FILE_CHARS:
            raise HTTPException(status_code=422, detail=f"Lucas proposed a disallowed or oversized file: {path[:100]}")
        seen.add(path)
        clean.append({"path": path, "content": content})
    if not any(path.startswith("tests/") for path in seen):
        raise HTTPException(status_code=422, detail="Lucas must include an automated test change in every coding pull request.")
    return {"title": str(value.get("title") or "Lucas coding task")[:120],
            "summary": str(value.get("summary") or "Automated coding proposal.")[:2000],
            "files": clean}


async def execute_lucas_coding_task(settings: Any, task: str) -> dict[str, Any]:
    token = getattr(settings, "github_token", None)
    repository = getattr(settings, "github_repository", None)
    if not token or not repository:
        raise HTTPException(
            status_code=503,
            detail="GitHub coding workspace is not configured. Set GITHUB_TOKEN and GITHUB_REPOSITORY on the server.",
        )
    workspace = GitHubWorkspace(
        token, repository, getattr(settings, "github_base_branch", "main"),
        getattr(settings, "llm_timeout_seconds", 45.0),
    )
    try:
        base, base_sha, context = await workspace.load_context()
        if not context:
            raise HTTPException(status_code=422, detail="No eligible project source files were found.")
        prompt = {
            "role": "user",
            "content": (
                "Act as Lucas, a senior software engineer working in an existing repository. "
                "Implement the user's task using the supplied repository context. Preserve existing "
                "architecture and conventions. Return ONLY valid JSON with keys title, summary, files. "
                "files must be an array of {path, content} containing complete replacement file contents. "
                "Change only app/, tests/, README.md, or requirements.txt; never modify secrets, CI workflows, "
                "deployment files, or files outside these paths. Include or update at least one automated "
                "test under tests/. Do not claim tests ran. Keep the patch focused and compatible with Python 3.11.\n\n"
                f"USER TASK:\n{task}\n\nREPOSITORY CONTEXT:\n" +
                "\n\n".join(f"--- {path} ---\n{content}" for path, content in context.items())
            ),
        }
        async with httpx.AsyncClient(timeout=settings.llm_timeout_seconds) as llm:
            response = await llm.post(
                settings.llm_base_url.rstrip("/") + "/v1/chat/completions",
                headers={"Authorization": f"Bearer {settings.llm_api_key}"},
                json={
                    "model": settings.llm_model,
                    "temperature": 0.1,
                    "response_format": {"type": "json_object"},
                    "messages": [
                        {"role": "system", "content": "You generate careful, minimal, tested software patches. Never invent repository files or dependencies."},
                        prompt,
                    ],
                },
            )
            response.raise_for_status()
            raw = response.json()["choices"][0]["message"]["content"]
        patch = _parse_patch(raw)
        body = (
            f"## Lucas coding task\n\n{patch['summary']}\n\n"
            f"**Task:** {task}\n\n"
            "### Safety and verification\n"
            "- Changes are proposed on a dedicated branch; the default branch is untouched.\n"
            "- GitHub Actions should run the repository test workflow for this pull request.\n"
            "- No shell commands were run by the application. Review CI results before merging.\n"
        )
        published = await workspace.publish_pull_request(
            base, base_sha, patch["files"], patch["title"], body
        )
        return {
            "status": "pull_request_opened",
            "execution_started": True,
            "tests_executed_by_app": False,
            "ci_status": "pending",
            "changed_files": [item["path"] for item in patch["files"]],
            **published,
        }
    except HTTPException:
        raise
    except (httpx.HTTPError, KeyError, IndexError, ValueError) as exc:
        raise HTTPException(status_code=502, detail="Lucas could not complete the GitHub coding workflow.") from exc
    finally:
        await workspace.close()
