"""
Cloudflare R2 storage service for file uploads.

Per contracts/r2-storage.md specification.
Uses boto3 for S3-compatible storage operations.
"""

import boto3
from botocore.exceptions import ClientError
from datetime import datetime, UTC
from typing import BinaryIO, Optional
import mimetypes
import os


class R2StorageService:
    """
    Service for uploading files to Cloudflare R2 storage.
    
    Provides S3-compatible file operations using boto3 client.
    """
    
    def __init__(
        self,
        endpoint_url: str,
        access_key_id: str,
        secret_access_key: str,
        bucket_name: str,
        bucket_id: str,
    ):
        """
        Initialize R2 storage client.
        
        Args:
            endpoint_url: R2 endpoint URL (e.g., "https://account-id.r2.cloudflarestorage.com")
            access_key_id: R2 access key ID
            secret_access_key: R2 secret access key
            bucket_name: Target bucket name
            bucket_id: Public bucket ID for URL construction
        """
        self.bucket_name = bucket_name
        self.bucket_id = bucket_id
        
        # Initialize boto3 S3 client for R2
        self.client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            region_name="auto",  # R2 uses "auto" region
        )
    
    def upload_file(
        self,
        file_data: BinaryIO,
        file_name: str,
        session_folder: str,
        content_type: Optional[str] = None,
    ) -> tuple[bool, Optional[str], Optional[str]]:
        """
        Upload a file to R2 storage.
        
        Args:
            file_data: Binary file data (file-like object)
            file_name: Original filename
            session_folder: Folder path in bucket (e.g., "session_id/timestamp")
            content_type: MIME type (auto-detected if not provided)
        
        Returns:
            Tuple of (success, r2_key, error_message)
            - success: True if upload succeeded, False otherwise
            - r2_key: Full path in R2 bucket (e.g., "session_id/timestamp_file.jpg")
            - error_message: None if success, error description if failed
        
        Example:
            >>> service = R2StorageService(...)
            >>> with open("photo.jpg", "rb") as f:
            >>>     success, key, error = service.upload_file(f, "photo.jpg", "session123/20231201")
        """
        # Generate timestamp for uniqueness
        timestamp = datetime.now(UTC).strftime('%Y%m%d_%H%M%S_%f')
        
        # Construct R2 key (path in bucket)
        # Format: session_folder/timestamp_filename
        r2_key = f"{session_folder}/{timestamp}_{file_name}"
        
        # Auto-detect content type if not provided
        if content_type is None:
            content_type, _ = mimetypes.guess_type(file_name)
            if content_type is None:
                content_type = "application/octet-stream"
        
        try:
            # Upload file to R2
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=r2_key,
                Body=file_data,
                ContentType=content_type,
            )
            return True, r2_key, None
        
        except ClientError as e:
            error_message = f"Upload failed: {str(e)}"
            return False, None, error_message
        
        except Exception as e:
            error_message = f"Unexpected error during upload: {str(e)}"
            return False, None, error_message
    
    def get_public_url(self, r2_key: str) -> str:
        """
        Generate public URL for an uploaded file.
        
        Args:
            r2_key: Path in R2 bucket (e.g., "session_id/timestamp_file.jpg")
        
        Returns:
            Public URL to access the file
        
        Format: https://pub-{bucket_id}.r2.dev/{r2_key}
        
        Note: Bucket must be configured with public access for URLs to work.
        """
        return f"https://pub-{self.bucket_id}.r2.dev/{r2_key}"
    
    def validate_file_upload(
        self,
        file_size_bytes: int,
        file_name: str,
        allowed_types: list[str],
        max_file_size_mb: int,
    ) -> tuple[bool, Optional[str]]:
        """
        Validate file before upload.
        
        Args:
            file_size_bytes: Size of file in bytes
            file_name: Original filename
            allowed_types: List of allowed MIME types (e.g., ["image/jpeg", "image/png"])
            max_file_size_mb: Maximum file size in MB
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check file size
        max_bytes = max_file_size_mb * 1024 * 1024
        if file_size_bytes > max_bytes:
            return False, f"File '{file_name}' exceeds {max_file_size_mb}MB limit."
        
        # Check MIME type
        mime_type, _ = mimetypes.guess_type(file_name)
        if mime_type is None:
            return False, f"Could not determine file type for '{file_name}'."
        
        if mime_type not in allowed_types:
            return False, f"File type '{mime_type}' not allowed. Allowed types: {', '.join(allowed_types)}"
        
        return True, None
    
    def batch_upload_files(
        self,
        files: list[tuple[BinaryIO, str]],
        session_folder: str,
        validation_rules: dict,
    ) -> tuple[list[dict], list[str]]:
        """
        Upload multiple files with validation.
        
        Args:
            files: List of (file_data, file_name) tuples
            session_folder: Folder path in bucket
            validation_rules: Dict with keys:
                - allowed_types: list[str]
                - max_file_size_mb: int
                - max_total_size_mb: int
                - min_files: int
                - max_files: int
        
        Returns:
            Tuple of (uploaded_files, errors)
            - uploaded_files: List of dicts with keys: r2_key, r2_url, file_name, file_size_bytes, mime_type
            - errors: List of error message strings
        
        Example:
            >>> service = R2StorageService(...)
            >>> files = [(f1, "photo1.jpg"), (f2, "photo2.png")]
            >>> rules = {"allowed_types": ["image/jpeg", "image/png"], "max_file_size_mb": 20, ...}
            >>> uploaded, errors = service.batch_upload_files(files, "session123/20231201", rules)
        """
        errors = []
        uploaded_files = []
        
        # Validate file count
        min_files = validation_rules.get("min_files", 1)
        max_files = validation_rules.get("max_files", float("inf"))
        
        if len(files) < min_files:
            errors.append(f"Please upload at least {min_files} file(s). Currently: {len(files)} file(s).")
            return uploaded_files, errors
        
        if len(files) > max_files:
            errors.append(f"Please upload at most {max_files} file(s). Currently: {len(files)} file(s).")
            return uploaded_files, errors
        
        # Validate total size
        total_size_bytes = sum(
            file_data.seek(0, 2) or file_data.tell() or 0
            for file_data, _ in files
        )
        # Reset file pointers
        for file_data, _ in files:
            file_data.seek(0)
        
        max_total_bytes = validation_rules.get("max_total_size_mb", 200) * 1024 * 1024
        if total_size_bytes > max_total_bytes:
            errors.append(
                f"Total upload size exceeds {validation_rules.get('max_total_size_mb', 200)}MB limit. "
                f"Current total: {total_size_bytes / (1024 * 1024):.2f}MB"
            )
            return uploaded_files, errors
        
        # Validate and upload each file
        for file_data, file_name in files:
            # Get file size
            file_data.seek(0, 2)  # Seek to end
            file_size_bytes = file_data.tell()
            file_data.seek(0)  # Reset to beginning
            
            # Validate individual file
            is_valid, error = self.validate_file_upload(
                file_size_bytes,
                file_name,
                validation_rules.get("allowed_types", []),
                validation_rules.get("max_file_size_mb", 20),
            )
            
            if not is_valid:
                errors.append(error)
                continue
            
            # Determine MIME type
            mime_type, _ = mimetypes.guess_type(file_name)
            
            # Upload file
            success, r2_key, upload_error = self.upload_file(
                file_data, file_name, session_folder, mime_type
            )
            
            if not success:
                errors.append(upload_error)
                continue
            
            # Generate public URL
            r2_url = self.get_public_url(r2_key)
            
            # Record uploaded file
            uploaded_files.append({
                "r2_key": r2_key,
                "r2_url": r2_url,
                "file_name": file_name,
                "file_size_bytes": file_size_bytes,
                "mime_type": mime_type,
            })
        
        return uploaded_files, errors

