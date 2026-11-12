import unittest

from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app import main


class AuthenticationTests(unittest.TestCase):
    def test_missing_server_token_fails_closed(self) -> None:
        original = main.settings.api_access_token
        try:
            main.settings.api_access_token = None
            with self.assertRaises(HTTPException) as raised:
                import asyncio
                asyncio.run(main.require_owner(None))
            self.assertEqual(raised.exception.status_code, 503)
        finally:
            main.settings.api_access_token = original

    def test_missing_or_invalid_bearer_token_is_rejected(self) -> None:
        original = main.settings.api_access_token
        try:
            main.settings.api_access_token = "test-secret-token"
            with self.assertRaises(HTTPException) as missing:
                import asyncio
                asyncio.run(main.require_owner(None))
            self.assertEqual(missing.exception.status_code, 401)

            credentials = HTTPAuthorizationCredentials(
                scheme="Bearer",
                credentials="wrong-token",
            )
            with self.assertRaises(HTTPException) as invalid:
                asyncio.run(main.require_owner(credentials))
            self.assertEqual(invalid.exception.status_code, 401)
        finally:
            main.settings.api_access_token = original

    def test_valid_bearer_token_resolves_owner_profile(self) -> None:
        original_token = main.settings.api_access_token
        original_profile = main.settings.owner_profile_id
        try:
            main.settings.api_access_token = "test-secret-token"
            main.settings.owner_profile_id = "test-owner"
            credentials = HTTPAuthorizationCredentials(
                scheme="Bearer",
                credentials="test-secret-token",
            )
            import asyncio
            self.assertEqual(asyncio.run(main.require_owner(credentials)), "test-owner")
        finally:
            main.settings.api_access_token = original_token
            main.settings.owner_profile_id = original_profile


if __name__ == "__main__":
    unittest.main()
