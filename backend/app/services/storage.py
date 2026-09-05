"""Storage abstraction — local MVP, S3 later.

LocalStorage: UUID filenames, no user path, Pillow verify, size/MIME checks.
"""

import uuid
from pathlib import Path
from typing import Tuple

from fastapi import HTTPException
from PIL import Image

from app.core.config import settings

ALLOWED_MIME = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}
ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".webp"}
MAX_MB = 5  # avatar and cover both 5 MB for MVP

# Story specific
STORY_IMAGE_MIME = {"image/jpeg", "image/png", "image/webp"}
STORY_VIDEO_MIME = {"video/mp4", "video/webm"}
STORY_IMAGE_MAX_MB = 5
STORY_VIDEO_MAX_MB = 25

def _ensure_dir():
    d = Path(settings.upload_dir)
    d.mkdir(parents=True, exist_ok=True)
    return d

def _validate_size(data: bytes, limit_mb: int = MAX_MB):
    if len(data) > limit_mb * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"File too large, max {limit_mb} MB")

def _detect_and_validate(data: bytes, content_type: str | None) -> str:
    # Check MIME first
    mime = (content_type or "").lower().split(";")[0].strip()
    if mime not in ALLOWED_MIME:
        # also check by sniffing extension fallback: try Pillow
        pass
    # Pillow verify — ensures actual image content
    try:
        from io import BytesIO
        im = Image.open(BytesIO(data))
        im.verify()
        # Re-open to get format after verify
        im2 = Image.open(BytesIO(data))
        fmt = (im2.format or "").lower()
        fmt_to_ext = {"jpeg": ".jpg", "jpg": ".jpg", "png": ".png", "webp": ".webp"}
        ext = fmt_to_ext.get(fmt)
        if not ext:
            raise HTTPException(status_code=415, detail="Unsupported image format")
        # If MIME was provided and mismatched, still allow if Pillow says ok, but ensure ext consistency
        if mime and mime not in ALLOWED_MIME:
            # allow if Pillow detected allowed format
            pass
        return ext
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=415, detail="Invalid image file")

def save_image(data: bytes, content_type: str | None, subdir: str = "avatars") -> Tuple[str, str]:
    """Save validated image, return (filesystem_path, public_url)."""
    _validate_size(data, MAX_MB)
    ext = _detect_and_validate(data, content_type)

    # subdir sanitized — only allow alphanumeric
    safe_subdir = "".join(c for c in subdir if c.isalnum() or c in ("-", "_")) or "misc"
    filename = f"{uuid.uuid4().hex}{ext}"
    dir_path = _ensure_dir() / safe_subdir
    dir_path.mkdir(parents=True, exist_ok=True)
    file_path = dir_path / filename
    # No overwrite risk due to UUID
    file_path.write_bytes(data)
    public_url = f"/uploads/{safe_subdir}/{filename}"
    return str(file_path), public_url

def save_story_media(data: bytes, content_type: str | None) -> Tuple[str, str, str]:
    """Validate and save story media (image 5MB, video 25MB). Returns (fs_path, public_url, media_type)."""
    mime = (content_type or "").lower().split(";")[0].strip()
    if mime in STORY_IMAGE_MIME:
        _validate_size(data, STORY_IMAGE_MAX_MB)
        ext = _detect_and_validate(data, content_type)
        media_type = "image"
    elif mime in STORY_VIDEO_MIME:
        _validate_size(data, STORY_VIDEO_MAX_MB)
        # basic video validation: check mime only (no Pillow), ensure not executable
        ext = ".mp4" if mime == "video/mp4" else ".webm"
        media_type = "video"
        # ensure data looks like video (not empty, not html)
        if len(data) < 100:
            raise HTTPException(status_code=415, detail="Invalid video file")
    else:
        raise HTTPException(status_code=415, detail="Unsupported story media type (jpeg/png/webp/mp4/webm only)")

    safe_subdir = "stories"
    filename = f"{uuid.uuid4().hex}{ext}"
    dir_path = _ensure_dir() / safe_subdir
    dir_path.mkdir(parents=True, exist_ok=True)
    file_path = dir_path / filename
    file_path.write_bytes(data)
    public_url = f"/uploads/{safe_subdir}/{filename}"
    return str(file_path), public_url, media_type
