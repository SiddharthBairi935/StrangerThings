"""Read-only Google Drive API helpers for Mike.

The access token is supplied only through server-side configuration. No token is
returned to clients, and this first integration intentionally exposes no writes.
"""
from __future__ import annotations

import httpx
from fastapi import HTTPException

DRIVE_API = "https://www.googleapis.com/drive/v3"


def _headers(access_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}"}


async def search_drive_files(
    access_token: str,
    query: str,
    page_size: int = 20,
) -> dict[str, object]:
    """Search file names and full text using Drive's read-only list endpoint."""
    safe_query = query.replace("\\", "\\\\").replace("'", "\\'")
    params = {
        "q": f"trashed = false and fullText contains '{safe_query}'",
        "pageSize": max(1, min(page_size, 50)),
        "orderBy": "modifiedTime desc",
        "fields": "nextPageToken,files(id,name,mimeType,modifiedTime,webViewLink,size)",
    }
    async with httpx.AsyncClient(timeout=25.0) as client:
        response = await client.get(
            f"{DRIVE_API}/files", headers=_headers(access_token), params=params
        )
    if response.status_code in (401, 403):
        raise HTTPException(
            status_code=503,
            detail="Google Drive access is not authorized. Reconnect the read-only Drive account.",
        )
    response.raise_for_status()
    payload = response.json()
    return {
        "files": payload.get("files", []),
        "next_page_token": payload.get("nextPageToken"),
    }


async def read_drive_file(access_token: str, file_id: str) -> dict[str, object]:
    """Read metadata and bounded text content for supported Drive files."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        meta_response = await client.get(
            f"{DRIVE_API}/files/{file_id}",
            headers=_headers(access_token),
            params={"fields": "id,name,mimeType,modifiedTime,webViewLink,size"},
        )
        if meta_response.status_code in (401, 403):
            raise HTTPException(status_code=503, detail="Google Drive access is not authorized.")
        meta_response.raise_for_status()
        metadata = meta_response.json()
        mime_type = metadata.get("mimeType", "")
        if mime_type == "application/vnd.google-apps.document":
            response = await client.get(
                f"{DRIVE_API}/files/{file_id}/export",
                headers=_headers(access_token),
                params={"mimeType": "text/plain"},
            )
        elif mime_type.startswith("text/") or mime_type in {
            "application/json", "application/xml"
        }:
            response = await client.get(
                f"{DRIVE_API}/files/{file_id}",
                headers=_headers(access_token),
                params={"alt": "media"},
            )
        else:
            return {
                "file": metadata,
                "content": None,
                "content_available": False,
                "note": "This file type is not yet supported for text extraction.",
            }
        if response.status_code in (401, 403):
            raise HTTPException(status_code=503, detail="This file cannot be read with current Drive permissions.")
        response.raise_for_status()
        raw = response.content[:1_000_000]
        encoding = response.encoding or "utf-8"
        return {
            "file": metadata,
            "content": raw.decode(encoding, errors="replace"),
            "content_available": True,
            "truncated": len(response.content) > len(raw),
        }
