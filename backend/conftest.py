"""Root conftest: patch supabase.create_client before any module-level singleton is created."""
from unittest.mock import MagicMock, patch

# Patch create_client for the entire test session so module-level singletons
# in dependencies.py and routers/auth.py don't hit the real Supabase validation.
_mock_supabase = MagicMock()
_patcher = patch("supabase.create_client", return_value=_mock_supabase)
_patcher.start()
