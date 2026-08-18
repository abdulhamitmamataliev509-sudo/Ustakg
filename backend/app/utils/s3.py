"""Object-storage (S3-compatible) upload helper.

PHASE 4: implement helpers for uploading profile photos, master
portfolios, and message attachments to an S3-compatible bucket.
"""

# Placeholder — populated in Phase 4.
def upload_file(bucket: str, key: str, body: bytes) -> str:
    """Upload ``body`` to ``key`` and return its public URL.

    Args:
        bucket: The target S3 bucket name.
        key: The object key/path within the bucket.
        body: The raw file bytes to upload.

    Returns:
        str: The object URL.
    """
    raise NotImplementedError("S3 upload will be implemented in Phase 4.")
