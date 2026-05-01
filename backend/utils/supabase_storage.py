import asyncio

from supabase import create_client

from config import settings

BUCKET = "receipts"

_client = create_client(settings.supabase_url, settings.supabase_service_key)


async def upload_file(storage_path: str, file_bytes: bytes, content_type: str = "image/jpeg") -> str:
    """Upload bytes to Supabase Storage. Returns the storage path."""
    await asyncio.to_thread(
        _client.storage.from_(BUCKET).upload,
        storage_path,
        file_bytes,
        {"content-type": content_type, "upsert": "false"},
    )
    return storage_path


async def move_file(from_path: str, to_path: str) -> str:
    """Move a file within the bucket. Returns the new path."""
    await asyncio.to_thread(
        _client.storage.from_(BUCKET).move,
        from_path,
        to_path,
    )
    return to_path


async def get_signed_url(storage_path: str, expires_in: int = 3600) -> str:
    """Return a signed URL expiring in 1 hour by default."""
    result = await asyncio.to_thread(
        _client.storage.from_(BUCKET).create_signed_url,
        storage_path,
        expires_in,
    )
    return result["signedURL"]


async def delete_file(storage_path: str) -> None:
    """Permanently delete a file from Supabase Storage."""
    await asyncio.to_thread(
        _client.storage.from_(BUCKET).remove,
        [storage_path],
    )
